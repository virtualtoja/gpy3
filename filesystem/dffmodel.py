from typing import ByteString
from filesystem.rwfiletypes import Atomic
from filesystem.rwfile import *

import filesystem.rwfiletypes as rwt

def containskey(arr, key) -> bool:
    for i in arr:
        if i[0] == key:
            return True;

    return False;
def readkey(arr, key):
    for i in arr:
        if i[0] == key: return i[1]

    return None
class Texture:
    name: str
    maskname: str
    tfilter: int
    addressU: int
    addressV: int
class BinaryMesh:
    indices = [0]
    binMaterial: None
    mode: int
class Material:
    flags: int
    color: bytearray
    props = [0]
    textures = [0]
    hasAlpha: bool
class Frame:
    name: str = ""
    rotation = [0]
    position = [0]

    parent: int = 0
    boneID: int = 0
class Geometry:
    flags: int
    spherePos = [0]
    sphereRadius: float

    binary = [0]
    materials = [0]
    colors: bytearray = [0]
    texcoords = [0]
    sec_texcoords = [0]

    frame: int = -1
    indices = [0]
    verticies = [0]
    normals = [0]
    triangleCount:int = 0
    bones: bytearray
    weights = [0]

    bonecount: int
    maxbonespervertex: int
    hasalpha: bool = False

class RWModelFile(RenderWareFile):
    geometry: Geometry
    surfaces: list()

    def __init__(self, filename) -> None:
        print(f"opening {filename}...")
        self.ptr = open(filename, "rb")

        h = self.read_header()
        if h.ctype != rwt.Clump:
            print("Invalid type, (l74 dffmodel.py)")
            self.ptr.seek(self.ptr.tell() + h.size)
            #return

        h = self.read_header()
        if h.ctype != rwt.Struct:
            print("Invalid type, (l79 dffmodel.py)")
            self.ptr.seek(self.ptr.tell() + h.size)
            #return

        numAtomics = self.read_int()
        if h.size == 12:
            numLights = self.read_int()
            numCameras = self.read_int()

        h = self.read_header()
        if h.ctype != rwt.FrameList:
            print(f"Invalid type {h.ctype}, {h.size}, (l89 dffmodel.py)")
            self.ptr.seek(self.ptr.tell() + h.size)
            #return

        h = self.read_header()
        if h.ctype != rwt.Struct:
            print("Invalid type, (l93 dffmodel.py)")
            self.ptr.seek(self.ptr.tell() + h.size)
            #return

        numFrames = self.read_int()
        print(f"NumFrames: {numFrames}\nNumAtomics: {numAtomics}")
        self.read_frames(numFrames)

        h = self.read_header()
        if h.ctype != rwt.GeometryList:
            print("Invalid type, (l102 dffmodel.py)")
            self.ptr.seek(self.ptr.tell() + h.size)
            #return
        h = self.read_header()
        if h.ctype != rwt.Struct:
            print("Invalid type, (l106 dffmodel.py)")
            self.ptr.seek(self.ptr.tell() + h.size)
            #return

        numGeometry = self.read_int()
        self.read_geometry(numGeometry)
        self.read_atomics(numAtomics)

        self.ptr.close()

    def read_frames(self, numFrames: int) -> None:
        frames = [Frame()] * numFrames

        for i in range(numFrames):
            #print(i)
            fr: Frame = Frame()

            fr.rotation = [0.0] * 9
            for i in range(9):
                fr.rotation[i] = self.read_float()

            fr.position = [0.0] * 3
            for i in range(3):
                fr.position[i] = self.read_float()

            fr.parent = self.read_int()
            self.ptr.seek(self.ptr.tell() + 4)
            frames[i] = fr

        frameRootLookup = [(0, 0)]

        for i in range(numFrames):
            h = self.read_header()
            if h.ctype != rwt.Extension:
                print(f"Invalid type {h.ctype}, {h.size}, (l138 dffmodel.py)")
                self.ptr.seek(self.ptr.tell() + h.size)
                return
            if h.size > 0:
                endps = self.ptr.tell() + h.size
                print(endps)
                while True:
                    if self.ptr.tell() >= endps:
                        break;
                    print("line 155")
                    h = self.read_header()
                    if h.size == 0: break;
                    if h.ctype == rwt.Frame:
                        frames[i].name = self.read_vcstring(h.size)
                        #break;
                    elif h.ctype == rwt.HAnim:
                        self.ptr.seek(self.ptr.tell() + 4)

                        boneID: int = self.read_int()
                        if frames[i].boneID == -1:
                            frames[i].boneID = boneID
                        boneCount: int = self.read_int()
                        if boneCount > 0:
                            self.ptr.seek(self.ptr.tell() + 8)

                        for bc in range(boneCount):
                            childBoneID: int = self.read_int()
                            childIndex: int = self.read_int()

                            self.ptr.seek(self.ptr.tell() + 4)
                            frameRootLookup.append((childBoneID, childIndex))
                        #break;
                    else:
                        self.ptr.seek(self.ptr.tell() + h.size)
                else:
                    break;

        for i in range(len(frames)):
            if frames[i].boneID != -1 and containskey(frameRootLookup, frames[i].boneID):
                frames[i].boneID = readkey(frameRootLookup, frames[i].boneID)
    def read_materials(self, numMaterials: int) -> None:
        self.geometry.materials = [0] * numMaterials
        for mt in range(numMaterials):
            h = self.read_header()

            if h.ctype != rwt.Material:
                print("Unexpected chunk")
                self.ptr.seek(self.ptr.tell() + h.size)
                #return

            h = self.read_header()
            if h.ctype != rwt.Struct:
                print("Invalid type, (l322 dffmodel.py)")
                self.ptr.seek(self.ptr.tell() + h.size)
                #return

            m = Material()
            m.flags = int.from_bytes(self.ptr.read(4), 'little')
            m.color = self.ptr.read(4)
            if m.color[3] < 254: m.hasAlpha = True

            self.ptr.seek(self.ptr.tell() + 4)

            texHave = self.read_int()
            m.props = [0.0] * 3
            for pg in range(3):
                m.props[pg] = self.read_float()

            if texHave > 0:
                h = self.read_header()

                texEnd: int = int(self.ptr.tell() + h.size)
                if h.ctype != rwt.Texture:
                    print("Invalid type, (l342 dffmodel.py)")
                    self.ptr.seek(self.ptr.tell() + h.size)
                    #return
                h = self.read_header()
                if h.ctype != rwt.Struct:
                    print("Invalid type, (l346 dffmodel.py)")
                    self.ptr.seek(self.ptr.tell() + h.size)
                    #return

                m.textures = [0] * 1
                t = Texture()
                m.textures[0] = t

                t.tfilter = self.ptr.read(1)
                wrapd = int.from_bytes(self.ptr.read(1), 'little')

                t.addressU = wrapd & 0x0f
                t.addressV = wrapd >> 4
                self.ptr.seek(self.ptr.tell() + 2)

                h = self.read_header()
                if h.ctype != rwt.String:
                    print("Invalid type, (l362 dffmodel.py)")
                    self.ptr.seek(self.ptr.tell() + h.size)
                    #return
                t.name = self.read_vcstring(h.size).lower()

                h = self.read_header()
                if h.ctype != rwt.String:
                    print("Invalid type, (l368 dffmodel.py)")
                    self.ptr.seek(self.ptr.tell() + h.size)
                    #return
                t.maskname = self.read_vcstring(h.size).lower()

                if t.maskname != "":
                    m.hasAlpha = True

                h = self.read_header()
                if h.ctype != rwt.Extension:
                    print("Invalid type, (l377 dffmodel.py)")
                    #self.ptr.seek(self.ptr.tell() + h.size)
                    #return
                self.ptr.seek(self.ptr.tell() + h.size)
            else:
                if self.geometry.hasalpha:
                    m.hasAlpha = True

            h = self.read_header()
            if h.ctype != rwt.Extension:
                print("Invalid type, (l386 dffmodel.py)")
                self.ptr.seek(self.ptr.tell() + h.size)
                #return

            if h.size > 0:
                ops: int = self.ptr.tell() + h.size

                while True:
                    if self.ptr.tell() >= ops:
                        break;

                    h = self.read_header()
                    self.ptr.seek(self.ptr.tell() + h.size)
            self.geometry.materials[mt] = m
    def read_geometry(self, geoNums: int):
        surfaces = [0] * geoNums
        print(f"surface arr size: {geoNums}, on byte {self.ptr.tell()}")

        for i in range(geoNums):
            self.geometry = Geometry()

            h = self.read_header('surface')
            if h.ctype != rwt.Geometry:
                print("Invalid type, (l179 dffmodel.py)")
                self.ptr.seek(self.ptr.tell() + h.size)
                #return
            h = self.read_header('surface')
            if h.ctype != rwt.Struct:
                print("Invalid type, (l183 dffmodel.py)")
                self.ptr.seek(self.ptr.tell() + h.size)
                #return

            self.geometry.flags = int.from_bytes(self.ptr.read(2), 'little')

            texCoords = self.ptr.read(1)
            if self.geometry.flags & 0x04 > 0:
                texCoords = 1
            nativeGeom: bool = self.read_bool()
            triCount: int = self.read_int()
            self.geometry.triangleCount = triCount
            vertCount = self.read_int()
            self.read_int()

            if h.version < 0x1003:
                self.ptr.seek(self.ptr.tell() + 12)

            if not nativeGeom:
                if self.geometry.flags & 0x08 > 0:
                    self.geometry.colors = self.ptr.read(vertCount * 4)
                    for ci in range(3, len(self.geometry.colors), 4):
                        if self.geometry.colors[ci] < 255:
                            self.geometry.hasalpha = True
                            #break

                if self.geometry.flags & 0x04 > 0:
                    self.geometry.texcoords = [0] * (vertCount * 2)
                    for c in range(len(self.geometry.texcoords)):
                        self.geometry.texcoords[c] = self.read_float()

                if self.geometry.flags & 0x80 > 0:
                    for cd in range(texCoords):
                        coords = [0.0] * (vertCount * 2)
                        for c in range(len(coords)):
                            coords[c] = self.read_float()
                        if cd == 0:
                            self.geometry.texcoords = coords
                        elif cd == 1:
                            self.geometry.sec_texcoords = coords;

                self.geometry.indices = [0] * (triCount * 4)
                for c in range(len(self.geometry.indices)):
                    self.geometry.indices[c] = int.from_bytes(self.ptr.read(2), 'little')
            self.geometry.spherePos = [0.0] * 3
            for c in range(3):
                self.geometry.spherePos[c] = self.read_float()
            self.geometry.sphereRadius = self.read_float()

            self.ptr.seek(self.ptr.tell() + 8)
            if not nativeGeom:
                self.geometry.verticies = [0.0] * (vertCount * 3)
                for v in range(len(self.geometry.verticies)):
                    self.geometry.verticies[v] = self.read_float()

                if self.geometry.flags & 0x10 > 0:
                    self.geometry.normals = [0.0] * (vertCount * 3)
                    for vn in range(vertCount * 3):
                        self.geometry.normals[vn] = self.read_float()

            h = self.read_header('material list')
            if h.ctype != rwt.MaterialList:
                print("Invalid type, (l243 dffmodel.py)")
                self.ptr.seek(self.ptr.tell() + h.size)
                #return
            h = self.read_header('struct_surface')
            if h.ctype != rwt.Struct:
                print("Invalid type, (l247 dffmodel.py)")
                self.ptr.seek(self.ptr.tell() + h.size)
                #return

            materialNum: int = self.read_int()
            self.ptr.seek(self.ptr.tell() + materialNum * 4)
            self.read_materials(materialNum)

            h = self.read_header()
            if h.ctype != rwt.Extension:
                print("Invalid type, (l256 dffmodel.py)")
                self.ptr.seek(self.ptr.tell() + h.size)
                #return
            if h.size > 0:
                ops: int = self.ptr.tell() + h.size

                while True:
                    if self.ptr.tell() >= ops: break;

                    h = self.read_header()
                    if h.ctype == rwt.BinMesh:
                        splitMode: int = self.read_int()
                        if splitMode != 0 and splitMode != 1:
                            return
                        numSplits = self.read_int()
                        self.ptr.seek(self.ptr.tell() + 4)
                        self.geometry.binary = [BinaryMesh()] * numSplits

                        hasData: bool = h.size > 12 + numSplits * 8
                        for sp in range(numSplits):
                            numInds = self.read_int()
                            matIndex = self.read_int()

                            bn = BinaryMesh()
                            bn.binMaterial = self.geometry.materials[matIndex]
                            bn.mode = splitMode
                            if hasData:
                                bn.indices = [0] * numInds
                                for vr in range(numInds):
                                    bn.indices[vr] = self.read_int()
                            self.geometry.binary[sp] = bn
                        #break;
                    elif h.ctype == rwt.Skin:
                        self.geometry.bonecount = self.ptr.read(1)
                        usedBones = self.ptr.read(1)

                        self.geometry.maxbonespervertex = self.ptr.read(1)[0]
                        self.ptr.seek(self.ptr.tell() + 1)
                        if usedBones > 0:
                            self.ptr.seek(self.ptr.tell() + usedBones)

                        numVerts = len(self.geometry.verticies) / 3
                        self.geometry.bones = self.ptr.read(numVerts * 4)
                        self.geometry.weights = [0.0] * (numVerts * 4)
                        for b in range(len(self.geometry.weights)):
                            self.geometry.weights[b] = self.read_float()

                        if self.geometry.maxbonespervertex == 0:
                            self.ptr.seek(self.ptr.tell() + 4 * self.geometry.bonecount)
                        self.ptr.seek(self.ptr.tell() + self.geometry.bonecount * 64)
                        if usedBones > 0:
                            self.ptr.seek(self.ptr.tell() + 12)
                    else:
                        self.ptr.seek(self.ptr.tell() + h.size)
            surfaces[i] = self.geometry
        self.surfaces = surfaces
    def read_atomics(self, numAtomics):
        for i in range(numAtomics):
            h = self.read_header()
            if h.ctype != rwt.Atomic:
                print("Invalid type, (l403 dffmodel.py)")
                #return
            h = self.read_header()
            if h.ctype != rwt.Struct:
                print("Invalid type, (l407 dffmodel.py)")
                self.ptr.seek(self.ptr.tell() + h.size)
                #return

            frameIndex: int = self.read_int()
            geomIndex: int = self.read_int()
            self.ptr.seek(self.ptr.tell() + 8)

            if self.surfaces[geomIndex].frame != -1:
                return
            self.surfaces[geomIndex].frame = frameIndex

            h = self.read_header()
            if h.ctype != rwt.Extension:
                print("Invalid type, (l420 dffmodel.py)")
                #self.ptr.seek(self.ptr.tell() + h.size)
                #return
            self.ptr.seek(self.ptr.tell() + h.size)