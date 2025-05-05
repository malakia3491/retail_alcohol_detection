import traceback
from fastapi import HTTPException, status

from Alc_Detection.Domain.Entities import *
from Alc_Detection.Application.Requests.Requests import (
    AddProductsRequest, Product as ProductModel)
from Alc_Detection.Application.Requests.Models import  ProductsResponse
from Alc_Detection.Persistance.Repositories.Repositories import *

class ProductResourcesService:
    def __init__(self,
                 product_repository: ProductRepository):
        self._product_repository = product_repository
    
    async def get_actual_product_count(
        self,
        store: Store,
        product: Product
    ) -> int:
        raise NotImplementedError()
    
    async def get_products(self) -> ProductsResponse:
        try:
            products = await self._product_repository.get_all()
            response = ProductsResponse(
                products=[ProductModel(
                    id=product.id,
                    name=product.name,
                    image_url=f"/static/products/{product.id}/{product.image.name}"
                   )
                    for product in products]
            )
            return response
        except Exception as ex:
            print(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ex.__str__())
    
    async def add_products(self, request: AddProductsRequest) -> str:
        try:
            products = [Product(name=product.name) for product in request.products]
            count_added_records = await self._product_repository.add(*products)
            return f"Succsessfully. Added {count_added_records} records."
        except Exception as ex:
            print(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ex.__str__())     