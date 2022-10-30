from pathlib import Path

import struct
import os
#import pickle

SECTOR_SIZE = 2048

class DirectoryEntry:
    offset: int
    size: int
    name: str

    def __init__(self, offset: int, size: int, name: str) -> None:
        self.offset = offset
        self.size = size
        self.name = name

        pass

class IMGArchive:
    entries = []
    files = []

    def __init__(self, dirfile: str, imgfile: str, unpackdir: str = "") -> None:
        dirdata = Path(dirfile).read_bytes()
        imgdata = Path(imgfile).read_bytes()
        if unpackdir != "":
            try: os.mkdir(unpackdir)
            except: print("error creating folder.")

        for i in range(0, len(dirdata), 32):
            hdrdata = struct.unpack('ii', dirdata[i: i + 8])
            hdrname = ""

            for j in range(8, 32):
                if hdrname != "" and dirdata[i+j] == 0x00: break;
                if dirdata[i+j] == 0x06 or dirdata[i+j] == 0x13: continue
                hdrname += chr(dirdata[i+j])

            self.entries.append(DirectoryEntry(hdrdata[0], hdrdata[1], hdrname))
            print(f"Name: {hdrname}, Offset: {hdrdata[0]}, Size: {hdrdata[1]}")

        for i in self.entries:
            file = []

            for j in range(i.offset*2048, (i.size+i.offset)*2048):
                file.append(imgdata[j])
            self.files.append((i.name, file))

            if unpackdir != "":
                print(f"Writing {len(file)} bytes to {i.name}")
                data = bytes(file) #struct.pack(len(file) * "B", *file)
                try: file = open(unpackdir + i.name, "xb")
                except: file = open(unpackdir + i.name, "wb")
                file.write(data)

        pass