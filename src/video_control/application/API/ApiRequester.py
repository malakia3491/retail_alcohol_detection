import aiohttp

from .PathBuilder import PathBuilder

class ApiRequester:
    def __init__(self, path_builder: PathBuilder):
        self._path_builder = path_builder

    @property
    def ready(self):
        return self._path_builder.status

    async def _request(self, method: str, url_path: str, **kwargs):
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url_path, **kwargs) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Request failed with status code {response.status}")

    async def get_shelvings(self):
        url_path = self._path_builder.get_shelvings_path()
        return (await self._request('GET', url_path))['shelvings']
            
    async def login(self, username: str, password: str):
        url_path = self._path_builder.login_path()
        data = {'username': username, 'password': password}
        return await self._request('POST', url_path, data=data)        
                
    async def me(self, token: str):
        url_path = self._path_builder.me_path()
        data = {'token': token}
        return await self._request('POST', url_path, data=data)
                
    async def upload_frame(
        self,
        store_id: str,
        shelving_id: str,
        frame_bytes: bytes
    ) -> dict:
            """
            Отправляет один JPEG-кадр на endpoint /images/{store_id}/{shelving_id}.
            Ожидаем, что контроллер принимает:
                image_file: UploadFile = File(...)
                shelving_id: UUID = Form(...)
                store_id: UUID = Form(...)
            """
            # Формируем URL: предположим, path_builder возвращает полный путь
            url = self._path_builder.post_video_camera_path(store_id, shelving_id)

            # Собираем multipart-файл
            form = aiohttp.FormData()
            # Добавляем поле image_file: имя «image_file», имя файла «frame.jpg»
            form.add_field(
                name="image_file",
                value=frame_bytes,
                filename="frame.jpg",
                content_type="image/jpeg"
            )

            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=form) as resp:
                    resp.raise_for_status()
                    return await resp.json()