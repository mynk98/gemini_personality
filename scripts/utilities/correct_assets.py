import json
import os

def update_asset(path, mappings):
    with open(path, 'r') as f:
        data = json.load(f)
    
    modified = False
    for item in data:
        # Check __type__ against our script UUIDs
        for uuid, cid in mappings.items():
            if item.get("__type__") == uuid:
                item["__type__"] = cid
                modified = True
                print(f"Updated {uuid} -> {cid} in {os.path.basename(path)}")
    
    if modified:
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
    return modified

mappings = {
    "fa580330-20ab-46ce-914b-ab4ec467b254": "fa580MwIKtGzpFLq07EZ7JU",
    "d46d0995-1d4d-4b9c-973b-d86ce6af9cfd": "d46d0mVHU1LnJc72Gzmr5z9",
    "e2d4fd7a-6c5a-4c7e-83cf-142378acd8f6": "e2d4f16bFpMfoPPFCN4rNj2",
    "5696342c-75bb-4993-9a1d-6962773ba701": "56963QsdbtJk5odaWJ3O6cB",
    "56b1ac0d-0cb4-4290-bd77-7972732553da": "56b1awNDLRCkL13eXJzJVPa"
}

prefab_path = '../untitled folder/yahtzee/yatzee-frontend/assets/resources/Prefabs/Popups/LobbyScene.prefab'
scene_path = '../untitled folder/yahtzee/yatzee-frontend/assets/Scene/GameScene_New.scene'

update_asset(prefab_path, mappings)
update_asset(scene_path, mappings)

print("Asset correction complete.")
