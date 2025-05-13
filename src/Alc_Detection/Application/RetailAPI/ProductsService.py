import aiohttp

from Alc_Detection.Application.RetailAPI.PathBuilder import PathBuilder

class ProductsService:
    def __init__(
        self,
        path_bulder: PathBuilder
    ):
        self._path_bulder = path_bulder
    
    async def get_actual_product_count(
        self,
        store_id: str,
        product_id: str
    ) -> int:
        url_path = self._path_bulder.get_actual_product_count(store_id="000000001", product_id=product_id)
        async with aiohttp.ClientSession() as session:
            async with session.get(url_path) as response:
                print(url_path)
                count = (await response.json())["product_count"]
                return count