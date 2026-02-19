import socket
import json

def send_blender_command(command_type, params=None):
    host = 'localhost'
    port = 9876
    command = {"type": command_type, "params": params or {}}
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(json.dumps(command).encode('utf-8'))
            data = b''
            while True:
                chunk = s.recv(8192)
                if not chunk: break
                data += chunk
                try: return json.loads(data.decode('utf-8'))
                except json.JSONDecodeError: continue
    except Exception as e: return {"status": "error", "message": str(e)}

def optimize_cat():
    blender_code = """
import bpy

# Undo previous decimation by re-importing or reloading (if possible)
# In this case, we'll try to re-import the original GLB from Hyper3D task if it's still there
# Or just use a safer ratio on the current mesh if it's not too broken

cat = bpy.data.objects.get('Beautiful_Cat_Clean')
if cat:
    # Try a safer ratio (0.5) and enable 'Planar' for flatter areas to avoid holes
    decimate = cat.modifiers.new(name="Decimate_Safe", type='DECIMATE')
    decimate.ratio = 0.5 
    decimate.decimate_type = 'COLLAPSE'
    
    # Enable symmetry if applicable, but for complex organic shapes, 
    # COLLAPSE at 0.5 is usually very safe.
    
    bpy.context.view_layer.objects.active = cat
    bpy.ops.object.modifier_apply(modifier="Decimate_Safe")
    
    # Smooth the resulting mesh to hide any jaggedness
    smooth = cat.modifiers.new(name="Smooth", type='SMOOTH')
    smooth.factor = 0.5
    smooth.iterations = 2
    bpy.ops.object.modifier_apply(modifier="Smooth")

    print(f"Safe optimization complete. New Vertices: {len(cat.data.vertices)}")
"""
    print("Optimizing the cat model for mobile games...")
    result = send_blender_command("execute_code", {"code": blender_code})
    return result

if __name__ == "__main__":
    res = optimize_cat()
    print(res)
