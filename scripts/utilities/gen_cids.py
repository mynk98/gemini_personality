import base64

def cocos_compress_uuid(uuid_str):
    # Standard Cocos Creator 3.x UUID compression
    # Reference: https://github.com/cocos/cocos-engine/blob/develop/cocos/core/utils/uuid-utils.ts
    
    u = uuid_str.replace('-', '')
    if len(u) != 32:
        return uuid_str
    
    # Prefix: first 5 chars are kept
    prefix = u[:5]
    
    # Remaining 27 hex chars
    # We need to process bits. 
    # Cocos uses a 23-character format for compressed UUIDs.
    # The first 5 characters are the same as the hex UUID.
    # The rest are base64 encoded.
    
    # Let's try the DataJsons example:
    # 4ea80471-ad0f-4bd3-a509-abc70038903a 
    # -> 4ea80RxrQ9L06UJq8cAOJA6
    
    # Observed mapping:
    # 4ea80 (5 chars) matches.
    # Remaining: 471ad0f4bd3a509abc70038903a (27 hex chars = 108 bits)
    # Target tail: RxrQ9L06UJq8cAOJA6 (18 chars)
    # 18 chars * 6 bits/char = 108 bits. MATCH!
    
    BASE64_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    
    remaining_hex = u[5:]
    # Convert hex to integer
    val = int(remaining_hex, 16)
    
    # Convert to 18 base64 characters
    encoded = ""
    for _ in range(18):
        encoded = BASE64_CHARS[val & 0x3F] + encoded
        val >>= 6
        
    return prefix + encoded

# Verify with DataJsons
test_uuid = "4ea80471-ad0f-4bd3-a509-abc70038903a"
print(f"Test UUID: {test_uuid}")
print(f"Result CID: {cocos_compress_uuid(test_uuid)}")
print(f"Target CID: 4ea80RxrQ9L06UJq8cAOJA6")

# Generate for our views
views = {
    "LobbyMainView": "fa580330-20ab-46ce-914b-ab4ec467b254",
    "LobbyHUDView": "d46d0995-1d4d-4b9c-973b-d86ce6af9cfd",
    "LobbyWorldView": "e2d4fd7a-6c5a-4c7e-83cf-142378acd8f6",
    "LobbyLevelProgressView": "5696342c-75bb-4993-9a1d-6962773ba701",
    "GameScene": "56b1ac0d-0cb4-4290-bd77-7972732553da"
}

for name, u in views.items():
    print(f"{name}: {cocos_compress_uuid(u)}")
