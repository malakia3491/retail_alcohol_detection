import asyncio
import os
from pathlib import Path
from onvif import ONVIFCamera

from video_control.domain.Shelving import Shelving

class Videocamera:
    def __init__(
        self,
        ip: str,
        url: str,
        port: int,
        username: str = None,
        password: str = None,
        shelving: Shelving = None
    ):
        self._ip = ip
        self._url = url
        self._shelving = shelving
        self._port = port
        self._username = username
        self._password = password
        self._client = None

    @property  
    def id(self) -> str:
        return self.url

    @property
    def ip(self) -> str:
        return self._ip

    @property
    def url(self) -> str:
        return self._url
    
    @property
    def port(self) -> int:
        return self._port
    
    @property
    def username(self) -> str:
        return self._username
    
    @property
    def password(self) -> str:
        return self._password
    
    @property
    def client(self) -> ONVIFCamera:
        if self._client is None:
            base = Path(__file__).resolve().parent.parent
            wsdl_dir = base / "deps" / "wsdl"
            wsdl_dir = str(wsdl_dir)
            self._client = ONVIFCamera(
                self._ip, self._port,
                self._username or '', self._password or '',
                wsdl_dir=wsdl_dir
            )
        return self._client
    
    @property
    def shelving(self) -> Shelving:
        return self._shelving
    
    @shelving.setter
    def shelving(self, shelving: Shelving):
        if not isinstance(shelving, Shelving):
            raise TypeError("shelving must be an instance of Shelving")
        self._shelving = shelving

    @property
    def is_mapped(self):
        return not self.shelving is None
    
    async def test_camera(self) -> tuple[bool, str]:
        try:
            await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.client.update_xaddrs()
            )
            
            info = await asyncio.get_event_loop().run_in_executor(
                None,
                self.client.devicemgmt.GetDeviceInformation
            )
            return True
        except Exception as e:
            return False


    async def test_rtsp_connection(self) -> bool:
        try:
            reader, writer = await asyncio.open_connection(
                self.ip, 
                self.port
            )
            writer.close()
            await writer.wait_closed()
            return True
        except:
            return False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "ip": self.ip,
            "url": self.url,
            "port": self.port,
            "username": self.username,
            "password": self.password,
            "shelving": self.shelving.to_dict() if self.shelving else None
        }

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Videocamera):
            return False
        return self.url == other.url
    
    def __hash__(self) -> int:
        return hash(self.url)

    def __str__(self):
        return f"Videocamera(url={self.url})"

    def __repr__(self):
        return f"Videocamera(url={self.url!r})"