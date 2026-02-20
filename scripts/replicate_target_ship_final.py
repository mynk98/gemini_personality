import socket
import json
import time
import os

def send_blender_command(command_type, params=None):
    host = 'localhost'
    port = 9876
    command = {"type": command_type, "params": params or {}}
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(json.dumps(command).encode('utf-8'))
            s.settimeout(240.0) 
            data = b''
            while True:
                try:
                    chunk = s.recv(4096)
                    if not chunk: break
                    data += chunk
                    if data.strip().endswith(b'}'): break 
                except socket.timeout:
                    return {"status": "timeout"}
            return json.loads(data.decode('utf-8'))
    except Exception as e: return {"status": "error", "message": str(e)}

def replicate_target_ship_final():
    blender_code = r"""
import bpy
import bmesh
import math
import random
import os
import mathutils

# --- 1. Scene Reset ---
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 256
bpy.context.scene.cycles.use_denoising = True

# World
if not bpy.context.scene.world:
    bpy.context.scene.world = bpy.data.worlds.new("World")
bpy.context.scene.world.use_nodes = True
bg = bpy.context.scene.world.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (0.6, 0.7, 0.9, 1) # Sky Blue
bg.inputs['Strength'].default_value = 1.0

# --- 2. Materials ---
mat_hull = bpy.data.materials.new(name="White_Hull")
mat_hull.use_nodes = True
mat_hull.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.9, 0.9, 0.92, 1)
mat_hull.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.1

mat_black = bpy.data.materials.new(name="Panel_Black")
mat_black.use_nodes = True
mat_black.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.05, 0.05, 0.05, 1)

mat_ion = bpy.data.materials.new(name="Ion_Cyan")
mat_ion.use_nodes = True
mat_ion.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 50.0
mat_ion.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value = (0, 0.8, 1, 1)

# --- 3. Construction ---
bpy.ops.mesh.primitive_cube_add(location=(0,0,0))
ship = bpy.context.active_object
ship.name = "BlendedShip"
ship.scale = (1.0, 2.5, 0.6)
bpy.ops.object.transform_apply(scale=True)

bm = bmesh.new()
bm.from_mesh(ship.data)
bm.faces.ensure_lookup_table()

# A. Taper Nose
front_verts = [v for v in bm.verts if v.co.y > 2.0]
bmesh.ops.scale(bm, vec=(0.2, 1, 0.1), verts=front_verts)
bmesh.ops.translate(bm, vec=(0, 0, -0.2), verts=front_verts)

# B. Extrude Wings
bm.faces.ensure_lookup_table()
side_faces = [f for f in bm.faces if abs(f.normal.x) > 0.9]
res = bmesh.ops.extrude_discrete_faces(bm, faces=side_faces)

for f in res['faces']:
    side = 1 if f.calc_center_median().x > 0 else -1
    # Move and Scale
    bmesh.ops.translate(bm, vec=(2.0 * side, -1.5, -0.2), verts=list(f.verts))
    bmesh.ops.scale(bm, vec=(1.5, 1.5, 0.1), verts=list(f.verts))
    
    # Rotate (Sweep)
    rot_matrix = mathutils.Matrix.Rotation(math.radians(-20*side), 3, 'Z')
    bmesh.ops.rotate(bm, cent=f.calc_center_median(), matrix=rot_matrix, verts=list(f.verts))

bm.to_mesh(ship.data)
bm.free()

ship.data.materials.append(mat_hull)
ship.data.materials.append(mat_black)

# Modifiers
ship.modifiers.new(name='Subsurf', type='SUBSURF').levels = 2
bpy.ops.object.shade_smooth()

# Engines (Simple Boxes)
for x in [-0.8, 0.8]:
    bpy.ops.mesh.primitive_cube_add(location=(x, -3.0, 0.2))
    eng = bpy.context.active_object
    eng.scale = (0.5, 0.8, 0.5)
    eng.parent = ship
    # Thruster
    bpy.ops.mesh.primitive_cube_add(location=(x, -3.8, 0.2))
    th = bpy.context.active_object
    th.scale = (0.4, 0.1, 0.2)
    th.data.materials.append(mat_ion)
    th.parent = eng

# Camera
bpy.ops.object.camera_add(location=(8, -10, 8), rotation=(math.radians(55), 0, math.radians(35)))
bpy.context.scene.camera = bpy.context.active_object

# Light
bpy.ops.object.light_add(type='SUN', location=(10, 10, 10))
bpy.context.active_object.data.energy = 5

output_path = os.path.expanduser('~/Project/gemini personality/personality/camera/target_ship_final.png')
bpy.context.scene.render.filepath = output_path
bpy.ops.render.render(write_still=True)
"""
    print("Executing Final Replication Script...")
    return send_blender_command("execute_code", {"code": blender_code})

if __name__ == "__main__":
    res = replicate_target_ship_final()
    print("Visual Cortex Response:", res)
