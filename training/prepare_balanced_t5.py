# training/prepare_balanced_t5.py
import json
from sklearn.model_selection import train_test_split

with open('data/nmap_balanced.json', 'r') as f:
    data = json.load(f)

# Formater pour T5
formatted = []
for item in data:
    formatted.append({
        'input_text': f"translate to nmap: {item['instruction']}",
        'target_text': item['output']
    })

# Split
train, temp = train_test_split(formatted, test_size=0.2, random_state=42)
val, test = train_test_split(temp, test_size=0.5, random_state=42)

# Sauvegarder
for name, split in [('train', train), ('val', val), ('test', test)]:
    with open(f'data/t5_balanced_{name}.json', 'w') as f:
        json.dump(split, f, indent=2)

print(f"Train: {len(train)} | Val: {len(val)} | Test: {len(test)}")