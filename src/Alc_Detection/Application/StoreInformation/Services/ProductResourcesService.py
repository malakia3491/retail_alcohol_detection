import traceback
from fastapi import HTTPException, status

from Alc_Detection.Application.RetailAPI.ProductsService import ProductsService
from Alc_Detection.Domain.Entities import *
from Alc_Detection.Application.Requests.Requests import (
    AddProductsRequest, Product as ProductModel)
from Alc_Detection.Application.Requests.Models import  ProductsResponse
from Alc_Detection.Persistance.Repositories.Repositories import *

class ProductResourcesService:
    def __init__(self,
                 product_repository: ProductRepository,
                 products_api_service: ProductsService
    ):
        self._product_repository = product_repository
        self._products_api_service = products_api_service
    
    async def get_actual_product_count(
        self,
        store: Store,
        product: Product
    ) -> int:
        try:
            print("СПРАШИВАЕМ КОЛИЧЕСТВО")
            count = await self._products_api_service.get_actual_product_count(
                store_id=store.retail_id,
                product_id=product.retail_id
            )
            print(count)
            return count
        except Exception as ex:
            print(traceback.format_exc())
            return 10000
    
    async def get_products(self) -> ProductsResponse:
        try:
            products = await self._product_repository.get_all()
            response = ProductsResponse(
                products=[ProductModel(
                    id=product.id,
                    name=product.name,
                    image_url= f"/static/products/{product.id}/{product.image.name}" if product.image else None 
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