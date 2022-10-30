from numpy import *
import struct

class ChunkHeader:
    size: int = 0
    toolkit: int = 0
    version: int = 0
    ctype: int = 0


class RenderWareFile:
    h: ChunkHeader = None
    ptr = None

    def __init__(self, filename) -> None:
        self.ptr = open(filename, "rb")

    def read_header(self, typestr : str = ""):
        h = ChunkHeader()

        print(f"reading chunk header @{self.ptr.tell()}")
        h.ctype = int.from_bytes(self.ptr.read(4), 'little')
        h.size = int.from_bytes(self.ptr.read(4), 'little')
        h.toolkit = int.from_bytes(self.ptr.read(2), 'little')
        h.version = int.from_bytes(self.ptr.read(2), 'little')
        print(f"Read header {h.size} type: {typestr}")

        return h

    def read_int(self) -> int:
        return int.from_bytes(self.ptr.read(4), 'little')

    def read_float(self) -> float:
        xa = self.ptr.read(4)
        (x) = struct.unpack("f", struct.pack("4B", xa[0], xa[1], xa[2], xa[3]))
        return float(x[0])

    def read_bool(self) -> bool:
        return int.from_bytes(self.ptr.read(1), 'little') > 0

    def read_vcstring(self, length: int) -> str:
        result: str = ""
        data = self.ptr.read(length)

        for i in range(0, length):
            if result != "" and data[i] == 0x00:
                break

            result += chr(data[i])

        return result