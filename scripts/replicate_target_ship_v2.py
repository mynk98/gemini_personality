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

def replicate_target_ship_v2():
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

# World: High Altitude Day (Blue Sky)
if not bpy.context.scene.world:
    bpy.context.scene.world = bpy.data.worlds.new("World")
bpy.context.scene.world.use_nodes = True
bg = bpy.context.scene.world.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (0.4, 0.6, 0.9, 1)
bg.inputs['Strength'].default_value = 1.2

# --- 2. Materials ---
def create_mat(name, color, roughness=0.3, emission_strength=0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = roughness
    if emission_strength > 0:
        bsdf.inputs['Emission Strength'].default_value = emission_strength
        bsdf.inputs['Emission Color'].default_value = color
    return mat

mat_hull = create_mat("White_Hull", (0.9, 0.9, 0.92, 1), 0.1)
mat_black = create_mat("Black_Panel", (0.05, 0.05, 0.05, 1), 0.8)
mat_mech = create_mat("Mech_Grey", (0.3, 0.3, 0.3, 1), 0.6)
mat_ion = create_mat("Ion_Cyan", (0.0, 0.8, 1.0, 1), 0, 80.0) # Brighter
mat_glass = create_mat("Cockpit", (0.0, 0.0, 0.05, 1), 0.0)

# --- 3. Unified Blended Wing Construction ---

# Start with a Cube for the central mass
bpy.ops.mesh.primitive_cube_add(location=(0,0,0))
ship = bpy.context.active_object
ship.name = "BlendedShip"
ship.scale = (1.0, 2.5, 0.6)
bpy.ops.object.transform_apply(scale=True)

bm = bmesh.new()
bm.from_mesh(ship.data)
bm.faces.ensure_lookup_table()

# A. Shape the Fuselage
# Taper Nose
front_verts = [v for v in bm.verts if v.co.y > 2.0]
bmesh.ops.scale(bm, vec=(0.2, 1, 0.1), verts=front_verts)
bmesh.ops.translate(bm, vec=(0, 0, -0.2), verts=front_verts) # Drop nose

# B. Extrude Wings (Blended)
# Select side faces
bm.faces.ensure_lookup_table()
side_faces = [f for f in bm.faces if abs(f.normal.x) > 0.9]
res = bmesh.ops.extrude_discrete_faces(bm, faces=side_faces)
for f in res['faces']:
    # Pull wings out and back
    side = 1 if f.calc_center_median().x > 0 else -1
    bmesh.ops.translate(bm, vec=(2.0 * side, -1.5, -0.2), verts=f.verts)
    bmesh.ops.scale(bm, vec=(1.5, 1.5, 0.1), verts=f.verts)
    # Rotate for sweep
    bmesh.ops.rotate(bm, cent=f.calc_center_median(), matrix=mathutils.Matrix.Rotation(math.radians(-20*side), 3, 'Z'), verts=f.verts)

# C. Detail Passes
bm.faces.ensure_lookup_table()

# Top Panels (Black) - Inset and Assign
top_wing_faces = [f for f in bm.faces if f.normal.z > 0.8 and abs(f.calc_center_median().x) > 1.0]
if top_wing_faces:
    res = bmesh.ops.inset_region(bm, faces=top_wing_faces, thickness=0.1)
    for f in res['faces']:
        f.material_index = 1 # Black

# Rear Engine Bay (Mechanics)
rear_faces = [f for f in bm.faces if f.normal.y < -0.8]
if rear_faces:
    res = bmesh.ops.extrude_discrete_faces(bm, faces=rear_faces)
    eng_face = res['faces'][0]
    bmesh.ops.translate(bm, vec=(0, -0.5, 0), verts=eng_face.verts)
    bmesh.ops.scale(bm, vec=(0.8, 1, 0.8), verts=eng_face.verts)
    # Inset for "Mech" area
    res2 = bmesh.ops.inset_region(bm, faces=[eng_face], thickness=0.2)
    res2['faces'][0].material_index = 2 # Grey Mech

# D. Subsurf & Crease Logic
# Crease sharp edges (Rear, Wing tips) to hold shape under subsurf
for e in bm.edges:
    if abs(e.verts[0].co.y) < -2.0 or abs(e.verts[0].co.x) > 2.0:
        e.seam = 1.0 # Mark seam
        # e.crease = 1.0 # BMesh crease access depends on layer, simpler to use bevel mod or sharp edges

bm.to_mesh(ship.data)
bm.free()

# Materials
ship.data.materials.append(mat_hull)
ship.data.materials.append(mat_black)
ship.data.materials.append(mat_mech)

# Subsurf for the "Blended" look
sub = ship.modifiers.new(name='Subsurf', type='SUBSURF')
sub.levels = 2

# Weighted Normal for shading
ship.data.use_auto_smooth = True
wn = ship.modifiers.new(name='WeightedNormal', type='WEIGHTED_NORMAL')
wn.keep_sharp = True

bpy.ops.object.shade_smooth()

# --- 4. Separate Details (Engines & Cockpit) ---

# Engine Thrusters (Rectangular Pads)
for x in [-0.6, 0.6]:
    bpy.ops.mesh.primitive_cube_add(location=(x, -3.2, 0.2))
    pad = bpy.context.active_object
    pad.scale = (0.4, 0.1, 0.3)
    pad.data.materials.append(mat_ion)
    pad.parent = ship

# Top Dock
bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=0.1, location=(0, 0.5, 0.65))
dock = bpy.context.active_object
dock.data.materials.append(mat_black)
dock.parent = ship

# Cockpit Windows (Black inset)
bpy.ops.mesh.primitive_cube_add(location=(0, 2.2, 0.4))
win = bpy.context.active_object
win.scale = (0.4, 0.6, 0.2)
win.rotation_euler[0] = math.radians(25)
win.data.materials.append(mat_glass)
win.parent = ship

# --- 5. Lighting & Camera (Match Reference) ---
# Sun coming from top-left
bpy.ops.object.light_add(type='SUN', location=(10, 10, 10))
sun = bpy.context.active_object
sun.data.energy = 6
sun.rotation_euler = (math.radians(60), 0, math.radians(45))

# Soft fill from below (snow reflection)
bpy.ops.object.light_add(type='AREA', location=(0, 0, -10))
fill = bpy.context.active_object
fill.data.energy = 300
fill.rotation_euler[0] = math.radians(180)

# Camera: High Angle Rear/Side
bpy.ops.object.camera_add(location=(6, -8, 6), rotation=(math.radians(50), 0, math.radians(35)))
cam = bpy.context.active_object
bpy.context.scene.camera = cam

# Render
output_path = os.path.expanduser('~/Project/gemini personality/personality/camera/target_ship_v2.png')
bpy.context.scene.render.filepath = output_path
bpy.ops.render.render(write_still=True)
"""
    print("Refining target ship replication (Version 2)...")
    return send_blender_command("execute_code", {"code": blender_code})

if __name__ == "__main__":
    res = replicate_target_ship_v2()
    print("Visual Cortex Response:", res)
