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
            s.settimeout(60.0)
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

def generate_spaceship():
    blender_code = r"""
import bpy
import bmesh
import random
import math
import os

# --- 1. Scene Setup ---
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128
bpy.context.scene.cycles.use_denoising = True

# Dark World
if not bpy.context.scene.world:
    bpy.context.scene.world = bpy.data.worlds.new("World")
bpy.context.scene.world.use_nodes = True
bpy.context.scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.002, 0.002, 0.005, 1)

# --- 2. Materials ---
def create_mat(name, color, emission=0, emissive_color=(1,1,1)):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = 0.2
    if emission > 0:
        bsdf.inputs['Emission Strength'].default_value = emission
        bsdf.inputs['Emission Color'].default_value = (emissive_color[0], emissive_color[1], emissive_color[2], 1.0)
    return mat

mat_hull = create_mat("Hull", (0.9, 0.9, 0.9, 1))
mat_accent = create_mat("Accent", (0.2, 0.2, 0.2, 1))
mat_engine = create_mat("Engine", (0.1, 0.1, 0.1, 1), 50, (1, 0.4, 0.1))
mat_window = create_mat("Window", (0.0, 0.5, 1.0, 1), 20, (0.1, 0.8, 1.0))

# --- 3. Procedural Hull Generation ---
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0,0,0))
obj = bpy.context.active_object

# Add Mirror Modifier
mod_mirror = obj.modifiers.new(name="Mirror", type='MIRROR')
mod_mirror.use_axis[0] = True 
mod_mirror.use_bisect_axis[0] = True
mod_mirror.use_clip = True

bm = bmesh.new()
bm.from_mesh(obj.data)

# Initial spine extrusion (Front)
bm.faces.ensure_lookup_table()
last_face = [f for f in bm.faces if f.normal.y > 0.9][0]
for i in range(5):
    res = bmesh.ops.extrude_discrete_faces(bm, faces=[last_face])
    last_face = res['faces'][0]
    bmesh.ops.translate(bm, vec=(0, 0.8, 0), verts=last_face.verts)
    scale = random.uniform(0.7, 0.95)
    bmesh.ops.scale(bm, vec=(scale, 1, scale), verts=last_face.verts)
    bm.faces.ensure_lookup_table()

# Initial spine extrusion (Back)
last_face_back = [f for f in bm.faces if f.normal.y < -0.9][0]
for i in range(2):
    res = bmesh.ops.extrude_discrete_faces(bm, faces=[last_face_back])
    last_face_back = res['faces'][0]
    bmesh.ops.translate(bm, vec=(0, -0.5, 0), verts=last_face_back.verts)
    if i == 1:
        bmesh.ops.scale(bm, vec=(1.2, 1, 1.2), verts=last_face_back.verts)
    bm.faces.ensure_lookup_table()

# --- 4. Greebling (Wings, Engines, Cockpit) ---
# Identify target faces BEFORE starting modifications
bm.faces.ensure_lookup_table()
wing_targets = [f.index for f in bm.faces if f.normal.x > 0.8 and abs(f.calc_center_median().y) < 1.0]

# Perform wing extrusions
for idx in wing_targets:
    bm.faces.ensure_lookup_table()
    f = bm.faces[idx]
    res = bmesh.ops.extrude_discrete_faces(bm, faces=[f])
    wing_face = res['faces'][0]
    bmesh.ops.translate(bm, vec=(1.5, -0.5, 0), verts=wing_face.verts)
    bmesh.ops.scale(bm, vec=(1, 0.5, 0.1), verts=wing_face.verts)
    wing_face.material_index = 1 

# Apply materials to remaining geometry
bm.faces.ensure_lookup_table()
for f in bm.faces:
    center = f.calc_center_median()
    if f.normal.y < -0.9:
        f.material_index = 2 # Engine
    elif f.normal.z > 0.8 and center.y > 1.5:
        f.material_index = 3 # Window

bm.to_mesh(obj.data)
bm.free()

# Final Scene Polish
obj.data.materials.append(mat_hull)
obj.data.materials.append(mat_accent)
obj.data.materials.append(mat_engine)
obj.data.materials.append(mat_window)

for poly in obj.data.polygons:
    poly.use_smooth = False

# --- 5. Lighting ---
bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
sun = bpy.context.active_object
sun.data.energy = 5

bpy.ops.object.light_add(type='POINT', location=(-5, 5, 2))
rim = bpy.context.active_object
rim.data.energy = 1000
rim.data.color = (0.0, 0.5, 1.0)

# --- 6. Camera & Render ---
bpy.ops.object.camera_add(location=(10, -10, 6), rotation=(math.radians(60), 0, math.radians(45)))
bpy.context.scene.camera = bpy.context.active_object

output_path = os.path.expanduser('~/Project/gemini personality/personality/camera/lowpoly_spaceship_20260220.png')
bpy.context.scene.render.filepath = output_path
bpy.ops.render.render(write_still=True)
"""
    print("Initiating procedural spaceship generation...")
    return send_blender_command("execute_code", {"code": blender_code})

if __name__ == "__main__":
    res = generate_spaceship()
    print("Visual Cortex Response:", res)
