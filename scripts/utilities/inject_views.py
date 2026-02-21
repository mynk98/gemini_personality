import json
import os

path = '../untitled folder/yahtzee/yatzee-frontend/assets/resources/Prefabs/Popups/LobbyScene.prefab'
with open(path, 'r') as f:
    data = json.load(f)

def add_component(node_idx, script_uuid):
    new_idx = len(data)
    # Create component entry
    comp_obj = {
        "__type__": script_uuid,
        "_name": "",
        "_objFlags": 0,
        "__editorExtras__": {},
        "node": {
            "__id__": node_idx
        },
        "_enabled": true
    }
    data.append(comp_obj)
    # Update node's components list
    if "_components" not in data[node_idx]:
        data[node_idx]["_components"] = []
    data[node_idx]["_components"].append({"__id__": new_idx})
    print(f"Added {script_uuid} to node index {node_idx} at new index {new_idx}")

# Python boolean conversion
true = True
false = False

# 1. LobbyMainView -> LobbyScene (1)
add_component(1, "fa580330-20ab-46ce-914b-ab4ec467b254")

# 2. LobbyHUDView -> Hud (11)
add_component(11, "d46d0995-1d4d-4b9c-973b-d86ce6af9cfd")

# 3. LobbyWorldView -> Text_WorldCount (55)
add_component(55, "e2d4fd7a-6c5a-4c7e-83cf-142378acd8f6")

# 4. LobbyLevelProgressView -> LevelCounter (63)
add_component(63, "5696342c-75bb-4993-9a1d-6962773ba701")

with open(path, 'w') as f:
    json.dump(data, f, indent=2)

print("Prefab updated successfully.")
