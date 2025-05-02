import torch
from fastapi import FastAPI

from Alc_Detection.API.Controllers.Controllers import *

from Alc_Detection.Application.Notification.start_up import TelegramInitializer
from Alc_Detection.Application.ImageGeneration.ProductMatrixImageGenerator import ProductMatrixImageGenerator
from Alc_Detection.Application.IncidentManagement.Interfaces.Messenger import Messenger
from Alc_Detection.Application.IncidentManagement.Services.IncidentManager import IncidentManager
from Alc_Detection.Application.Mappers.Mappers import *
from Alc_Detection.Application.Mappers.CalibrationMapper import CalibrationMapper
from Alc_Detection.Application.Mappers.ProductMatrixMapper import ProductMatrixMapper
from Alc_Detection.Application.StoreInformation.Services.StoreService import StoreService
from Alc_Detection.Application.VideoAnalytics.Dependencies import *

from Alc_Detection.Application.VideoAnalytics.ImageProcessing.ImageSaver import ImageSaver
from Alc_Detection.Persistance.Cache.InMemoryCache import InMemoryCache
from Alc_Detection.Persistance.Configs.ConfigReader import IniConfigReader
from Alc_Detection.Persistance.Repositories.EmbeddingModelRepository import EmbeddingModelRepository
from Alc_Detection.Persistance.Repositories.Repositories import *
from Alc_Detection.Persistance.db_ini import DbInitializer

class ModulesInitializer:
    def __init__(self,
                 app: FastAPI):
        self.app = app
        self.config_reader = IniConfigReader(
                    path_to_config="C:\\Users\\pyatk\\Desktop\\Nikita\\source\\retail_alcohol_detection\\src\\Alc_Detection\\Persistance\\Configs\\config.ini"
        )
        self.tg_starter = TelegramInitializer(self.config_reader)
        self.db_starter = DbInitializer(self.config_reader)
        self.controllers_dict = {}
    
    def _include_routers(self, controllers_dict):
        for key in controllers_dict:
            controller, meta_data = controllers_dict[key]
            self.app.include_router(controller.router, prefix=meta_data[0], tags=[meta_data[1]])
    
    async def initialize(self):
        await self.db_starter.initialize()        
        product_mapper, \
        person_mapper, \
        shelving_mapper, \
        product_matrix_mapper, \
        planogram_mapper, \
        planogram_order_mapper, \
        store_mapper = self._initialize_mappers()
                 
        store_repository, \
        shelving_repository, \
        planogram_order_repository, \
        person_repository, \
        product_repository, \
        embedding_model_repository = await self._initialize_db(
                                    product_mapper=product_mapper, 
                                    person_mapper=person_mapper, 
                                    shelving_mapper=shelving_mapper,  
                                    planogram_mapper=planogram_mapper, 
                                    planogram_order_mapper=planogram_order_mapper,
                                    store_mapper=store_mapper)
        
        image_saver = ImageSaver(product_crop_save_dir=self.config_reader.get_save_dir_path("product_crops"),
                                 realogram_save_dir=self.config_reader.get_save_dir_path("realogram_snapshots"))
        image_generator = ProductMatrixImageGenerator(image_saver=image_saver)
                
        await self._initialize_notification_module()
        
        incident_manager = self._initialize_incident_management(
            image_generator=image_generator,
            store_service=store_service,
            store_rep=store_repository,
            messanger=None)
        
        store_service = self._initialize_store_module(
            store_repository=store_repository,
            shelving_repository=shelving_repository,
            person_repository=person_repository,
            planogram_order_repository=planogram_order_repository,
            product_repository=product_repository,
            product_matrix_mapper=product_matrix_mapper,
            planogram_order_mapper=planogram_order_mapper)
        
        await self._initialize_videoanalytics(
            image_saver=image_saver,
            store_service=store_service,
            incident_management_service=incident_manager,
            product_repository=product_repository,
            embedding_model_repository=embedding_model_repository)
        
        self._include_routers(self.controllers_dict)
    
    async def _initialize_db(self,
                             product_mapper, 
                             person_mapper, 
                             shelving_mapper,  
                             planogram_mapper, 
                             planogram_order_mapper,
                             store_mapper):
        session_factory = await self.db_starter.initialize()
      
        embedding_model_repository = EmbeddingModelRepository(session_factory=session_factory,
                                                              cache=InMemoryCache(),)
        store_repository =  StoreRepository(session_factory=session_factory,
                                            cache=InMemoryCache(),
                                            store_mapper=store_mapper)
        shelving_repository =  ShelvingRepository(session_factory=session_factory,
                                                  cache=InMemoryCache(),
                                                  shelving_mapper=shelving_mapper)
        planogram_order_repository =  PlanogramOrderRepository(session_factory=session_factory,
                                                               cache=InMemoryCache(),
                                                               planogram_order_mapper=planogram_order_mapper,
                                                               planogram_mapper=planogram_mapper)
        person_repository =  PersonRepository(session_factory=session_factory,
                                              cache=InMemoryCache(),
                                              person_mapper=person_mapper)
        
        product_repository= ProductRepository(session_factory=session_factory,
                                              embedding_model_version="standard",
                                              cache=InMemoryCache(),
                                              product_mapper=product_mapper)
        
        reps = [product_repository, store_repository, shelving_repository, planogram_order_repository, person_repository, embedding_model_repository]
        for rep in reps: await rep.on_start()        
        return store_repository, shelving_repository, planogram_order_repository, person_repository, product_repository, embedding_model_repository
    
    async def _initialize_videoanalytics(self,
                                         image_saver: ImageSaver,
                                         incident_management_service: IncidentManager,
                                         store_service: StoreService,
                                         product_repository: ProductRepository,
                                         embedding_model_repository: EmbeddingModelRepository):
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        modelLoader = ModelLoader(device=device,
                                  config_reader=self.config_reader)
        imagePreprocessor = ImagePreprocessor(device=device,
                                              output_size=(640, 640)).build()
        cropPreprocessor = ImagePreprocessor(device=device,
                                             output_size=(128, 128))
        person_detector_service = PersonDetectionService(detection_model=modelLoader.get_person_detector("standard"))
        bottles_detector_service = BottleModelDetectionService(detection_model=modelLoader.get_bottle_detector("standard"))
        bottle_classifier_service = BottleClassifierService(preprocessor=cropPreprocessor,
                                                            classifier=modelLoader.get_bottle_classifier(),
                                                            siamese_model=modelLoader.bottle_embedding_model("standard"),
                                                            cache=InMemoryCache(),
                                                            device=device)      
        shelfService = ShelfService(preprocessor=imagePreprocessor,
                                    person_detector=person_detector_service,
                                    bottle_detector=bottles_detector_service,
                                    bottle_classifier=bottle_classifier_service,
                                    image_saver=image_saver,
                                    product_repository=product_repository,
                                    embedding_network_repository=embedding_model_repository,
                                    incident_management_service=incident_management_service,
                                    store_service=store_service)
        await shelfService.on_start()
        
        controller = ShelfController(shelfService=shelfService)         
        self.controllers_dict["shelf_controller"] = (controller, ("/video_control", "video control"))
    
    def _initialize_incident_management(
        self,
        store_service: StoreService,
        store_rep: StoreRepository,
        messanger: Messenger=None
    ):
        incident_manager = IncidentManager(store_service=store_service,
                                           store_repository=store_rep,
                                           messanger=messanger)
        return incident_manager
    
    async def _initialize_notification_module(self):
        messanger = await self.tg_starter.initialize()
        controller = TelegramBotContoller(
            api_token=messanger._api_token,
            dispetcher=messanger.dispatcher
        )
        self.controllers_dict["telegram_bot_controller"] = (controller, ("/webhook", "telegram bot"))
    
    def _initialize_store_module(self,
                                 store_repository: StoreRepository,
                                 shelving_repository: ShelvingRepository,
                                 person_repository: PersonRepository,
                                 planogram_order_repository: PlanogramOrderRepository,
                                 product_repository: ProductRepository,
                                 product_matrix_mapper: ProductMatrixMapper,
                                 planogram_order_mapper: PlanogramOrderMapper,
                                 image_generator: ProductMatrixImageGenerator):   
        store_service = StoreService(store_repository=store_repository,
                                     shelving_repository=shelving_repository,
                                     person_repository=person_repository,
                                     planogram_order_repository=planogram_order_repository,
                                     product_repository=product_repository,
                                     planogram_order_mapper=planogram_order_mapper,
                                     product_matrix_mapper=product_matrix_mapper,
                                     image_generator=image_generator)
        controller = StoreController(storeService=store_service)
        self.controllers_dict["store_controller"] = (controller, ("/retail", "retail"))
        return store_service
        
    def _initialize_mappers(self):
        product_mapper = ProductMapper()
        product_matrix_mapper = ProductMatrixMapper(product_mapper=product_mapper)
        shelving_mapper = ShelvingMapper()
        person_mapper = PersonMapper()
        planogram_mapper = PlanogramMapper(person_mapper=person_mapper,
                                           shelving_mapper=shelving_mapper,
                                           product_mapper=product_mapper,
                                           product_matrix_mapper=product_matrix_mapper)
        calibration_mapper = CalibrationMapper(person_mapper=person_mapper,
                                               planogram_mapper=planogram_mapper)
        store_mapper = StoreMapper(person_mapper=person_mapper,
                                   calibration_mapper=calibration_mapper)
        planogram_order_mapper = PlanogramOrderMapper(person_mapper=person_mapper,
                                                      shelving_mapper=shelving_mapper,
                                                      planogram_mapper=planogram_mapper)
        return product_mapper, person_mapper, shelving_mapper, product_matrix_mapper, planogram_mapper, planogram_order_mapper, store_mapper         