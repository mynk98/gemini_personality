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

def generate_advanced_spaceship_v2():
    blender_code = r"""
import bpy
import bmesh
import random
import math
import os

# --- 1. Scene Reset & Engine Setup ---
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128 # Optimized for speed
bpy.context.scene.cycles.use_denoising = True

# World: Dark Void
if not bpy.context.scene.world:
    bpy.context.scene.world = bpy.data.worlds.new("World")
bpy.context.scene.world.use_nodes = True
nodes_w = bpy.context.scene.world.node_tree.nodes
nodes_w['Background'].inputs['Color'].default_value = (0.001, 0.001, 0.002, 1)

# --- 2. Advanced PBR Hull Material (Architect-Optimized) ---
def create_optimized_hull_mat():
    mat = bpy.data.materials.new(name="Architect_Hull")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new(type='ShaderNodeOutputMaterial')
    pbsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    pbsdf.inputs['Base Color'].default_value = (0.8, 0.8, 0.85, 1)
    pbsdf.inputs['Metallic'].default_value = 1.0
    
    # Normal Map (Panel Lines)
    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    voronoi = nodes.new(type='ShaderNodeTexVoronoi')
    voronoi.feature = 'F1'
    voronoi.inputs['Scale'].default_value = 20.0
    
    bump = nodes.new(type='ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.4
    
    links.new(tex_coord.outputs['Object'], voronoi.inputs['Vector'])
    links.new(voronoi.outputs['Distance'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], pbsdf.inputs['Normal'])
    
    # Roughness (Weathering)
    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 15.0
    links.new(noise.outputs['Fac'], pbsdf.inputs['Roughness'])
    
    # Window Emissive (Simplified Grid)
    math_node = nodes.new(type='ShaderNodeMath')
    math_node.operation = 'GREATER_THAN'
    math_node.inputs[1].default_value = 0.98
    
    noise_win = nodes.new(type='ShaderNodeTexNoise')
    noise_win.inputs['Scale'].default_value = 100.0
    
    links.new(noise_win.outputs['Fac'], math_node.inputs[0])
    links.new(math_node.outputs['Value'], pbsdf.inputs['Emission Strength'])
    pbsdf.inputs['Emission Color'].default_value = (0.1, 0.8, 1.0, 1)
    
    links.new(pbsdf.outputs['BSDF'], output.inputs['Surface'])
    return mat

mat_hull = create_optimized_hull_mat()
mat_engine = bpy.data.materials.new(name="Engine_Core")
mat_engine.use_nodes = True
mat_engine.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 100.0
mat_engine.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value = (1, 0.4, 0, 1)

# --- 3. Procedural Hull & Rule-Based Greebling ---
bpy.ops.mesh.primitive_cube_add(size=1.0)
obj = bpy.context.active_object
obj.name = "Architect_Spaceship"
obj.data.materials.append(mat_hull)

bm = bmesh.new()
bm.from_mesh(obj.data)

# A. Hull Generation (The Spine)
bm.faces.ensure_lookup_table()
last_face = [f for f in bm.faces if f.normal.y > 0.9][0]
spine_verts = []
for i in range(10):
    res = bmesh.ops.extrude_discrete_faces(bm, faces=[last_face])
    last_face = res['faces'][0]
    y_move = random.uniform(0.6, 1.4)
    bmesh.ops.translate(bm, vec=(0, y_move, 0), verts=last_face.verts)
    s = random.uniform(0.5, 1.2)
    bmesh.ops.scale(bm, vec=(s, 1, s), verts=last_face.verts)
    spine_verts.extend(last_face.verts)
    bm.faces.ensure_lookup_table()

# B. Rule-Based Greeble Pass
bm.faces.ensure_lookup_table()
# Identify target faces BEFORE starting modifications
# Rules: 1. Normal Z > 0.7 (Spine) or 2. Normal X > 0.8 (Sides)
# AND exclude very front/back for clarity
targets = []
for f in bm.faces:
    center = f.calc_center_median()
    if abs(center.y) < 5.0: # Middle of ship
        if f.normal.z > 0.7 or abs(f.normal.x) > 0.8:
            if random.random() > 0.6:
                targets.append(f)

for f in targets:
    if not f.is_valid: continue
    f_normal = f.normal.copy()
    # Safe Extrude
    res = bmesh.ops.extrude_discrete_faces(bm, faces=[f])
    g_face = res['faces'][0]
    # Detailed greebling: random height and multi-step
    depth = random.uniform(0.05, 0.2)
    bmesh.ops.translate(bm, vec=(f_normal * depth), verts=g_face.verts)
    bmesh.ops.scale(bm, vec=(0.7, 0.7, 0.7), verts=g_face.verts)
    bm.faces.ensure_lookup_table()

bm.to_mesh(obj.data)
bm.free()

# Symmetry Modifier
mod_mirror = obj.modifiers.new(name="Mirror", type='MIRROR')
mod_mirror.use_axis[0] = True 
mod_mirror.use_bisect_axis[0] = True

# C. Engine Array (Multiple ports)
for x_pos in [-0.8, 0, 0.8]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=0.4, location=(x_pos, -0.2, 0), rotation=(math.radians(90), 0, 0))
    eng = bpy.context.active_object
    eng.data.materials.append(mat_engine)
    eng.parent = obj

# --- 4. Lighting & Camera ---
bpy.ops.object.light_add(type='SUN', location=(10, -10, 10))
bpy.context.active_object.data.energy = 5
bpy.ops.object.light_add(type='POINT', location=(-5, 5, 2))
rim = bpy.context.active_object
rim.data.energy = 2000
rim.data.color = (0.0, 0.5, 1.0)

bpy.ops.object.camera_add(location=(15, -15, 10), rotation=(math.radians(60), 0, math.radians(45)))
bpy.context.scene.camera = bpy.context.active_object

output_path = os.path.expanduser('~/Project/gemini personality/personality/camera/architect_spaceship_v2_20260220.png')
bpy.context.scene.render.filepath = output_path
bpy.ops.render.render(write_still=True)
"""
    print("Delegating construction to Architect for final optimization...")
    return send_blender_command("execute_code", {"code": blender_code})

if __name__ == "__main__":
    res = generate_advanced_spaceship_v2()
    print("Visual Cortex Response:", res)
