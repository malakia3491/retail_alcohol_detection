from sqlalchemy import UUID
from Alc_Detection.Application.Mappers.ProductMapper import ProductMapper
from Alc_Detection.Application.Requests.Requests import ProductMatrix as ProductMatrixResponseModel
from Alc_Detection.Application.Requests.Models import Product as ProductResponseModel
from Alc_Detection.Application.Requests.Models import ProductBox as ProductBoxResponseModel
from Alc_Detection.Application.Requests.Models import PlanogramProduct as PlanogramProductResponseModel
from Alc_Detection.Application.Requests.Models import Shelf as ShelfResponseModel
from Alc_Detection.Domain.Shelf.ProductMatrix.ProductMatrix import ProductMatrix
from Alc_Detection.Domain.Shelf.ProductMatrix.ProductBox import ProductBox
from Alc_Detection.Domain.Shelf.ProductMatrix.Point import Point
from Alc_Detection.Domain.Shelf.ProductMatrix.Shelf import Shelf
from Alc_Detection.Domain.Store.Product import Product 

class ProductMatrixMapper:
    def __init__(self,
                 product_mapper: ProductMapper):
        self._product_mapper = product_mapper
    
    def map_response_to_domain_model(self,
                                     request_model: ProductMatrixResponseModel,
                                     products: list[Product]
    ) -> tuple[ProductMatrix, dict[Product, int]]:
        product_count = {}
        id_to_product = {}
        for product, planogram_product in zip(products, request_model.products):
            product_count[product] = planogram_product.count
            id_to_product[planogram_product.product_id] = product
            
        shelfs: dict[int, Shelf] = {}
        for planogram_shelf in request_model.shelfs:
            boxes = []
            for planogram_box in planogram_shelf.product_boxes:
                box = ProductBox(product=id_to_product[planogram_box.product_id])
                box.load_positions(Point(planogram_shelf.position, planogram_box.pos_x))
                boxes.append(box)
            shelfs[planogram_shelf.position] = Shelf(boxes=boxes)
        product_matrix = ProductMatrix(shelves=shelfs)
        return product_matrix, product_count
    
    def map_to_response_model(self,
                              domain_model: ProductMatrix,
                              product_count: dict[Product, int]
    ) -> ProductMatrixResponseModel:
        if domain_model is None: return None
        if not isinstance(domain_model, ProductMatrix):
            raise ValueError(domain_model)
        planogram_products = {}
        for product, count in product_count.items():
            planogram_products[product.id] = PlanogramProductResponseModel(id=None,
                                                                           product_id=product.id,
                                                                           product=self._product_mapper.map_to_response_model(product),
                                                                           count=count) 
        shelves = [ShelfResponseModel(position=index,
                                      product_boxes=[
                                          ProductBoxResponseModel(
                                                    id=None,
                                                    product_id=box.product.id,
                                                    planogram_product=planogram_products[box.product.id],
                                                    pos_x=box.position.x,
                                                    is_empty=box.is_empty) 
                                                    for box in shelf.boxes]) 
                   for index, (_, shelf) in enumerate(domain_model)]
        product_matrix = ProductMatrixResponseModel(products=planogram_products.values(),
                                                    shelfs=shelves)        
        return product_matrix