from cffi import FFI
from renderer.rl_vicemodel import ViceModel

import filesystem.dffmodel as dff
import pyray as rl
import numpy as np

import ctypes
ffi = FFI()

def convert_image():
    pass

def convert(model: dff.RWModelFile):
    # model: ViceModel = ViceModel()
    # for surf in mesh.surfaces:
    #     msh = rl.Mesh()
    #
    #     msh.triangleCount = surf.triangleCount
    #     msh.vertexCount = len(surf.verticies)
    #     msh.vertices = ffi.new(f"float[{len(surf.verticies)}]", surf.vertices)
    #
    #     model.meshes.append(msh)
    mesh = rl.Mesh()

    vertex = []
    indices = []
    texcoords = []
    texcoords2 = []

    triangleCount = 0
    for surf in model.surfaces:
        for vert in surf.verticies:
            vertex.append(vert)
        for indi in surf.indices:
            indices.append(indi)
        for coord in surf.texcoords:
            texcoords.append(coord)
        for coord2 in surf.sec_texcoords:
            texcoords2.append(coord2)

        triangleCount += surf.triangleCount

    c_vert = ffi.new(f"float[{len(vertex)}]", vertex)
    c_indi = ffi.new(f"unsigned short[{len(indices)}]", indices)
    c_texc = ffi.new(f"float[{len(texcoords)}]", texcoords)
    c_tex2 = ffi.new(f"float[{len(texcoords2)}]", texcoords2)

    mesh.triangleCount = triangleCount
    mesh.vertexCount = len(vertex)

    mesh.vertices = c_vert
    mesh.indices = c_indi
    mesh.texcoords = c_texc
    mesh.texcoords2 = c_tex2

    print("<CONVERSION SUCCESS> ===================")
    print(f"Triangle count: {triangleCount}")
    print(f"Indices: {len(indices)}")
    print(f"Vertices: {len(vertex)}")
    print("Uploading mesh....")

    rl.upload_mesh(mesh, False)

    return mesh
