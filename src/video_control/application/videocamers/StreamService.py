# video_control/application/videocamers/StreamService.py

import asyncio
import threading
import cv2
import base64
from typing import Dict, Tuple

from video_control.application.videocamers.CameraService import CameraService
from video_control.application.services.AuthService import AuthService
from video_control.application.services.ShelvingService import ShelvingService
from video_control.application.API.ApiRequester import ApiRequester
from video_control.persistance.repositories.VideocameraRepository import VideocameraRepository
from video_control.domain.Videocamera import Videocamera


class StreamService:
    def __init__(
        self,
        auth_service: AuthService,
        camera_service: CameraService,
        shelving_service: ShelvingService,
        requester: ApiRequester,
        interval: float = 1.0,
        capture_backend: int = cv2.CAP_ANY,
        jpeg_quality: int = 80
    ):
        self._auth_service   = auth_service
        self._cam_svc        = camera_service
        self._shelf_svc      = shelving_service
        self._requester      = requester

        self._interval       = interval
        self._backend        = capture_backend
        self._encode_params  = [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality]
        # URL → (VideoCapture, Videocamera)
        self._captures: Dict[str, Tuple[cv2.VideoCapture, Videocamera]] = {}

        self._stop_event = threading.Event()
        self._thread     = None

    def is_ready(self) -> bool:
        store_ready = getattr(self._auth_service, "_store", None) is not None
        cams_ready  = bool(asyncio.run(self._cam_svc.is_ready))
        shelves_ready = bool(asyncio.run(self._shelf_svc.get_shelvings()))
        return store_ready and cams_ready and shelves_ready

    def start(self) -> None:
        if not self.is_ready():
            raise RuntimeError("Нельзя запустить: конфигурация не завершена.")
        if self._thread and self._thread.is_alive():
            return

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_background, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join()
            self._thread = None

        for cap, _cam in self._captures.values():
            cap.release()
        self._captures.clear()

    def _run_background(self) -> None:
        asyncio.run(self.run_loop())

    async def on_start(self) -> None:
        for cap, _cam in self._captures.values():
            cap.release()
        self._captures.clear()

        cameras = await self._cam_svc.get_all()
        for cam in cameras:
            cap = cv2.VideoCapture(cam.url, self._backend)
            if not cap.isOpened():
                print(f"[StreamService] Не удалось открыть поток: {cam.url}")
                continue
            self._captures[cam.url] = (cap, cam)
            print(f"[StreamService] Открыт поток: {cam.url}, полка: {cam.shelving.id}")

    def _read_frame(self, cap: cv2.VideoCapture) -> bytes | None:
        ret, frame = cap.read()
        if not ret:
            return None
        ret2, buf = cv2.imencode('.jpg', frame, self._encode_params)
        if not ret2:
            return None
        return buf.tobytes()

    async def send_frames(self) -> None:
        store = getattr(self._auth_service, "_store", None)
        if not store:
            return

        coros = []
        for url, (cap, cam) in self._captures.items():
            frame_bytes = self._read_frame(cap)
            if not frame_bytes:
                continue

            coros.append(
                self._requester.upload_frame(
                    store_id=str(store.id),
                    shelving_id=str(cam.shelving.id),
                    frame_bytes=frame_bytes
                )
            )

        if not coros:
            return

        # Собираем результаты, не выбрасывая исключений
        results = await asyncio.gather(*coros, return_exceptions=True)
        for result in results:
            if isinstance(result, Exception):
                # Логируем, но не бросаем
                print(f"[StreamService] Ошибка при отправке кадра: {result}")

    async def run_loop(self) -> None:
        await self.on_start()
        try:
            while not self._stop_event.is_set():
                await self.send_frames()
                await asyncio.sleep(self._interval)
        finally:
            for cap, _cam in self._captures.values():
                cap.release()
            self._captures.clear()
