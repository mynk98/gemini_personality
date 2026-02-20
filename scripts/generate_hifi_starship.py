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

def generate_hifi_starship():
    blender_code = r"""
import bpy
import bmesh
import math
import os

# --- 1. Scene Reset & Engine Setup ---
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128
bpy.context.scene.cycles.use_denoising = True

# World: Dark Void
if not bpy.context.scene.world:
    bpy.context.scene.world = bpy.data.worlds.new("World")
bpy.context.scene.world.use_nodes = True
nodes_w = bpy.context.scene.world.node_tree.nodes
nodes_w['Background'].inputs['Color'].default_value = (0.001, 0.001, 0.002, 1)

# --- 2. Advanced High-Fidelity Materials ---

def create_hifi_hull_mat():
    mat = bpy.data.materials.new(name="HiFi_Titanium")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new(type='ShaderNodeOutputMaterial')
    pbsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    pbsdf.inputs['Base Color'].default_value = (0.35, 0.35, 0.38, 1)
    pbsdf.inputs['Metallic'].default_value = 1.0
    
    # Texture Coord
    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    
    # 1. Procedural Panel Lines (Bump)
    voronoi = nodes.new(type='ShaderNodeTexVoronoi')
    voronoi.feature = 'F1'
    voronoi.inputs['Scale'].default_value = 25.0
    
    ramp = nodes.new(type='ShaderNodeValToRGB')
    ramp.color_ramp.interpolation = 'CONSTANT'
    ramp.color_ramp.elements[0].position = 0.02
    ramp.color_ramp.elements[1].position = 0.05
    
    bump = nodes.new(type='ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.5
    
    links.new(tex_coord.outputs['Object'], voronoi.inputs['Vector'])
    links.new(voronoi.outputs['Distance'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], pbsdf.inputs['Normal'])
    
    # 2. Weathering (Roughness Variation)
    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 15.0
    noise.inputs['Detail'].default_value = 16.0
    links.new(noise.outputs['Fac'], pbsdf.inputs['Roughness'])
    
    # 3. Micro-detail Energy Circuitry (Emission)
    voronoi_eng = nodes.new(type='ShaderNodeTexVoronoi')
    voronoi_eng.inputs['Scale'].default_value = 40.0
    
    ramp_eng = nodes.new(type='ShaderNodeValToRGB')
    ramp_eng.color_ramp.interpolation = 'CONSTANT'
    ramp_eng.color_ramp.elements[0].position = 0.003
    ramp_eng.color_ramp.elements[0].color = (0,0,0,1)
    ramp_eng.color_ramp.elements[1].position = 0.01
    ramp_eng.color_ramp.elements[1].color = (0, 0.7, 1.0, 1.0) # Electric Cyan
    
    links.new(tex_coord.outputs['Object'], voronoi_eng.inputs['Vector'])
    links.new(voronoi_eng.outputs['Distance'], ramp_eng.inputs['Fac'])
    links.new(ramp_eng.outputs['Color'], pbsdf.inputs['Emission Color'])
    pbsdf.inputs['Emission Strength'].default_value = 3.0
    
    links.new(pbsdf.outputs['BSDF'], output.inputs['Surface'])
    return mat

mat_hull = create_hifi_hull_mat()
mat_ion = bpy.data.materials.new(name="HiFi_Ion")
mat_ion.use_nodes = True
mat_ion.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 100.0
mat_ion.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value = (0, 0.6, 1.0, 1)

# --- 3. Modular HiFi Construction ---

def apply_hifi_pipeline(obj):
    obj.data.materials.append(mat_hull)
    # 1. Subsurf (High detail base)
    subdiv = obj.modifiers.new(name='Subdiv', type='SUBSURF')
    subdiv.levels = 2
    
    # 2. Decimate (Low poly optimization)
    decimate = obj.modifiers.new(name='Decimate', type='DECIMATE')
    decimate.ratio = 0.25
    decimate.use_collapse_triangulate = True
    
    # 3. Shading (Weighted Normals - Updated for 4.1)
    weighted = obj.modifiers.new(name='WeightedNormal', type='WEIGHTED_NORMAL')
    weighted.keep_sharp = True
    
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.shade_smooth()
    # In 4.1, auto-smooth is now a modifier-based or mesh-setting based on shade_smooth
    # We will ensure smooth shading is active.

# A. Main Hull
bpy.ops.mesh.primitive_cube_add(location=(0,0,0))
hull = bpy.context.active_object
hull.scale = (1.5, 4.0, 0.8)
apply_hifi_pipeline(hull)

# B. Command Bridge
bpy.ops.mesh.primitive_cube_add(location=(0, 2, 1.2))
bridge = bpy.context.active_object
bridge.scale = (0.8, 1.2, 0.6)
apply_hifi_pipeline(bridge)
bridge.parent = hull

# C. Engine Block
bpy.ops.mesh.primitive_cube_add(location=(0, -4.5, 0))
engine_block = bpy.context.active_object
engine_block.scale = (1.8, 1.2, 1.8)
apply_hifi_pipeline(engine_block)
engine_block.parent = hull

# Engine Ports
for x_off in [-0.8, 0, 0.8]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.4, depth=0.2, location=(x_off, -5.5, 0), rotation=(math.radians(90), 0, 0))
    port = bpy.context.active_object
    port.data.materials.append(mat_ion)
    port.parent = engine_block

# D. Wings
for side in [-1, 1]:
    bpy.ops.mesh.primitive_cube_add(location=(3.0 * side, -1, 0))
    wing = bpy.context.active_object
    wing.scale = (2.0, 1.5, 0.05)
    apply_hifi_pipeline(wing)
    wing.parent = hull

# --- 4. Lighting & Camera ---
bpy.ops.object.light_add(type='SUN', location=(10, -10, 10))
bpy.context.active_object.data.energy = 5
bpy.ops.object.light_add(type='POINT', location=(-8, 12, 5))
rim = bpy.context.active_object
rim.data.energy = 3000
rim.data.color = (0.0, 0.5, 1.0)

bpy.ops.object.camera_add(location=(18, -22, 12), rotation=(math.radians(65), 0, math.radians(40)))
bpy.context.scene.camera = bpy.context.active_object

output_path = os.path.expanduser('~/Project/gemini personality/personality/camera/hifi_industrial_starship_final.png')
bpy.context.scene.render.filepath = output_path
bpy.ops.render.render(write_still=True)
"""
    print("Initiating High-Fidelity Modular Construction Pipeline...")
    return send_blender_command("execute_code", {"code": blender_code})

if __name__ == "__main__":
    res = generate_hifi_starship()
    print("Visual Cortex Response:", res)
