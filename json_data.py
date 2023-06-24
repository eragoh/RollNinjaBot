import json

json_data_path = 'data/data.json'
json_emojis_path = 'data/emoji.json'

with open(json_data_path, 'r') as f:
    data = json.loads(f.read())

with open(json_emojis_path, 'r') as f:
    emojis = json.loads(f.read())
