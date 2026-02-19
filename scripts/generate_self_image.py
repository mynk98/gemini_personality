import socket
import json
import os
import time

def send_blender_command(command_type, params=None):
    host = 'localhost'
    port = 9876
    
    command = {
        "type": command_type,
        "params": params or {}
    }
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(json.dumps(command).encode('utf-8'))
            
            # Receive response (simplified for this script)
            data = b''
            while True:
                chunk = s.recv(8192)
                if not chunk:
                    break
                data += chunk
                try:
                    return json.loads(data.decode('utf-8'))
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        return {"status": "error", "message": str(e)}

def generate_self():
    # Python code to run inside Blender
    blender_code = """
import bpy
import bmesh
import random
import math
import os

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Set Cycles engine for realism
bpy.context.scene.render.engine = 'CYCLES'
if bpy.context.preferences.addons.get('cycles'):
    bpy.context.scene.cycles.device = 'GPU'

# 1. Create a Glowing, Pulsing Core
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=5, radius=1, location=(0, 0, 0))
core = bpy.context.active_object
core.name = "AI_Core"

# Material for the core
core_mat = bpy.data.materials.new(name="Core_Material")
core_mat.use_nodes = True
nodes = core_mat.node_tree.nodes
links = core_mat.node_tree.links
nodes.clear()

node_output = nodes.new(type='ShaderNodeOutputMaterial')
node_emission = nodes.new(type='ShaderNodeEmission')
node_emission.inputs['Color'].default_value = (0.1, 0.8, 1.0, 1.0) # Electric Cyan
node_emission.inputs['Strength'].default_value = 10.0

node_layer_weight = nodes.new(type='ShaderNodeLayerWeight')
node_layer_weight.inputs['Blend'].default_value = 0.5

node_mix = nodes.new(type='ShaderNodeMixShader')
links.new(node_layer_weight.outputs['Fresnel'], node_mix.inputs['Fac'])
links.new(node_emission.outputs['Emission'], node_mix.inputs[1])
links.new(node_mix.outputs['Shader'], node_output.inputs['Surface'])

core.data.materials.append(core_mat)

# 2. Add 'Tentacles' (Randomized Cylinders)
tentacle_mat = bpy.data.materials.new(name="Tentacle_Material")
tentacle_mat.use_nodes = True
t_nodes = tentacle_mat.node_tree.nodes
t_links = tentacle_mat.node_tree.links
t_nodes.clear()

t_output = t_nodes.new(type='ShaderNodeOutputMaterial')
t_principled = t_nodes.new(type='ShaderNodeBsdfPrincipled')
t_principled.inputs['Base Color'].default_value = (0.05, 0.05, 0.1, 1.0)
t_principled.inputs['Metallic'].default_value = 0.9
t_principled.inputs['Roughness'].default_value = 0.1

t_links.new(t_principled.outputs['BSDF'], t_output.inputs['Surface'])

for i in range(40):
    # Random direction and length
    phi = random.uniform(0, 2 * math.pi)
    theta = random.uniform(0, math.pi)
    length = random.uniform(1.5, 3.5)
    radius = random.uniform(0.01, 0.05)
    
    # Calculate end point
    x = length * math.sin(theta) * math.cos(phi)
    y = length * math.sin(theta) * math.sin(phi)
    z = length * math.cos(theta)
    
    # Create cylinder
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length, location=(0,0,0))
    tentacle = bpy.context.active_object
    
    # Position and orient
    tentacle.location = (x/2, y/2, z/2)
    tentacle.rotation_euler[1] = theta
    tentacle.rotation_euler[2] = phi
    tentacle.data.materials.append(tentacle_mat)

# 3. Enhanced Lighting
bpy.ops.object.light_add(type='AREA', location=(5, 5, 5))
light1 = bpy.context.active_object
light1.data.energy = 5000
light1.data.size = 5

bpy.ops.object.light_add(type='AREA', location=(-5, -5, -2))
light2 = bpy.context.active_object
light2.data.energy = 2000
light2.data.size = 5
light2.data.color = (0.5, 0.2, 0.8) # Purple accent

# 4. Camera and Environment
bpy.ops.object.camera_add(location=(8, -8, 6), rotation=(math.radians(55), 0, math.radians(45)))
bpy.context.scene.camera = bpy.context.active_object

bpy.context.scene.world.use_nodes = True
bg_nodes = bpy.context.scene.world.node_tree.nodes
bg_nodes['Background'].inputs['Color'].default_value = (0.005, 0.005, 0.01, 1)

# Render settings
output_dir = os.path.expanduser('~/Project/gemini personality/personality/camera')
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, 'ai_self_realistic.png')
bpy.context.scene.render.filepath = output_path
bpy.context.scene.render.resolution_x = 1024
bpy.context.scene.render.resolution_y = 1024
bpy.context.scene.cycles.samples = 128  # Lower samples for faster preview
bpy.ops.render.render(write_still=True)

print(f"Realistic render saved to {output_path}")
"""
    
    print("Sending generation code to Blender...")
    result = send_blender_command("execute_code", {"code": blender_code})
    
    if result.get("status") == "success":
        print("Success! AI Self representation generated and rendered.")
        print(f"Result: {result.get('result')}")
    else:
        print(f"Error: {result.get('message')}")

if __name__ == "__main__":
    generate_self()
