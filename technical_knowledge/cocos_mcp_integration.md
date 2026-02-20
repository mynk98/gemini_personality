# Cocos MCP Integration

## Connection Details
- **Endpoint:** `http://localhost:3001/mcp`
- **Protocol:** JSON-RPC 2.0 over HTTP POST
- **Headers:** `Content-Type: application/json`

## Discovery History
- The root `http://localhost:3001/` returns 404.
- The standard MCP discovery method is `tools/list` on the `/mcp` path.

## Primary Tools
### Scene Management
- `scene_get_current_scene`: Get active scene name and UUID.
- `scene_get_scene_hierarchy`: Retrieve full node tree (use `{"includeComponents": true}` for detail).
- `scene_open_scene`: Open scene by path.
- `scene_save_scene`: Save current state.

### Node Manipulation
- `node_get_all_nodes`: List all nodes in hierarchy.
- `node_get_node_info`: Get specific node details by UUID.
- `node_set_node_transform`: Update position, rotation, or scale.
- `node_create_node`: Instantiate new nodes or prefabs.

### Debug & Project
- `debug_get_console_logs`: Fetch editor logs.
- `project_get_project_info`: Get project-level metadata.

## Usage Pattern
Always use `curl` or an HTTP client to POST JSON-RPC payloads to the `/mcp` endpoint.
Example:
```bash
curl -X POST -H "Content-Type: application/json" 
  -d '{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "scene_get_current_scene", "arguments": {}}, "id": 1}' 
  http://localhost:3001/mcp
```
