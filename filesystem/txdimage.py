from numpy import *
from rwfile import RenderWareFile
from ntypes import Vector2, Vector2I

import rwfiletypes as rwt
import rwdefinitions as rwd
import pyray as rl


class Scan:
    data = None
    size: Vector2 = None


class TXEntry:
    name: str
    mask: str
    scans: list(Scan)
    flags: uint32
    filtering: int
    addressU: int
    addressV: int
    compression: int


class RWTextureFile(RenderWareFile):
    textures = []

    def read_data(self):
        self.h = self.read_header()
        if self.h.ctype != rwt.TexDictionary:
            print("Invalid file type.")
            return

        texNum: uint16 = uint16(int.from_bytes(self.ptr.read(2)))
        self.ptr.seek(self.ptr.tell() + 2)

        for i in range(texNum):
            h = self.read_header()
            if h.ctype != rwt.TextureNative:
                print("invalid chunk format")
                return

            h = self.read_header()
            if h.ctype != rwt.Struct:
                print("invalid struct format")
                return

            e: TXEntry = self.read_texture()
            self.textures.append((e.name, e))
            h = self.read_header()
            self.ptr.seek(self.ptr.tell() + h.size)

        self.ptr.close()

    def read_texture(self) -> TXEntry:
        tx: TXEntry = TXEntry()

        platform = uint32(int.from_bytes(self.ptr.read(4)))
        if platform != 8:
            print("Invalid platform.")
            return

        tx.filtering = int.from_bytes(self.ptr.read(1))
        wrapd = self.ptr.read(1)
        tx.addressU = wrapd & 0x0F
        tx.addressV = wrapd >> 4
        self.ptr.seek(self.ptr.tell() + 2)

        tx.name = self.read_vcstring(32).lower()
        tx.mask = self.read_vcstring(32).lower()

        tx.flags = uint32(int.from_bytes(self.ptr.read(4)))
        hasAlpha = uint32(int.from_bytes(self.ptr.read(4)))

        texW = uint16(int.from_bytes(self.ptr.read(2)))
        texH = uint16(int.from_bytes(self.ptr.read(2)))

        depth = self.ptr.read(1)
        mipcount = self.ptr.read(1)
        xtype = self.ptr.read(1)

        tx.compression = int.from_bytes(self.ptr.read(1))

        palette = []
        scans = []

        if (tx.flags & rwd.FORMAT_EXT_PAL8) > 0 or (tx.flags & rwd.FORMAT_EXT_PAL4) > 0:
            palleteSize = 1024
            if (tx.flags & rwd.FORMAT_EXT_PAL4) > 0:
                palleteSize = 64

            palette = self.ptr.read(palleteSize)
        for mip in range(mipcount):
            dataSize = int.from_bytes(self.ptr.read(4))
            if dataSize == 0:
                if (tx.flags & rwd.FORMAT_EXT_PAL8) > 0 or (tx.flags & rwd.FORMAT_EXT_PAL4) > 0:
                    dataSize = texW * texH
                    if (tx.flags & rwd.FORMAT_EXT_PAL4) > 0:
                        dataSize /= 2
                elif tx.compression != 0:
                    ttw = texW
                    tth = texH

                    if ttw < 4: ttw = 4
                    if tth < 4: tth = 4
                    if tx.compression == 3:
                        dataSize = (ttw / 4) * (tth / 4) * 16
                    else:
                        dataSize = (ttw / 4) * (tth / 4) * 8

            data = self.ptr.read(dataSize)
            scan: Scan = Scan()
            scan.size = Vector2I(texW, texH)

            if (tx.flags & rwd.FORMAT_EXT_PAL8) > 0:
                output = [] * (texW * texH * 4)
                for i in range(len(data)):
                    for j in range(0, 4):
                        output[i * 4 + j] = palette[data[i] * 4 + j]
                scan.data = output
            else:
                scan.data = data
            scans.append(scan)

            texW /= 2
            texH /= 2
        tx.scans = scans
        return tx

    def __init__(self, data, readNow: bool = False) -> None:
        if readNow:
            self.read_data()
        
        pass

def send_texture(tex: TXEntry):
    mipLevel = 0

    if tex.compression != 0:
        print("Compresssed texture files not supported.")
        return None

    for scan in tex.scans:
        rl.load_image_raw()