import asyncio
import socket
import xml.etree.ElementTree as ET
from typing import Set

class ONVIFProbeProtocol(asyncio.DatagramProtocol):
    _found_ips: Set[str] = set()

    def connection_made(self, transport):
        self.transport = transport
        message = self._build_probe_message()
        multicast_addr = ("239.255.255.250", 3702)
        self.transport.sendto(message.encode(), multicast_addr)

    def datagram_received(self, data, addr):
        ip = addr[0]
        if ip not in self._found_ips:
            if b"onvif" in data.lower():
                self._found_ips.add(ip)

    @staticmethod
    def found_ips():
        return list(ONVIFProbeProtocol._found_ips)

    def error_received(self, exc):
        print(f"Error received during ONVIF probe: {exc}")

    @staticmethod
    def _build_probe_message():
        # UUID нужен уникальный, но можно захардкодить для тестов
        uuid = "uuid:00000000-0000-0000-0000-000000000000"
        return f"""<?xml version="1.0" encoding="utf-8"?>
<e:Envelope xmlns:e="http://www.w3.org/2003/05/soap-envelope"
            xmlns:w="http://schemas.xmlsoap.org/ws/2004/08/addressing"
            xmlns:d="http://schemas.xmlsoap.org/ws/2005/04/discovery"
            xmlns:dn="http://www.onvif.org/ver10/network/wsdl">
  <e:Header>
    <w:MessageID>{uuid}</w:MessageID>
    <w:To>urn:schemas-xmlsoap-org:ws:2005:04:discovery</w:To>
    <w:Action>http://schemas.xmlsoap.org/ws/2005/04/discovery/Probe</w:Action>
  </e:Header>
  <e:Body>
    <d:Probe>
      <d:Types>dn:NetworkVideoTransmitter</d:Types>
    </d:Probe>
  </e:Body>
</e:Envelope>"""
