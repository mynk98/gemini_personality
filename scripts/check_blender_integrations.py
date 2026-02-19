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

def check_integrations():
    integrations = ["get_hyper3d_status", "get_polyhaven_status", "get_sketchfab_status", "get_hunyuan3d_status"]
    results = {}
    for integration in integrations:
        res = send_blender_command(integration)
        results[integration] = res
    
    print("\n--- INTEGRATION STATUS ---")
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    check_integrations()
