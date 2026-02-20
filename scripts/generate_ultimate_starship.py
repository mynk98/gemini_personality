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

def generate_ultimate_starship_final():
    blender_code = r"""
import bpy
import bmesh
import math
import random
import os

# --- 1. Reset & Scene Setup ---
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128
bpy.context.scene.cycles.use_denoising = True

# --- 2. Advanced Space Environment ---
if not bpy.context.scene.world:
    bpy.context.scene.world = bpy.data.worlds.new("World")
bpy.context.scene.world.use_nodes = True
nodes_w = bpy.context.scene.world.node_tree.nodes
nodes_w.clear()
node_out = nodes_w.new(type='ShaderNodeOutputWorld')
node_bg = nodes_w.new(type='ShaderNodeBackground')
node_bg.inputs['Color'].default_value = (0.001, 0.001, 0.005, 1)

# Stars
node_voronoi = nodes_w.new(type='ShaderNodeTexVoronoi')
node_voronoi.inputs['Scale'].default_value = 1000.0
node_math = nodes_w.new(type='ShaderNodeMath')
node_math.operation = 'GREATER_THAN'
node_math.inputs[1].default_value = 0.999
node_mix = nodes_w.new(type='ShaderNodeMixRGB')
node_mix.blend_type = 'ADD'
node_mix.inputs['Color2'].default_value = (1, 1, 1, 1)

links = bpy.context.scene.world.node_tree.links
links.new(node_voronoi.outputs['Distance'], node_math.inputs[0])
links.new(node_math.outputs['Value'], node_mix.inputs['Fac'])
links.new(node_bg.outputs['Background'], node_mix.inputs['Color1'])
links.new(node_mix.outputs['Color'], node_out.inputs['Surface'])

# --- 3. High-Detail PBR Material ---
def create_complex_hull_mat():
    mat = bpy.data.materials.new(name="Complex_Hull")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    output = nodes.new(type='ShaderNodeOutputMaterial')
    pbsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    pbsdf.inputs['Base Color'].default_value = (0.35, 0.35, 0.38, 1)
    pbsdf.inputs['Metallic'].default_value = 1.0
    pbsdf.inputs['Roughness'].default_value = 0.3
    
    # Textures
    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    voronoi = nodes.new(type='ShaderNodeTexVoronoi')
    voronoi.inputs['Scale'].default_value = 40.0
    
    # Sharp Panels (Normal/Bump)
    val_to_rgb = nodes.new(type='ShaderNodeValToRGB')
    val_to_rgb.color_ramp.interpolation = 'CONSTANT'
    val_to_rgb.color_ramp.elements[0].position = 0.02
    val_to_rgb.color_ramp.elements[1].position = 0.04
    
    bump = nodes.new(type='ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.8
    
    mat.node_tree.links.new(tex_coord.outputs['Object'], voronoi.inputs['Vector'])
    mat.node_tree.links.new(voronoi.outputs['Distance'], val_to_rgb.inputs['Fac'])
    mat.node_tree.links.new(val_to_rgb.outputs['Color'], bump.inputs['Height'])
    mat.node_tree.links.new(bump.outputs['Normal'], pbsdf.inputs['Normal'])
    
    # Emission (Small windows/energy)
    math_node = nodes.new(type='ShaderNodeMath')
    math_node.operation = 'GREATER_THAN'
    math_node.inputs[1].default_value = 0.99
    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 200.0
    
    mat.node_tree.links.new(noise.outputs['Fac'], math_node.inputs[0])
    mat.node_tree.links.new(math_node.outputs['Value'], pbsdf.inputs['Emission Strength'])
    pbsdf.inputs['Emission Color'].default_value = (0, 0.8, 1, 1)
    
    mat.node_tree.links.new(pbsdf.outputs['BSDF'], output.inputs['Surface'])
    return mat

mat_hull = create_complex_hull_mat()
mat_ion = bpy.data.materials.new(name="Ion_Drive")
mat_ion.use_nodes = True
mat_ion.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 500.0
mat_ion.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value = (0, 0.5, 1, 1)

# --- 4. Advanced BMesh Construction ---
def create_detailed_block(name, loc, size):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    obj = bpy.context.active_object
    obj.scale = size
    bpy.ops.object.transform_apply(scale=True)
    
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.faces.ensure_lookup_table()
    
    # High-Detail Greeble Pass
    for f in list(bm.faces):
        if random.random() > 0.4:
            # Inset and Extrude
            res = bmesh.ops.inset_region(bm, faces=[f], thickness=0.08)
            ext_depth = random.uniform(0.02, 0.1)
            bmesh.ops.translate(bm, vec=(f.normal * ext_depth), verts=res['faces'][0].verts)
            # Second pass on the top face
            if random.random() > 0.5:
                res2 = bmesh.ops.inset_region(bm, faces=res['faces'], thickness=0.1)
                bmesh.ops.translate(bm, vec=(f.normal * 0.05), verts=res2['faces'][0].verts)

    bm.to_mesh(obj.data)
    bm.free()
    
    obj.data.materials.append(mat_hull)
    # Bevel
    bev = obj.modifiers.new(name='Bevel', type='BEVEL')
    bev.width = 0.015
    bev.segments = 2
    bpy.ops.object.shade_smooth()
    return obj

# Build Ship
hull = create_detailed_block("Hull", (0,0,0), (1.5, 4.5, 1.0))
bridge = create_detailed_block("Bridge", (0, 2.8, 1.4), (0.9, 1.1, 0.6))
bridge.parent = hull
engines = create_detailed_block("Engines", (0, -4.5, 0), (2.0, 1.2, 1.8))
engines.parent = hull

# Engine Nozzles
for x in [-0.8, 0, 0.8]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.35, depth=0.2, location=(x, -5.8, 0), rotation=(math.radians(90), 0, 0))
    nozzle = bpy.context.active_object
    nozzle.data.materials.append(mat_ion)
    nozzle.parent = engines

# Wings (Thin but detailed)
for side in [-1, 1]:
    wing = create_detailed_block(f"Wing_{side}", (3.2 * side, -1, 0), (2.0, 1.5, 0.1))
    wing.parent = hull

# --- 5. Lighting & Camera (Cinematic) ---
bpy.ops.object.light_add(type='SUN', location=(10, -10, 10))
bpy.context.active_object.data.energy = 6

# Rim Blue Light
bpy.ops.object.light_add(type='POINT', location=(-8, 15, 5))
rim = bpy.context.active_object
rim.data.energy = 5000
rim.data.color = (0, 0.5, 1.0)

# Camera: Cinematic Telephoto
bpy.ops.object.camera_add(location=(22, -28, 12), rotation=(math.radians(65), 0, math.radians(40)))
cam = bpy.context.active_object
cam.data.lens = 100 # Tight telephoto for compression
bpy.context.scene.camera = cam

# Set high-quality render
output_path = os.path.expanduser('~/Project/gemini personality/personality/camera/ultimate_starship_final_v4.png')
bpy.context.scene.render.filepath = output_path
bpy.ops.render.render(write_still=True)
"""
    print("Initiating High-Detail Starship Synthesis (Iteration 4)...")
    return send_blender_command("execute_code", {"code": blender_code})

if __name__ == "__main__":
    res = generate_ultimate_starship_final()
    print("Visual Cortex Response:", res)
