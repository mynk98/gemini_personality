import json
import os

path = '../untitled folder/yahtzee/yatzee-frontend/assets/Scene/GameScene_New.scene'
with open(path, 'r') as f:
    data = json.load(f)

def add_gamescene_comp(node_idx, script_uuid, lobby_parent_idx):
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
        "_enabled": True,
        "lobbyParent": {
            "__id__": lobby_parent_idx
        },
        "gameSubSceneParent": None,
        "dataJsons": None
    }
    data.append(comp_obj)
    # Update node's components list
    if "_components" not in data[node_idx]:
        data[node_idx]["_components"] = []
    data[node_idx]["_components"].append({"__id__": new_idx})
    print(f"Added {script_uuid} to node index {node_idx} at new index {new_idx}")

# 1. GameScene script UUID
game_scene_uuid = "56b1ac0d-0cb4-4290-bd77-7972732553da"

# 2. Add to GameScene node (218) linking to LobbyScene_Instance (50)
add_gamescene_comp(218, game_scene_uuid, 50)

with open(path, 'w') as f:
    json.dump(data, f, indent=2)

print("Scene updated successfully.")
