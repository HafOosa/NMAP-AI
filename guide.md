@"
# 🤖 AGENTS MEDIUM & HARD

## 🎯 OBJECTIF DE CETTE PARTIE

Développer deux agents d'IA capables de générer automatiquement des commandes Nmap à partir de langage naturel :

- **Agent MEDIUM** : Requêtes moyennes (scans de ports, détection OS/services)
- **Agent HARD** : Requêtes complexes (évasion IDS/Firewall, techniques avancées)

---

## 📁 FICHIERS DE MA PARTIE

\`\`\`
agents/
├── generator_medium_agent.py       ← Agent MEDIUM
├── generator_hard_agent.py         ← Agent HARD
├── command_processor.py            ← Post-processing MEDIUM
└── hard_command_processor.py       ← Post-processing HARD

data/
├── nmap_balanced.json              ← Dataset MEDIUM (3000)
├── nmap_hard_dataset.json          ← Dataset HARD (1700)
├── t5_balanced_train.json          ← Training MEDIUM
├── t5_balanced_val.json            ← Validation MEDIUM
├── t5_balanced_test.json           ← Test MEDIUM
├── diffusion_hard_train.json       ← Training HARD
├── diffusion_hard_val.json         ← Validation HARD
└── diffusion_hard_test.json        ← Test HARD

models/
├── medium_models/                  ← Modèle MEDIUM (~3 MB)
│   ├── adapter_config.json
│   ├── adapter_model.safetensors
│   └── tokenizer files...
└── hard_models/                    ← Modèle HARD (~30 MB)
    ├── adapter_config.json
    ├── adapter_model.safetensors
    └── tokenizer files...

training/
├── create_balanced_dataset.py      ← Génération dataset MEDIUM
├── prepare_balanced_t5.py          ← Préparation MEDIUM
├── train_medium_optimized.py       ← Entraînement MEDIUM
├── create_hard_dataset.py          ← Génération dataset HARD
├── prepare_hard_data.py            ← Préparation HARD
└── train_hard_diffusion.py         ← Entraînement HARD

tests/
├── test_medium.py                  ← Tests MEDIUM (10 tests)
└── test_hard.py                    ← Tests HARD (10 tests)
\`\`\`

---

## 🚀 INSTALLATION & UTILISATION

### 1. Installation des dépendances

\`\`\`bash
pip install torch transformers peft datasets scikit-learn pandas numpy
\`\`\`

### 2. Tests

\`\`\`bash
# Test Agent MEDIUM
python tests/test_medium.py

# Test Agent HARD
python tests/test_hard.py
\`\`\`

---

## 🔬 MÉTHODOLOGIE

### 1. Préparation des Datasets

#### Agent MEDIUM
\`\`\`bash
# Génération de 3000 exemples équilibrés
python training/create_balanced_dataset.py
\`\`\`

#### Agent HARD
\`\`\`bash
# Génération de 1700 exemples d'évasion
python training/create_hard_dataset.py
\`\`\`

---

### 2. Fine-tuning avec LoRA

**Pourquoi LoRA ?**
- ✅ 99% moins de paramètres à entraîner
- ✅ 99% moins d'espace disque
- ✅ 95% plus rapide
- ✅ Même performance que full fine-tuning

**Architecture LoRA :**

**Agent MEDIUM :**
- Base : T5-small (60M paramètres)
- LoRA : 589K paramètres (0.96%)

**Agent HARD :**
- Base : T5-base (220M paramètres)
- LoRA : 7M paramètres (3.08%)

---

### 3. Entraînement

#### Agent MEDIUM
\`\`\`bash
# Préparation
python training/prepare_balanced_t5.py

# Entraînement
python training/train_medium_optimized.py

# Paramètres :
# - Epochs : 5
# - Batch size : 8
# - Learning rate : 2e-4
\`\`\`

#### Agent HARD
\`\`\`bash
# Préparation
python training/prepare_hard_data.py

# Entraînement
python training/train_hard_diffusion.py

# Paramètres :
# - Epochs : 8
# - Batch size : 4
# - Learning rate : 3e-4
\`\`\`
"@ | Out-File -FilePath "README_AGENTS.md" -Encoding UTF8

Write-Host "✅ README_AGENTS.md créé" -ForegroundColor Green