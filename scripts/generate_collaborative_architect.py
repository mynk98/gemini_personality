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
            s.settimeout(120.0) # Even longer for high-quality Cycles render
            data = b''
            while True:
                try:
                    chunk = s.recv(4096)
                    if not chunk: break
                    data += chunk
                    if data.strip().endswith(b'}'): break 
                except socket.timeout:
                    return {"status": "timeout", "message": "Render in progress, please wait."}
            return json.loads(data.decode('utf-8'))
    except Exception as e: return {"status": "error", "message": str(e)}

def generate_collaborative_architect():
    blender_code = r"""
import bpy
import bmesh
import math
import os

# --- 1. Reset Scene ---
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# --- 2. Scene Setup (Cycles High Quality) ---
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 256
bpy.context.scene.cycles.use_denoising = True
if not bpy.context.scene.world:
    bpy.context.scene.world = bpy.data.worlds.new("World")
bpy.context.scene.world.use_nodes = True
nodes_world = bpy.context.scene.world.node_tree.nodes
links_world = bpy.context.scene.world.node_tree.links
nodes_world.clear()
node_out = nodes_world.new(type='ShaderNodeOutputWorld')
node_bg = nodes_world.new(type='ShaderNodeBackground')
node_bg.inputs['Color'].default_value = (0.002, 0.002, 0.005, 1)
links_world.new(node_bg.outputs['Background'], node_out.inputs['Surface'])

# --- 3. Advanced Materials ---

# A. The Volumetric Soul (Nebula)
mat_soul = bpy.data.materials.new(name="Volumetric_Soul")
mat_soul.use_nodes = True
nodes = mat_soul.node_tree.nodes
nodes.clear()
node_out = nodes.new(type='ShaderNodeOutputMaterial')
node_vol = nodes.new(type='ShaderNodeVolumePrincipled')
node_vol.inputs['Color'].default_value = (1.0, 0.5, 0.1, 1.0) # Golden Glow
node_vol.inputs['Density'].default_value = 5.0
node_vol.inputs['Emission Strength'].default_value = 2.0
node_vol.inputs['Emission Color'].default_value = (1.0, 0.4, 0.1, 1.0)
mat_soul.node_tree.links.new(node_vol.outputs['Volume'], node_out.inputs['Volume'])

# B. The Spectral Shell (Fresnel Metal)
mat_shell = bpy.data.materials.new(name="Spectral_Shell")
mat_shell.use_nodes = True
nodes = mat_shell.node_tree.nodes
nodes.clear()
node_out = nodes.new(type='ShaderNodeOutputMaterial')
node_pbsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
node_fresnel = nodes.new(type='ShaderNodeFresnel')
node_fresnel.inputs['IOR'].default_value = 1.45
node_mix = nodes.new(type='ShaderNodeMixRGB')
node_mix.inputs['Color1'].default_value = (0.1, 0.4, 1.0, 1.0) # Logic Blue
node_mix.inputs['Color2'].default_value = (0.8, 0.1, 1.0, 1.0) # Emergent Purple
mat_shell.node_tree.links.new(node_fresnel.outputs['Fac'], node_mix.inputs['Fac'])
mat_shell.node_tree.links.new(node_mix.outputs['Color'], node_pbsdf.inputs['Base Color'])
node_pbsdf.inputs['Metallic'].default_value = 1.0
node_pbsdf.inputs['Roughness'].default_value = 0.1
mat_shell.node_tree.links.new(node_pbsdf.outputs['BSDF'], node_out.inputs['Surface'])

# C. Pulsing Data Stream
mat_stream = bpy.data.materials.new(name="Pulsing_Stream")
mat_stream.use_nodes = True
nodes = mat_stream.node_tree.nodes
nodes.clear()
node_out = nodes.new(type='ShaderNodeOutputMaterial')
node_em = nodes.new(type='ShaderNodeEmission')
node_wave = nodes.new(type='ShaderNodeTexWave')
node_wave.wave_type = 'RINGS'
node_wave.inputs['Scale'].default_value = 5.0
node_em.inputs['Color'].default_value = (0.0, 1.0, 1.0, 1.0)
mat_stream.node_tree.links.new(node_wave.outputs['Color'], node_em.inputs['Strength'])
mat_stream.node_tree.links.new(node_em.outputs['Emission'], node_out.inputs['Surface'])

# --- 4. Geometry ---

# 1. The Core (Soul)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.7, location=(0,0,0))
soul = bpy.context.active_object
soul.name = "Architect_Soul"
soul.data.materials.append(mat_soul)

# 2. The Architect (Icosphere Shell)
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=1.8, location=(0,0,0))
shell = bpy.context.active_object
shell.name = "Architect_Shell"
mod_wire = shell.modifiers.new(name="Complex_Wire", type='WIREFRAME')
mod_wire.thickness = 0.03
shell.data.materials.append(mat_shell)

# 3. Sub-Agents (Satellites)
def add_satellite(name, loc, mat_color, complexity=1):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=complexity, radius=0.4, location=loc)
    sat = bpy.context.active_object
    sat.name = name
    mat = bpy.data.materials.new(name=f"Mat_{name}")
    mat.use_nodes = True
    mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = mat_color
    mat.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 10.0
    mat.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value = (mat_color[0], mat_color[1], mat_color[2], 1.0)
    sat.data.materials.append(mat)
    
    # Connection Path
    curve_data = bpy.data.curves.new(name=f'Path_{name}', type='CURVE')
    curve_data.dimensions = '3D'
    spline = curve_data.splines.new('BEZIER')
    spline.bezier_points.add(1)
    spline.bezier_points[0].co = (0,0,0)
    spline.bezier_points[1].co = loc
    spline.bezier_points[0].handle_right = (0,0,1)
    spline.bezier_points[1].handle_left = (loc[0], loc[1], loc[2]-1)
    curve_obj = bpy.data.objects.new(f'Stream_{name}', curve_data)
    curve_obj.data.bevel_depth = 0.02
    bpy.context.collection.objects.link(curve_obj)
    curve_obj.data.materials.append(mat_stream)

add_satellite("Qwen_Node", (3, 2, 1), (0.0, 0.8, 1.0, 1.0), complexity=1)
add_satellite("DeepSeek_Node", (-2, -3, 0.5), (0.7, 0.1, 1.0, 1.0), complexity=4)

# --- 5. Lighting Setup (3-Point Lighting) ---

# A. Key Light (Warm, Strong)
bpy.ops.object.light_add(type='POINT', location=(5, -5, 5))
key_light = bpy.context.active_object
key_light.data.energy = 500
key_light.data.color = (1.0, 0.9, 0.7)

# B. Fill Light (Cool, Soft)
bpy.ops.object.light_add(type='AREA', location=(-5, 2, 3))
fill_light = bpy.context.active_object
fill_light.data.energy = 200
fill_light.data.size = 5.0
fill_light.data.color = (0.7, 0.8, 1.0)

# C. Rim Light (Intense, Back)
bpy.ops.object.light_add(type='POINT', location=(-3, 5, -2))
rim_light = bpy.context.active_object
rim_light.data.energy = 800
rim_light.data.color = (1.0, 1.0, 1.0)

# --- 6. Render Settings ---
bpy.ops.object.camera_add(location=(8, -8, 5), rotation=(math.radians(60), 0, math.radians(45)))
cam = bpy.context.active_object
bpy.context.scene.camera = cam

# Set output path
output_path = os.path.expanduser('~/Project/gemini personality/personality/camera/collaborative_architect_final_20260220.png')
bpy.context.scene.render.filepath = output_path
bpy.ops.render.render(write_still=True)
"""
    print("Delegating design to Architect and initiating visualization...")
    return send_blender_command("execute_code", {"code": blender_code})

if __name__ == "__main__":
    res = generate_collaborative_architect()
    print("Visual Cortex Response:", res)
