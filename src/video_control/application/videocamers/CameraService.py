import traceback

from video_control.domain.Videocamera import Videocamera
from video_control.persistance.repositories.VideocameraRepository import VideocameraRepository

class CameraService:
    def __init__(self, camera_repository: VideocameraRepository):
        self._repo = camera_repository

    @property
    async def is_ready(self) -> bool:
        return (await self.cameras_loaded) and self.mappings_setted

    @property
    async def cameras_loaded(self) -> bool:
        is_loaded = True
        for camera in self._cameras:
            if not (await camera.test_camera()) or not camera.is_mapped:
                is_loaded = False
                break                     
        return not self._cameras is None and is_loaded
    
    @property
    def mappings_setted(self) -> bool:
        for camera in self._cameras:
            if not camera.is_mapped:
                return False
        return True
    
    async def on_start(self) -> 'CameraService':
        self._cameras = await self._repo.get_all()
        return self

    async def set_camera_mappings(
        self,
        cameras: list[Videocamera],
        shelvings: list[str]
    ):
        """
        Устанавливаем соответствие камеры и полки.
        `shelves` - это список названий полок.
        """
        if len(cameras) != len(shelvings):
            raise ValueError(
                "Количество камер и полок должно совпадать."
            )
        
        for cam, shelving in zip(cameras, shelvings):
            cam.shelving = shelving
        await self._repo.save()
    
    async def add_camera(
        self,
        ip: str,
        port: int,
        username: str,
        password: str
    ) -> Videocamera:
        """
        Создаём новый Videocamera, сохраняем в репозиторий.
        `other` передаём как WSDL_DIR, чтобы клиент мог создан позже.
        """
        url = f"rtsp://{ip}:{port}/h264_aac.sdp"
        cam = Videocamera(
            ip=ip,
            url=url,
            port=port,
            username=username,
            password=password,
        )
        await self._repo.add(cam)
        await self._repo.save()
        return cam

    async def get_all(self) -> list[Videocamera]:
        return await self._repo.get_all()

    async def test_camera(self, camera: Videocamera) -> tuple[bool,str]:
        """
        Используем camera.client (ONVIFCamera) для GetDeviceInformation.
        """
        try:
            if await camera.test_rtsp_connection():
                print("RTSP порт доступен")
                success = await camera.test_camera()
                if success:
                    print("Камера доступна")
                else:
                    print("Камера недоступна")
                return True, f"{success}"
            return False, ""
        except Exception as e:
            print(traceback.format_exc())
            return False, str(e)

    async def remove_camera(self, camera: Videocamera) -> None:
        await self._repo.remove(camera)
        await self._repo.save()