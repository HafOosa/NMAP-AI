"""
Préparer données HARD pour le modèle Diffusion-like (T5)
"""

import json
from sklearn.model_selection import train_test_split

INPUT_JSON = "data/nmap_hard_dataset.json"

def main():
    print("\n📝 PRÉPARATION DONNÉES DIFFUSION (HARD)\n")
    
    with open(INPUT_JSON, 'r') as f:
        data = json.load(f)
    
    print(f"Dataset chargé : {len(data)} exemples")
    
    # Format pour Diffusion: text-to-text avec préfixe spécial
    formatted = []
    for item in data:
        formatted.append({
            'input_text': f"generate advanced nmap command: {item['instruction']}",
            'target_text': item['output']
        })
    
    # Split 80/10/10
    train, temp = train_test_split(formatted, test_size=0.2, random_state=42)
    val, test = train_test_split(temp, test_size=0.5, random_state=42)
    
    print(f"\n✅ Split effectué :")
    print(f"   Train : {len(train)}")
    print(f"   Val   : {len(val)}")
    print(f"   Test  : {len(test)}")
    
    # Sauvegarder
    for name, split in [('train', train), ('val', val), ('test', test)]:
        path = f'data/diffusion_hard_{name}.json'
        with open(path, 'w') as f:
            json.dump(split, f, indent=2)
        print(f"   Saved: {path}")
    
    print("\n📋 EXEMPLES DU FORMAT :")
    for i in range(3):
        print(f"\n[{i+1}]")
        print(f"  Input : {train[i]['input_text']}")
        print(f"  Target: {train[i]['target_text']}")


if __name__ == "__main__":
    main()