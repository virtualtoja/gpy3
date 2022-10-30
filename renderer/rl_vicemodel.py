from pyray import *

class ViceModel:
    meshes = []
    materials = []
    texture = []

    position = (0, 0, 0)
    rotation = (0, 0, 0)
    scale = (0, 0, 0)

    def construct_materials(self) -> None:
        pass

    def render(self) -> None:
        for i in range(len(self.meshes)):
            mdl = load_model_from_mesh(self.meshes[i])
            mdl.materials[0].maps[0].texture = load_texture_from_image(gen_image_checked(256, 256, 32, 32, Color(255, 109, 194, 255), Color(0, 0, 0, 255)))
            draw_model_ex(mdl, self.position, self.rotation, self.rotation[0], self.scale, Color(255, 255, 255, 255))