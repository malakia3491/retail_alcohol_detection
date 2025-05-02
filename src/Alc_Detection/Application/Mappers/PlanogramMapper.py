from sqlalchemy import UUID
from Alc_Detection.Application.Mappers.ProductMatrixMapper import ProductMatrixMapper
from Alc_Detection.Domain.Shelf.Planogram import Planogram
from Alc_Detection.Domain.Shelf.ProductMatrix.Point import Point
from Alc_Detection.Domain.Shelf.ProductMatrix.ProductBox import ProductBox
from Alc_Detection.Domain.Shelf.ProductMatrix.ProductMatrix import ProductMatrix
from Alc_Detection.Domain.Store.Product import Product
from Alc_Detection.Domain.Store.Shelving import Shelving
from Alc_Detection.Application.Mappers.ProductMapper import ProductMapper
from Alc_Detection.Application.Mappers.ShelvingMapper import ShelvingMapper
from Alc_Detection.Application.Mappers.PersonMapper import PersonMapper
from Alc_Detection.Persistance.Models.Models import Planogram as PlanogramModel
from Alc_Detection.Persistance.Models.Models import ProductBox as ProductBoxModel
from Alc_Detection.Persistance.Models.Models import PlanogramProduct as PlanogramProductModel

from Alc_Detection.Application.Requests.Models import Planogram as PlanogramResponseModel

class PlanogramMapper:
    def __init__(self,
                 person_mapper: PersonMapper,
                 shelving_mapper: ShelvingMapper,
                 product_mapper: ProductMapper,
                 product_matrix_mapper: ProductMatrixMapper):
        self._person_mapper = person_mapper
        self._shelving_mapper = shelving_mapper
        self._product_mapper = product_mapper
        self._product_matrix_mapper = product_matrix_mapper
    
    def map_to_domain_model(self, db_model: PlanogramModel) -> Planogram:
        if db_model is None: return None
        if not isinstance(db_model, PlanogramModel):
            raise ValueError(db_model)
        
        shelving = self._shelving_mapper.map_to_domain_model(db_model.shelving_planogram_order.shelving)
        author = self._person_mapper.map_to_domain_model(db_model.author)
        approver = self._person_mapper.map_to_domain_model(db_model.approver)
        product_matrix = ProductMatrix(shelving_count=shelving.shelves_count)
        product_count: dict[Product, int] = {}
        for planogram_product in db_model.products:
            product = self._product_mapper.map_to_domain_model(planogram_product.product)
            product_count[product] = planogram_product.count
            boxes = [ProductBox(product=product)
                    .load_positions(Point(int(box.matrix_cords[0]),
                                          int(box.matrix_cords[1])))
                                    for box in planogram_product.boxes]
            product_matrix.add_products(boxes)            
                        
        return Planogram(id=db_model.id,
                         shelving=shelving,
                         product_matrix=product_matrix,
                         product_count=product_count,
                         author=author,
                         create_date=db_model.upload_date,
                         approver=approver,
                         approval_date=db_model.approval_date)
            
    def map_to_db_model(self,
                        domain_model: Planogram,
                        assignment_id: UUID
    ) -> PlanogramModel:
        if domain_model is None: return None
        if not isinstance(domain_model, Planogram):
            raise ValueError(domain_model)
        
        boxes: dict[int, list[ProductBoxModel]] = {}
        for product_id in domain_model.product_count: boxes[product_id] = []
        for _, shelf in domain_model.product_matrix:
            for box in shelf.boxes:
                boxes[box.product.id].append(ProductBoxModel(matrix_cords=(int(box.position.x), int(box.position.y))))
                                                        
        planogram_products = []
        for product_id in domain_model.product_count:
            planogram_product = PlanogramProductModel(product_id = product_id,
                                                      count = int(domain_model.product_count[product_id]),
                                                      boxes = boxes[product_id])            
            planogram_products.append(planogram_product)
                       
        planogram = PlanogramModel(
            shelving_planogram_order_id = assignment_id,
            author_id = domain_model.author.id,
            upload_date = domain_model.create_date,
            products = planogram_products
        )
        return planogram
    
    def map_to_response_model(self,
                              domain_model: Planogram
    ) -> PlanogramResponseModel:
        if domain_model is None: return None
        if not isinstance(domain_model, Planogram):
            raise ValueError(domain_model)
        
        author = self._person_mapper.map_to_response_model(domain_model.author)
        approver = self._person_mapper.map_to_response_model(domain_model.approver)
        shelving = self._shelving_mapper.map_to_response_model(domain_model.shelving)
        product_matrix = self._product_matrix_mapper.map_to_response_model(domain_model=domain_model.product_matrix,
                                                                           product_count=domain_model.product_count)
        planogram = PlanogramResponseModel( id=domain_model.id,
                                            author=author,
                                            shelving=shelving,
                                            create_date=domain_model.create_date,
                                            product_matrix=product_matrix,
                                            approver=approver,
                                            approval_date=domain_model.approval_date,)        
        return planogram