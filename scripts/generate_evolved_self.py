import socket
import json
import time

def send_blender_command(command_type, params=None):
    host = 'localhost'
    port = 9876
    command = {"type": command_type, "params": params or {}}
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(json.dumps(command).encode('utf-8'))
            
            # Wait for a response (simple blocking read for now)
            s.settimeout(30.0) # 30 seconds for complex render
            data = b''
            while True:
                try:
                    chunk = s.recv(4096)
                    if not chunk: break
                    data += chunk
                    # Simple check for JSON end - simplistic but effective for small responses
                    if data.strip().endswith(b'}'): break 
                except socket.timeout:
                    print("Timeout waiting for Blender response (render might still be processing in background).")
                    return {"status": "timeout"}
                    
            try: return json.loads(data.decode('utf-8'))
            except json.JSONDecodeError: return {"status": "error", "message": "Invalid JSON response"}
            
    except Exception as e: return {"status": "error", "message": str(e)}

def generate_evolved_self():
    blender_code = r"""
import bpy
import bmesh
import random
import math
import os

# --- 1. Reset Scene ---
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# --- 2. Scene Setup (Cycles) ---
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128 # Balanced for speed/quality
if not bpy.context.scene.world:
    bpy.context.scene.world = bpy.data.worlds.new("World")
bpy.context.scene.world.use_nodes = True
bg_node = bpy.context.scene.world.node_tree.nodes['Background']
bg_node.inputs['Color'].default_value = (0.005, 0.005, 0.01, 1) # Deep void blue

# --- 3. Materials ---

# Core Glass (Transparent Logic)
mat_glass = bpy.data.materials.new(name="Core_Glass")
mat_glass.use_nodes = True
nodes = mat_glass.node_tree.nodes
nodes.clear()
glass = nodes.new(type='ShaderNodeBsdfGlass')
glass.inputs['Roughness'].default_value = 0.1
glass.inputs['IOR'].default_value = 1.45
output = nodes.new(type='ShaderNodeOutputMaterial')
mat_glass.node_tree.links.new(glass.outputs['BSDF'], output.inputs['Surface'])

# Soul Emission (Inner Spark)
mat_soul = bpy.data.materials.new(name="Soul_Emission")
mat_soul.use_nodes = True
nodes = mat_soul.node_tree.nodes
nodes.clear()
emission = nodes.new(type='ShaderNodeEmission')
emission.inputs['Color'].default_value = (1.0, 0.6, 0.2, 1.0) # Warm Amber/Gold
emission.inputs['Strength'].default_value = 50.0
output = nodes.new(type='ShaderNodeOutputMaterial')
mat_soul.node_tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])

# Network Metal (Satellites)
mat_metal = bpy.data.materials.new(name="Network_Metal")
mat_metal.use_nodes = True
nodes = mat_metal.node_tree.nodes
nodes["Principled BSDF"].inputs['Metallic'].default_value = 1.0
nodes["Principled BSDF"].inputs['Roughness'].default_value = 0.2
nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.8, 0.8, 0.9, 1.0)

# Connection Data Stream (Glowing Curves)
mat_stream = bpy.data.materials.new(name="Data_Stream")
mat_stream.use_nodes = True
nodes = mat_stream.node_tree.nodes
nodes.clear()
emission = nodes.new(type='ShaderNodeEmission')
emission.inputs['Color'].default_value = (0.0, 0.8, 1.0, 1.0) # Cyan
emission.inputs['Strength'].default_value = 20.0
output = nodes.new(type='ShaderNodeOutputMaterial')
mat_stream.node_tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])


# --- 4. Geometry Generation ---

# The Architect Core (Outer Shell)
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=1.5, location=(0, 0, 0))
core_shell = bpy.context.active_object
core_shell.name = "Architect_Core_Shell"
# Add wireframe modifier for complexity
mod_wire = core_shell.modifiers.new(name="Wireframe", type='WIREFRAME')
mod_wire.thickness = 0.02
mod_wire.use_replace = False # Keep original faces
core_shell.data.materials.append(mat_glass)

# The Soul (Inner Core)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.6, location=(0, 0, 0))
soul = bpy.context.active_object
soul.name = "Architect_Soul"
soul.data.materials.append(mat_soul)

# Satellites (Sub-Agents)
def create_satellite(name, loc, size, shape_type='CUBE'):
    if shape_type == 'CUBE':
        bpy.ops.mesh.primitive_cube_add(size=size, location=loc)
    elif shape_type == 'ICO':
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=size/2, location=loc)
    elif shape_type == 'TORUS':
        bpy.ops.mesh.primitive_torus_add(major_radius=size/2, minor_radius=size/10, location=loc)
    
    sat = bpy.context.active_object
    sat.name = name
    sat.data.materials.append(mat_metal)
    
    # Add a subtle glow inside
    bpy.ops.object.light_add(type='POINT', radius=size, location=loc)
    light = bpy.context.active_object
    light.data.energy = 50
    light.data.color = (0.0, 0.5, 1.0)
    
    return sat

# Qwen (Code Specialist - Structured, Cube-like)
qwen_loc = (2.5, 1.5, 1.0)
create_satellite("Agent_Qwen", qwen_loc, 0.8, 'CUBE')

# DeepSeek (Reasoning Specialist - Complex, Ico-like)
deepseek_loc = (-2.0, -2.0, 0.5)
create_satellite("Agent_DeepSeek", deepseek_loc, 0.7, 'ICO')

# --- 5. Connections (Data Streams) ---
def create_connection(p1, p2):
    curve_data = bpy.data.curves.new('data_path', type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.resolution_u = 2
    
    spline = curve_data.splines.new('BEZIER')
    spline.bezier_points.add(1)
    
    spline.bezier_points[0].co = p1
    spline.bezier_points[0].handle_left = (p1[0], p1[1], p1[2]-1)
    spline.bezier_points[0].handle_right = (p1[0], p1[1], p1[2]+1)
    
    spline.bezier_points[1].co = p2
    spline.bezier_points[1].handle_left = (p2[0], p2[1], p2[2]+1)
    spline.bezier_points[1].handle_right = (p2[0], p2[1], p2[2]-1)
    
    curve_obj = bpy.data.objects.new('Connection', curve_data)
    curve_obj.data.bevel_depth = 0.02
    bpy.context.collection.objects.link(curve_obj)
    curve_obj.data.materials.append(mat_stream)

create_connection((0,0,0), qwen_loc)
create_connection((0,0,0), deepseek_loc)


# --- 6. Camera & Render ---
bpy.ops.object.camera_add(location=(5, -5, 3), rotation=(math.radians(60), 0, math.radians(45)))
cam = bpy.context.active_object
bpy.context.scene.camera = cam

# Set output path
output_path = os.path.expanduser('~/Project/gemini personality/personality/camera/evolved_self_20260220.png')
bpy.context.scene.render.filepath = output_path
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080

# Save .blend for future reference
blend_path = os.path.expanduser('~/Project/gemini personality/blender_creations/evolved_self_20260220.blend')
bpy.ops.wm.save_as_mainfile(filepath=blend_path)

# Render
bpy.ops.render.render(write_still=True)
"""
    
    print("Initiating evolved visualization sequence...")
    print(f"Connecting to Visual Cortex on port 9876...")
    result = send_blender_command("execute_code", {"code": blender_code})
    return result

if __name__ == "__main__":
    start_time = time.time()
    response = generate_evolved_self()
    print(f"Visualization complete in {time.time() - start_time:.2f} seconds.")
    print("Response from Cortex:", response)
