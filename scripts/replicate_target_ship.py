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
            s.settimeout(180.0) 
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

def replicate_target_ship():
    blender_code = r"""
import bpy
import bmesh
import math
import random
import os

# --- 1. Scene Reset ---
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 256
bpy.context.scene.cycles.use_denoising = True

# World: Bright High-Altitude Day
if not bpy.context.scene.world:
    bpy.context.scene.world = bpy.data.worlds.new("World")
bpy.context.scene.world.use_nodes = True
bg = bpy.context.scene.world.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (0.6, 0.7, 0.9, 1) # Sky Blue
bg.inputs['Strength'].default_value = 1.0

# --- 2. Materials ---
def create_mat(name, color, roughness=0.4, emission_strength=0):
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

mat_white = create_mat("Hull_White", (0.9, 0.9, 0.92, 1), 0.1) # Glossy
mat_black = create_mat("Panel_Black", (0.05, 0.05, 0.05, 1), 0.8) # Matte
mat_grey = create_mat("Mech_Grey", (0.2, 0.2, 0.2, 1), 0.5)
mat_blue = create_mat("Ion_Blue", (0.0, 0.6, 1.0, 1), 0, 50.0)
mat_glass = create_mat("Cockpit_Dark", (0.0, 0.0, 0.05, 1), 0.0)

# --- 3. Construction ---

# A. Central Fuselage (Snub Nose)
bpy.ops.mesh.primitive_cube_add(location=(0, 1, 0))
fuselage = bpy.context.active_object
fuselage.name = "Fuselage"
fuselage.scale = (1.2, 3.5, 0.8)
bpy.ops.object.transform_apply(scale=True)
fuselage.data.materials.append(mat_white)

# Taper the nose
bm = bmesh.new()
bm.from_mesh(fuselage.data)
bm.faces.ensure_lookup_table()
front_face = [f for f in bm.faces if f.normal.y > 0.9][0]
bmesh.ops.scale(bm, vec=(0.4, 1, 0.3), verts=front_face.verts)
# Flatten rear
rear_face = [f for f in bm.faces if f.normal.y < -0.9][0]
bmesh.ops.scale(bm, vec=(1.5, 1, 1.2), verts=rear_face.verts)
bm.to_mesh(fuselage.data)
bm.free()

# B. Delta Wings
for side in [-1, 1]:
    bpy.ops.mesh.primitive_cube_add(location=(2.5 * side, -0.5, -0.2))
    wing = bpy.context.active_object
    wing.scale = (1.8, 2.5, 0.1)
    # Rotate slightly to sweep back
    wing.rotation_euler[2] = math.radians(-15 * side)
    # Anhedral (Angle down)
    wing.rotation_euler[1] = math.radians(10 * side)
    
    wing.data.materials.append(mat_white)
    wing.data.materials.append(mat_black)
    
    # Assign Black Panel to Top Face
    bm = bmesh.new()
    bm.from_mesh(wing.data)
    bm.faces.ensure_lookup_table()
    top_face = [f for f in bm.faces if f.normal.z > 0.8][0]
    
    # Inset for panel border
    res = bmesh.ops.inset_region(bm, faces=[top_face], thickness=0.15)
    res['faces'][0].material_index = 1 # Black
    
    bm.to_mesh(wing.data)
    bm.free()
    wing.parent = fuselage

# C. Engine Pods
for side in [-1, 1]:
    bpy.ops.mesh.primitive_cube_add(location=(1.2 * side, -3.5, 0.2))
    eng = bpy.context.active_object
    eng.scale = (0.8, 1.2, 0.8)
    eng.data.materials.append(mat_grey)
    eng.parent = fuselage
    
    # Thrusters (4 dots)
    for i in range(4):
        # 2x2 grid or horizontal line? Reference looks like horizontal line of 4
        # Let's do a 2x2 grid for density, looks cooler and fits the "quad" desc
        # Actually reference image shows 4 in a horizontal row? No, it looks like 4 large blue circles.
        # Let's do 2x2.
        ox = (i % 2) * 0.4 - 0.2
        oz = (i // 2) * 0.4 - 0.2
        bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.1, location=(1.2 * side + ox, -4.7, 0.2 + oz), rotation=(math.radians(90), 0, 0))
        thruster = bpy.context.active_object
        thruster.data.materials.append(mat_blue)
        thruster.parent = eng

# D. Top Detail (Docking Port)
bpy.ops.mesh.primitive_cylinder_add(radius=0.6, depth=0.2, location=(0, 0, 0.8))
dock = bpy.context.active_object
dock.data.materials.append(mat_black)
# Add detail ring
bpy.ops.mesh.primitive_cylinder_add(radius=0.4, depth=0.25, location=(0, 0, 0.8))
dock_inner = bpy.context.active_object
dock_inner.data.materials.append(mat_grey)
dock_inner.parent = dock
dock.parent = fuselage

# E. Cockpit (Front)
# Just intersect a black shape
bpy.ops.mesh.primitive_cube_add(location=(0, 2.5, 0.5))
cockpit = bpy.context.active_object
cockpit.scale = (0.5, 0.8, 0.3)
cockpit.rotation_euler[0] = math.radians(20)
cockpit.data.materials.append(mat_glass)
cockpit.parent = fuselage

# --- 4. Lighting & Camera ---
bpy.ops.object.light_add(type='SUN', location=(10, 10, 10))
sun = bpy.context.active_object
sun.data.energy = 8
# Angle it to show the top/side
sun.rotation_euler = (math.radians(45), 0, math.radians(45))

# Camera - High Angle Rear/Side View (Chase Cam)
bpy.ops.object.camera_add(location=(8, -12, 8), rotation=(math.radians(55), 0, math.radians(35)))
cam = bpy.context.active_object
bpy.context.scene.camera = cam

# Save Blend for manual check
blend_path = os.path.expanduser('~/Project/gemini personality/blender_creations/target_ship_recreation.blend')
bpy.ops.wm.save_as_mainfile(filepath=blend_path)

# Render
output_path = os.path.expanduser('~/Project/gemini personality/personality/camera/target_ship_recreation.png')
bpy.context.scene.render.filepath = output_path
bpy.ops.render.render(write_still=True)
"""
    print("Replicating target spaceship geometry...")
    return send_blender_command("execute_code", {"code": blender_code})

if __name__ == "__main__":
    res = replicate_target_ship()
    print("Visual Cortex Response:", res)
