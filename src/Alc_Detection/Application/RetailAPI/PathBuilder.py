class PathBuilder:
    def __init__(
        self,
        base_url: str
    ):
        self._base_url = base_url
    
    def get_actual_product_count(
        self,
        store_id: str,
        product_id: str
    ) -> str:
        return f"{self._base_url}/products/{store_id}/{product_id}/count/"  