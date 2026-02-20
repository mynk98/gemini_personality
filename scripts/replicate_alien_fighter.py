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

def replicate_alien_fighter():
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

# Dark Space World
if not bpy.context.scene.world:
    bpy.context.scene.world = bpy.data.worlds.new("World")
bpy.context.scene.world.use_nodes = True
bg = bpy.context.scene.world.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (0.01, 0.01, 0.02, 1)

# --- 2. Materials ---
mat_obsidian = bpy.data.materials.new(name="Obsidian_Armor")
mat_obsidian.use_nodes = True
mat_obsidian.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.02, 0.02, 0.02, 1)
mat_obsidian.node_tree.nodes['Principled BSDF'].inputs['Metallic'].default_value = 0.9
mat_obsidian.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.2

mat_gunmetal = bpy.data.materials.new(name="Gunmetal")
mat_gunmetal.use_nodes = True
mat_gunmetal.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.2, 0.2, 0.2, 1)
mat_gunmetal.node_tree.nodes['Principled BSDF'].inputs['Metallic'].default_value = 1.0

mat_glow = bpy.data.materials.new(name="Alien_Glow")
mat_glow.use_nodes = True
mat_glow.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 50.0
mat_glow.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value = (0.0, 0.8, 1.0, 1)

mat_glass = bpy.data.materials.new(name="Cockpit_Glass")
mat_glass.use_nodes = True
mat_glass.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0, 0, 0, 1)
mat_glass.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.0
mat_glass.node_tree.nodes['Principled BSDF'].inputs['IOR'].default_value = 1.45

# --- 3. Construction ---

# A. Central Spine (Needle Nose)
bpy.ops.mesh.primitive_cube_add(location=(0,0,0))
spine = bpy.context.active_object
spine.name = "Alien_Spine"
spine.scale = (0.8, 1.0, 0.6)
bpy.ops.object.transform_apply(scale=True)

bm = bmesh.new()
bm.from_mesh(spine.data)
bm.faces.ensure_lookup_table()

# Extrude Nose (Forward)
front_face = [f for f in bm.faces if f.normal.y > 0.9][0]
for i in range(5):
    res = bmesh.ops.extrude_discrete_faces(bm, faces=[front_face])
    front_face = res['faces'][0]
    bmesh.ops.translate(bm, vec=(0, 1.2, -0.1), verts=list(front_face.verts))
    bmesh.ops.scale(bm, vec=(0.7, 1, 0.6), verts=list(front_face.verts)) # Taper

# Extrude Rear (Heavy)
bm.faces.ensure_lookup_table()
rear_face = [f for f in bm.faces if f.normal.y < -0.9][0]
res = bmesh.ops.extrude_discrete_faces(bm, faces=[rear_face])
rear_face = res['faces'][0]
bmesh.ops.translate(bm, vec=(0, -2.0, 0.2), verts=list(rear_face.verts))
bmesh.ops.scale(bm, vec=(1.5, 1, 1.2), verts=list(rear_face.verts))

bm.to_mesh(spine.data)
bm.free()
spine.data.materials.append(mat_obsidian)

# B. Claw Wings (Forward Swept)
# Create separate object for easier mirroring
bpy.ops.mesh.primitive_cube_add(location=(1.0, -1.0, 0))
wing = bpy.context.active_object
wing.scale = (0.5, 1.5, 0.2)
bpy.ops.object.transform_apply(scale=True)

bm = bmesh.new()
bm.from_mesh(wing.data)
bm.faces.ensure_lookup_table()

# Extrude Out and Forward
side_face = [f for f in bm.faces if f.normal.x > 0.9][0]
# Segment 1: Out
res = bmesh.ops.extrude_discrete_faces(bm, faces=[side_face])
f = res['faces'][0]
bmesh.ops.translate(bm, vec=(1.5, 0, 0), verts=list(f.verts))
bmesh.ops.scale(bm, vec=(1, 0.8, 0.5), verts=list(f.verts))

# Segment 2: Forward Hook
res = bmesh.ops.extrude_discrete_faces(bm, faces=[f])
f = res['faces'][0]
bmesh.ops.translate(bm, vec=(1.0, 2.0, -0.2), verts=list(f.verts)) # Forward sweep
bmesh.ops.rotate(bm, cent=f.calc_center_median(), matrix=mathutils.Matrix.Rotation(math.radians(30), 3, 'Z'), verts=list(f.verts))
bmesh.ops.scale(bm, vec=(0.6, 1, 0.5), verts=list(f.verts)) # Taper tip

# Segment 3: Sharp Tip
res = bmesh.ops.extrude_discrete_faces(bm, faces=[f])
f = res['faces'][0]
bmesh.ops.translate(bm, vec=(0.2, 1.5, -0.1), verts=list(f.verts))
bmesh.ops.scale(bm, vec=(0.1, 0.1, 0.1), verts=list(f.verts))

bm.to_mesh(wing.data)
bm.free()
wing.data.materials.append(mat_obsidian)

# Mirror Wing
mod_mirror = wing.modifiers.new(name='Mirror', type='MIRROR')
mod_mirror.mirror_object = spine

# C. Heavy Guns (Wing Tips)
bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=3.0, location=(3.5, 1.0, 0))
gun = bpy.context.active_object
gun.rotation_euler[0] = math.radians(90) # Point forward
gun.data.materials.append(mat_gunmetal)
# Mirror Gun
mod_mirror_gun = gun.modifiers.new(name='Mirror', type='MIRROR')
mod_mirror_gun.mirror_object = spine

# D. Cockpit Canopy (Bubble)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.6, location=(0, 1.5, 0.5))
cockpit = bpy.context.active_object
cockpit.scale = (0.7, 1.5, 0.5)
cockpit.data.materials.append(mat_glass)

# E. Details (Bevel Modifier for Armor Look)
spine.modifiers.new(name='Bevel', type='BEVEL').width = 0.05
wing.modifiers.new(name='Bevel', type='BEVEL').width = 0.05

# F. Lighting & Camera (Cinematic Front-Left)
bpy.ops.object.light_add(type='SUN', location=(-10, -10, 10))
sun = bpy.context.active_object
sun.data.energy = 5
sun.rotation_euler = (math.radians(60), 0, math.radians(-45))

# Rim Light (Blue)
bpy.ops.object.light_add(type='POINT', location=(5, 5, 5))
rim = bpy.context.active_object
rim.data.energy = 1000
rim.data.color = (0, 0.5, 1)

# Camera
bpy.ops.object.camera_add(location=(-8, -8, 6), rotation=(math.radians(60), 0, math.radians(-45)))
bpy.context.scene.camera = bpy.context.active_object

output_path = os.path.expanduser('~/Project/gemini personality/personality/camera/alien_fighter_v1.png')
bpy.context.scene.render.filepath = output_path
bpy.ops.render.render(write_still=True)
"""
    print("Replicating Alien Fighter geometry...")
    return send_blender_command("execute_code", {"code": blender_code})

if __name__ == "__main__":
    res = replicate_alien_fighter()
    print("Visual Cortex Response:", res)
