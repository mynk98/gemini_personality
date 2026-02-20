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

def generate_advanced_spaceship():
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
bpy.context.scene.cycles.samples = 256
bpy.context.scene.cycles.use_denoising = True

# World: Dark Void with Volumetric Scatter
if not bpy.context.scene.world:
    bpy.context.scene.world = bpy.data.worlds.new("World")
bpy.context.scene.world.use_nodes = True
nodes_w = bpy.context.scene.world.node_tree.nodes
links_w = bpy.context.scene.world.node_tree.links
nodes_w.clear()
node_w_out = nodes_w.new(type='ShaderNodeOutputWorld')
node_w_bg = nodes_w.new(type='ShaderNodeBackground')
node_w_bg.inputs['Color'].default_value = (0.001, 0.001, 0.002, 1)
node_w_vol = nodes_w.new(type='ShaderNodeVolumeScatter')
node_w_vol.inputs['Density'].default_value = 0.01
links_w.new(node_w_bg.outputs['Background'], node_w_out.inputs['Surface'])
links_w.new(node_w_vol.outputs['Volume'], node_w_out.inputs['Volume'])

# --- 2. Advanced PBR Hull Material ---
def create_advanced_hull_mat():
    mat = bpy.data.materials.new(name="Advanced_Hull")
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
    voronoi.distance = 'EUCLIDEAN'
    voronoi.inputs['Scale'].default_value = 15.0
    
    bump = nodes.new(type='ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.3
    
    links.new(tex_coord.outputs['Object'], voronoi.inputs['Vector'])
    links.new(voronoi.outputs['Distance'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], pbsdf.inputs['Normal'])
    
    # Roughness (Weathering)
    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 20.0
    links.new(noise.outputs['Fac'], pbsdf.inputs['Roughness'])
    
    # Window Emissive Layer
    brick = nodes.new(type='ShaderNodeTexBrick')
    brick.inputs['Scale'].default_value = 50.0
    brick.inputs['Mortar Size'].default_value = 0.02
    brick.inputs['Color1'].default_value = (0, 0, 0, 1)
    brick.inputs['Color2'].default_value = (1, 1, 1, 1) 
    
    mix_em = nodes.new(type='ShaderNodeMixRGB')
    mix_em.blend_type = 'MULTIPLY'
    mix_em.inputs['Color1'].default_value = (0.1, 0.8, 1.0, 1) 
    
    links.new(brick.outputs['Color'], mix_em.inputs['Fac'])
    links.new(mix_em.outputs['Color'], pbsdf.inputs['Emission Color'])
    pbsdf.inputs['Emission Strength'].default_value = 5.0
    
    links.new(pbsdf.outputs['BSDF'], output.inputs['Surface'])
    return mat

mat_hull = create_advanced_hull_mat()

# Engine Material
mat_engine = bpy.data.materials.new(name="Engine_Core")
mat_engine.use_nodes = True
e_nodes = mat_engine.node_tree.nodes
e_nodes.clear()
e_out = e_nodes.new(type='ShaderNodeOutputMaterial')
e_em = e_nodes.new(type='ShaderNodeEmission')
e_em.inputs['Color'].default_value = (1, 0.4, 0, 1)
e_em.inputs['Strength'].default_value = 50.0
mat_engine.node_tree.links.new(e_em.outputs['Emission'], e_out.inputs['Surface'])

# --- 3. Procedural Hull & Greebling ---
bpy.ops.mesh.primitive_cube_add(size=1.0)
obj = bpy.context.active_object
obj.name = "Advanced_Spaceship"
obj.data.materials.append(mat_hull)

bm = bmesh.new()
bm.from_mesh(obj.data)

# A. Hull Generation (The Spine)
bm.faces.ensure_lookup_table()
last_face = [f for f in bm.faces if f.normal.y > 0.9][0]
for i in range(8):
    res = bmesh.ops.extrude_discrete_faces(bm, faces=[last_face])
    last_face = res['faces'][0]
    y_move = random.uniform(0.8, 1.2)
    bmesh.ops.translate(bm, vec=(0, y_move, 0), verts=last_face.verts)
    s = random.uniform(0.6, 1.1)
    bmesh.ops.scale(bm, vec=(s, 1, s), verts=last_face.verts)
    bm.faces.ensure_lookup_table()

# B. Greeble Pass (Surface Detail) - SAFE VERSION
bm.faces.ensure_lookup_table()
target_indices = [f.index for f in bm.faces if random.random() > 0.7]

for idx in target_indices:
    bm.faces.ensure_lookup_table()
    if idx >= len(bm.faces): continue
    f = bm.faces[idx]
    if not f.is_valid: continue
    
    # Store normal
    f_normal = f.normal.copy()
    
    # Extrude
    res = bmesh.ops.extrude_discrete_faces(bm, faces=[f])
    g_face = res['faces'][0]
    
    # Translate along original normal
    depth = random.uniform(0.02, 0.15)
    bmesh.ops.translate(bm, vec=(f_normal * depth), verts=g_face.verts)
    # Scale
    bmesh.ops.scale(bm, vec=(0.8, 0.8, 0.8), verts=g_face.verts)

bm.to_mesh(obj.data)
bm.free()

# Symmetry Modifier
mod_mirror = obj.modifiers.new(name="Mirror", type='MIRROR')
mod_mirror.use_axis[0] = True 
mod_mirror.use_bisect_axis[0] = True

# Engine Objects
for x_off in [-0.5, 0.5]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=0.2, location=(x_off, -0.2, 0), rotation=(math.radians(90), 0, 0))
    engine_obj = bpy.context.active_object
    engine_obj.data.materials.append(mat_engine)
    engine_obj.parent = obj

# --- 4. Lighting & Camera ---
bpy.ops.object.light_add(type='SUN', location=(10, -10, 10))
bpy.context.active_object.data.energy = 8
bpy.ops.object.light_add(type='POINT', location=(-10, -5, 5))
bpy.context.active_object.data.energy = 2000
bpy.context.active_object.data.color = (0.7, 0.8, 1)
bpy.ops.object.light_add(type='POINT', location=(0, 15, 5))
bpy.context.active_object.data.energy = 4000

bpy.ops.object.camera_add(location=(12, -15, 8), rotation=(math.radians(65), 0, math.radians(40)))
bpy.context.scene.camera = bpy.context.active_object

output_path = os.path.expanduser('~/Project/gemini personality/personality/camera/advanced_spaceship_final_20260220.png')
bpy.context.scene.render.filepath = output_path
bpy.ops.render.render(write_still=True)
"""
    print("Initiating advanced procedural spaceship construction with PBR texturing...")
    return send_blender_command("execute_code", {"code": blender_code})

if __name__ == "__main__":
    res = generate_advanced_spaceship()
    print("Visual Cortex Response:", res)
