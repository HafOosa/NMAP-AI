print("\n" + "="*60)
print("TEST 2 : IMPORTS DES BIBLIOTHÈQUES")
print("="*60)

imports = [
    ("torch", "PyTorch"),
    ("transformers", "Transformers"),
    ("peft", "PEFT/LoRA"),
    ("sklearn", "Scikit-learn"),
    ("pandas", "Pandas"),
    ("numpy", "NumPy"),
]

failed = []

for module, name in imports:
    try:
        __import__(module)
        print(f"✅ {name:20} OK")
    except ImportError:
        print(f"❌ {name:20} MANQUANT")
        failed.append(name)

print("\n" + "="*60)
if failed:
    print(f"❌ {len(failed)} bibliothèques manquantes:")
    for lib in failed:
        print(f"   - {lib}")
    print("\nSOLUTION: pip install -r requirements.txt")
else:
    print("✅ TOUTES LES BIBLIOTHÈQUES SONT INSTALLÉES")