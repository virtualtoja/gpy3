import pyray
from pyray import *

import filesystem.dffmodel as dff
import renderer.modelconv as dconv

init_window(1024, 768, "ModernVice")
set_target_fps(120)

mesh_rl: Mesh
model = input("Enter path to model file: ")
model_rw = dff.RWModelFile(model)
mesh_rl = dconv.convert(model_rw)

model_rl = load_model_from_mesh(mesh_rl)
model_rl.materials[0].maps[0].texture = load_texture_from_image(
    gen_image_checked(256, 256, 32, 32, Color(255, 109, 194, 255), Color(0, 0, 0, 255)))

c3d = Camera3D([5.0, 5.0, 5.0], [0.0, 0.0, 0.0], [0.0, 1.0, 0.0], 45.0, 0)
set_camera_mode(c3d, 4)
scale = 1.0

while not window_should_close():
    update_camera(c3d)

    begin_drawing()
    clear_background(Color(245, 245, 245, 255))
    begin_mode_3d(c3d)

    draw_model(model_rl, Vector3(0, 0, 0), scale, Color(255, 255, 255, 255))
    draw_grid(10, 1.0)

    if is_key_pressed(pyray.KeyboardKey.KEY_UP): scale += 0.1
    if is_key_pressed(pyray.KeyboardKey.KEY_DOWN): scale -= 0.1

    end_mode_3d(c3d)

    draw_fps(0, 0)
    end_drawing()
close_window()
