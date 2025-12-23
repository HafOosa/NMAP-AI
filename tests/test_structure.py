import os

print("\n" + "="*60)
print("TEST 1 : STRUCTURE DES FICHIERS")
print("="*60)

# Fichiers essentiels à vérifier
files = [
    "agents/command_processor.py",
    "agents/generator_medium_agent.py",
    "agents/generator_hard_agent.py",
    "data/nmap_dataset.json",
    "data/nmap_balanced.json",
    "data/t5_balanced_train.json",
    "models/medium_models/adapter_config.json",
    "training/create_balanced_dataset.py",
    "training/train_medium_optimized.py",
    "tests/test_medium.py",
    "requirements.txt"
]

missing = []
present = []

for f in files:
    if os.path.exists(f):
        present.append(f)
        print(f"✅ {f}")
    else:
        missing.append(f)
        print(f"❌ {f} MANQUANT")

print("\n" + "="*60)
if missing:
    print(f"❌ {len(missing)} fichiers manquants")
    for f in missing:
        print(f"   - {f}")
else:
    print("✅ TOUS LES FICHIERS SONT PRÉSENTS")