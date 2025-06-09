import asyncio
import socket
from typing import List, Optional
from onvif import ONVIFCamera  

from video_control.application.videocamers.ONVIFProbeProtocol import ONVIFProbeProtocol

class CameraDiscovery:
    """
    Обнаружение IP-камер в локальной сети через ONVIF WS-Discovery
    и проверка на RTSP-стрим по умолчанию.
    """
    def __init__(self, timeout: float = 3.0):
        self.timeout = timeout
        self.rtsp_ports = [554, 8554]  # Добавляем проверку порта 8554
        self.rtsp_paths = [
            "/", 
            "/h264_opus.sdp",
            "/h264_aac.sdp",
            "/h264_ulaw.sdp",
            "/h264.sdp"
        ]

    async def discover_onvif(self) -> List[str]:
        """
        WS-Discovery ONVIF: возвращает список IP адресов камер.
        """
        # Используем асинхронный UDP-сокет для multicast WS-Discovery
        loop = asyncio.get_event_loop()
        transport, _ = await loop.create_datagram_endpoint(
            lambda: ONVIFProbeProtocol(),
            local_addr=('0.0.0.0', 0),
            family=socket.AF_INET
        )
        await asyncio.sleep(self.timeout)
        transport.close()
        return ONVIFProbeProtocol.found_ips()

    async def probe_rtsp(self, ip: str, port: int) -> Optional[str]:
        """Проверяет RTSP на разных путях"""
        for path in self.rtsp_paths:
            url = f"rtsp://{ip}:{port}{path}"
            writer = None  # Инициализируем переменную
            try:
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(ip, port),
                    timeout=1.5
                )
                req = f"OPTIONS {url} RTSP/1.0\r\nCSeq: 1\r\n\r\n"
                writer.write(req.encode())
                await writer.drain()
                data = await reader.read(256)
                
                if b"RTSP/1.0 200 OK" in data:
                    return url
            except (Exception, asyncio.TimeoutError):
                continue
            finally:
                if writer and not writer.is_closing(): 
                    writer.close()
        return None

    def _generate_local_ips(self) -> List[str]:
        """Генерирует IP-адреса локальной подсети"""
        try:
            host_ip = socket.gethostbyname(socket.gethostname())
            base = ".".join(host_ip.split(".")[:-1]) + "."
            return [f"{base}{i}" for i in range(1, 255)]
        except:
            return []

    async def get_camera_urls(self) -> List[str]:
        """Новая стратегия поиска:"""
        urls = []
        
        onvif_ips = await self.discover_onvif()
        for ip in onvif_ips:
            for port in self.rtsp_ports:
                if url := await self.probe_rtsp(ip, port):
                    urls.append(url)
        
        # if not urls:
        #     local_ips = self._generate_local_ips()
        #     for ip in local_ips:
        #         for port in self.rtsp_ports:
        #             if url := await self.probe_rtsp(ip, port):
        #                 urls.append(url)
        
        return urls