import atexit
import socket

from .cli import Cli


class UdpCli(Cli):
    """One localhost player: send an initial datagram, then UTF-8 replies to prompts."""

    def __init__(self, port: int = 9999):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        atexit.register(self.socket.close)
        self.socket.bind(("127.0.0.1", port))
        _, self.peer = self.socket.recvfrom(4096)

    def _read(self, prompt: str) -> str:
        self._write(prompt)
        while True:
            data, peer = self.socket.recvfrom(4096)
            if peer == self.peer:
                return data.decode("utf-8")

    def _write(self, text: str) -> None:
        self.socket.sendto((text + "\n").encode("utf-8"), self.peer)
