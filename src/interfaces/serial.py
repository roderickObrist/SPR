import atexit
import os
import termios
import tty

from .cli import Cli, _Exit


class SerialCli(Cli):
    """Exchange UTF-8 lines over a POSIX serial device at 9600 baud, 8N1."""

    def __init__(self, device: str = "/dev/tty.usbserial"):
        self.connection = os.fdopen(os.open(device, os.O_RDWR | os.O_NOCTTY), "r+b", buffering=0)
        tty.setraw(self.connection.fileno())
        settings = termios.tcgetattr(self.connection.fileno())
        settings[2] &= ~(termios.PARENB | termios.CSTOPB)
        settings[2] |= termios.CLOCAL | termios.CREAD
        settings[4] = settings[5] = termios.B9600
        termios.tcsetattr(self.connection.fileno(), termios.TCSANOW, settings)
        atexit.register(self.connection.close)

    def _read(self, prompt: str) -> str:
        self._write(prompt)
        line = self.connection.readline()
        if not line:
            raise _Exit
        return line.decode("utf-8").strip()

    def _write(self, text: str) -> None:
        remaining = memoryview((text + "\n").encode("utf-8"))
        while remaining:
            remaining = remaining[self.connection.write(remaining):]
