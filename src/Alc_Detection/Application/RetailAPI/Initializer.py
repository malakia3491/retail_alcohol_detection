from Alc_Detection.Application.RetailAPI.PathBuilder import PathBuilder
from Alc_Detection.Application.RetailAPI.ProductsService import ProductsService
from Alc_Detection.Persistance.Configs.ConfigReader import IniConfigReader

class Initializer:
    def __init__(
        self,
        config_reader: IniConfigReader
    ):
        self._config_reader = config_reader
        
    def initialize(self):
        path_builder = PathBuilder(base_url=self._config_reader.get_retail_api_base_url())
        products_service = ProductsService(
            path_bulder=path_builder
        )
        return products_service