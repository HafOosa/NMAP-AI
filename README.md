# NMAP-AI : Générateur de Commandes Nmap Basé sur l'IA

## Table des matières

1. [Introduction](#introduction)
2. [Objectifs](#objectifs)
3. [Répartition des Tâches](#répartition-des-tâches)
4. [Technologies Utilisées](#technologies-utilisées)
5. [Modules et Fonctionnalités](#modules-et-fonctionnalités)
   - [Personne 1 : Imane Allioui](#personne-1-imane-allioui)
   - [Personne 2 : Chaimae Ababri](#personne-2-chaimae-ababri)
   - [Personne 3 : Rami Hala](#personne-3-rami-hala)
   - [Personne 4 : Habib Samia](#personne-4-habib-samia)
   - [Personne 5 : El Guallaf Hafssa](#personne-5-el-guallaf-hafssa)
6. [Installation et Utilisation](#installation-et-utilisation)
7. [Résultats et Évaluation](#résultats-et-évaluation)
8. [Avenir et Améliorations](#avenir-et-améliorations)

## Introduction

Le projet **NMAP-AI** a pour objectif de simplifier l’utilisation de **Nmap**, un outil de sécurité réseau, en permettant de générer automatiquement des commandes **Nmap** à partir de requêtes en **langage naturel**. Grâce à l’intelligence artificielle et aux modèles de machine learning, ce projet transforme des requêtes complexes en commandes exploitables pour des analyses de sécurité.

Les différents types de requêtes sont classés en trois niveaux de complexité : **EASY**, **MEDIUM** et **HARD**, permettant ainsi une génération dynamique et optimisée des commandes.

## Objectifs

- **Comprendre le besoin** : Convertir des requêtes en langage naturel en commandes Nmap adaptées.
- **Générer des commandes Nmap** : Créer un modèle capable de prédire la complexité des requêtes et de générer les commandes correspondantes.
- **Optimisation** : Améliorer la gestion des requêtes complexes en utilisant des modèles d’IA adaptés (medium et hard).

## Répartition des Tâches

| Personne | Rôle & Responsabilité                                                                                  |
|----------|--------------------------------------------------------------------------------------------------------|
| **Personne 1** | **Imane Allioui** : Construction et gestion du **Knowledge Graph** pour enrichir les données de recherche et de génération de commandes. |
| **Personne 2** | **Chaimae Ababri** : Préparation des données, **fine-tuning des modèles** (Phi-4 et Diffusion) pour la gestion des requêtes **MEDIUM** et **HARD**. |
| **Personne 3** | **Rami Hala** : **Classification des requêtes** (EASY, MEDIUM, HARD) et routage vers les modèles appropriés. |
| **Personne 4** | **Habib Samia** : Développement de l'agent **RAG** pour les requêtes **EASY** et correction automatique des erreurs de requêtes. |
| **Personne 5** | **El Guallaf Hafssa** : Validation des commandes générées et prise de décision finale sur l'exécution des commandes. |

## Technologies Utilisées

- **Python** : Langage principal pour le développement des modèles et du système.
- **PyTorch** : Framework utilisé pour le fine-tuning des modèles **Phi-4** et **Diffusion**.
- **Hugging Face Transformers** : Utilisation des modèles de type T5 pour la génération de commandes Nmap.
- **Spacy** : Pour le prétraitement des données textuelles et l'extraction de caractéristiques.
- **Git LFS** : Gestion des fichiers volumineux (comme les bases de données) dans le dépôt Git.

## Modules et Fonctionnalités

### Personne 1 : Imane Allioui

- **Gestion du Knowledge Graph** : Enrichissement des données avec des relations entre services et ports.
- **Requêtes faciles (EASY)** : Utilisation de l'agent **RAG** pour traiter les requêtes simples de type **EASY**.

### Personne 2 : Chaimae Ababri

En tant que **Personne 2**, vous avez travaillé sur **la gestion des requêtes complexes (MEDIUM et HARD)**, en fine-tunant des modèles de génération de commandes et en créant des scripts d'inférence.

#### Étapes détaillées de votre tâche :

1. **Préparation du Dataset** :
   - **Enrichissement du dataset** : Vous avez créé et enrichi un dataset pour les requêtes **EASY**, **MEDIUM**, et **HARD**. Vous avez intégré des services comme **SSH**, **FTP**, **HTTP**, etc., et associé chaque service à son port respectif.
   - **Paraphrasing des requêtes** : Vous avez augmenté le dataset en créant des paraphrases des requêtes pour rendre le modèle plus flexible face aux variations des instructions. Par exemple, "Scan port 22" a été reformulé sous différentes formes pour couvrir des variantes de syntaxe et de style.
   - **Exemples de données** :
     ```json
     {
       "instruction": "Scan port 22 on 192.168.1.0/24",
       "input": "",
       "output": "nmap -p 22 192.168.1.0/24"
     }
     ```
     Ces exemples ont été utilisés pour entraîner les modèles sur des requêtes de **niveau MEDIUM**.

2. **Fine-Tuning des Modèles** :
   - **Modèle Phi-4 pour les requêtes MEDIUM** : Vous avez fine-tuné un modèle **T5-base** (Phi-4) pour gérer les requêtes **MEDIUM** nécessitant une détection de services et une analyse de vulnérabilités. Le modèle a été entraîné pour comprendre des instructions complexes et générer des commandes Nmap adaptées.
   - **Exemple de fine-tuning du modèle** :
     ```python
     from transformers import T5ForConditionalGeneration, T5Tokenizer
     from transformers import Trainer, TrainingArguments
     from datasets import load_dataset

     model = T5ForConditionalGeneration.from_pretrained("t5-base")
     tokenizer = T5Tokenizer.from_pretrained("t5-base")

     # Charger et préparer le dataset
     train_dataset = load_dataset("data/t5_balanced_train.json")
     val_dataset = load_dataset("data/t5_balanced_val.json")

     training_args = TrainingArguments(
         output_dir="./results",
         per_device_train_batch_size=16,
         per_device_eval_batch_size=16,
         num_train_epochs=3,
         logging_dir='./logs',
     )

     trainer = Trainer(
         model=model,
         args=training_args,
         train_dataset=train_dataset,
         eval_dataset=val_dataset,
         tokenizer=tokenizer,
     )

     trainer.train()
     ```

   - **Modèle Diffusion pour les requêtes HARD** : Pour les requêtes complexes de **niveau HARD**, vous avez utilisé un modèle **Diffusion**. Ce modèle a été fine-tuné pour traiter des scans complexes, comme les scans furtifs, les évasions de pare-feu, et les scans avancés.
     ```python
     from transformers import T5ForConditionalGeneration, T5Tokenizer
     from peft import PeftModel
     import torch

     model = T5ForConditionalGeneration.from_pretrained("t5-base")
     model = model.to("cuda" if torch.cuda.is_available() else "cpu")
     tokenizer = T5Tokenizer.from_pretrained("t5-base")

     peft_model = PeftModel.from_pretrained(model, "path/to/hard_model")

     instruction = "Scan with evasion using decoys on 192.168.1.0/24"
     inputs = tokenizer(instruction, return_tensors="pt")
     outputs = peft_model.generate(**inputs)

     generated_command = tokenizer.decode(outputs[0], skip_special_tokens=True)
     print(f"Commande générée : {generated_command}")
     ```

3. **Évaluation des Modèles** :
   - Vous avez évalué les modèles sur un **dataset de test** pour mesurer leur performance dans la génération de commandes Nmap pour les requêtes **MEDIUM** et **HARD**.
   - **Résultats** : Les modèles ont atteint une précision de **85-92%** pour les requêtes **MEDIUM** et de **70-80%** pour les requêtes **HARD**, ce qui montre une bonne capacité du modèle à gérer des requêtes complexes.

4. **Création des Scripts d'Inférence** :
   - Vous avez créé des scripts permettant d'utiliser les modèles fine-tunés pour générer des commandes Nmap en réponse à des requêtes en langage naturel. Voici un exemple de votre code pour l'inférence :
     ```python
     instruction = "Scan all ports on 192.168.1.0/24"
     generated_command = model.generate(instruction)
     print(f"Commande générée : {generated_command}")
     ```

### Personne 3 : Rami Hala

                               Person 3 Module — Nmap Complexity Classification

📌 Project Context

This module represents the work of Person 3 in the collaborative NMAP-AI project.
It acts as the decision core of the system, responsible for understanding Nmap natural language queries and estimating their complexity level in order to enable intelligent routing to the appropriate AI engine.

🎯 Module Objective

⦁ Given a user Nmap request expressed in natural language, the module must:
⦁ Analyze the query using NLP techniques
⦁ Extract technical and semantic features
⦁ Predict a complexity level
⦁ Provide a clear, explainable decision

🎚️ Complexity Levels

| Level     | Meaning                 | Routing              |
| --------- | ----------------------- | -------------------- |
| 🟢 EASY   | Simple, low-risk scan   | RAG (Person 1)       |
| 🟡 MEDIUM | Standard technical scan | Phi-4 (Person 2)     |
| 🔴 HARD   | Stealth / evasion scan  | Diffusion (Person 2) |

🧠 Global Approach

The module is based on a hybrid architecture combining:

⦁ 🧩 Advanced NLP (spaCy)
⦁ 🌲 Machine Learning (Random Forest)
⦁ 🧠 Expert business rules
⦁ 🕸️ Knowledge Graph enrichment (Neo4j – Person 1)

This design ensures:

⦁ Robust generalization (ML)
⦁ Precise handling of critical edge cases (rules)
⦁ Semantic understanding of Nmap concepts (KG)

🏗️ Module Architecture

src/
├── extract_features.py # NLP feature extraction
├── enrich_with_kg.py # Neo4j knowledge graph enrichment
├── train_classifier.py # ML model training
├── classifier.py # Prediction + business rules
├── router.py # Final intelligent routing
models/
├── complexity_classifier.pkl # Trained ML model
data/
├── dataset_fusionne.csv # Final training dataset
screenshots/

✅ Implemented Features

1️⃣ Advanced NLP Feature Extraction

The file extract_features.py converts a natural language query into a rich numerical vector (>25 features), including:
⦁ Linguistic statistics (tokens, POS, named entities)
⦁ IP address, network range and port detection
⦁ Keyword detection per complexity level
⦁ Nmap options (UDP, OS detection, scripts, timing)
⦁ Single-port detection
⦁ Weighted complexity score

2️⃣ Knowledge Graph Enrichment (Neo4j – Person 1)

The module enrich_with_kg.py enriches features by querying the Knowledge Graph.

Neo4j labels used

⦁ Option
⦁ ScanType
⦁ Port
⦁ Script

Added features

⦁ Number of recognized options
⦁ Number of associated relationships
⦁ Average usage frequency
⦁ Script risk indicators

🔒 Fault tolerance: if Neo4j is unavailable → default values are applied.

3️⃣ Machine Learning Classification (Random Forest)

⦁ Algorithm: RandomForestClassifier
⦁ Input: numerical feature vector (NLP + KG)
⦁ Classes: EASY / MEDIUM / HARD
⦁ Dataset: merged multi-source datasets (CSV + JSON)

The trained model is saved as:

models/complexity_classifier.pkl

![Training Accuracy](screenshots/training_accuracy.png)

4️⃣ Post-Prediction Business Rules

To handle linguistic ambiguities and edge cases, expert rules are applied after ML prediction:

⦁ Single port scan → EASY
⦁ Standard ports without advanced options → EASY
⦁ OS detection on a network → at least MEDIUM
⦁ Stealth / evasion techniques (fragmentation, decoy, spoofing) → HARD

5️⃣ Final Classifier (Interactive Mode)

Run:

⦁ python src/classifier.py

Example:

Enter Nmap query > Stealth scan with fragmentation and decoy
→ Detected complexity: HARD

![Classifier Test](screenshots/classifier_test.png)

6️⃣ Intelligent Router

The router.py module provides:

⦁ Complexity prediction
⦁ Confidence score
⦁ Human-readable explanation
⦁ Clear routing recommendation

![Router Output](screenshots/router_output.png)

🌐 REST API — FastAPI (Production Ready)

The module exposes a REST API using FastAPI, allowing external systems (frontend, orchestrator, or other agents) to query the Nmap complexity classifier in real time.

📄 api.py

The API wraps the routing logic and provides:

⦁ Input validation
⦁ Error handling
⦁ Confidence scores
⦁ Explainable predictions
⦁ CORS support (for frontend / Postman testing)

🚀 Available Endpoints

🔹 Health Check
GET /

Response

{
"message": "NMAP-AI Router prêt ! POST /predict avec {'query': 'votre phrase'}"
}

🔹 Predict Nmap Complexity
POST /predict

Request Body

{
"query": "Scan SYN furtif avec fragmentation sur 192.168.1.0/24"
}

Response

{
"predicted_complexity": "HARD",
"confidence": 0.973,
"all_probabilities": {
"EASY": 0.013,
"MEDIUM": 0.013,
"HARD": 0.973
},
"explanation": "• Fragmentation de paquets détectée (-f)\n→ **Classe prédite : HARD**"
}

🛡 Error Handling

⦁ Empty query → 400 Bad Request
⦁ Non-Nmap request → 400 Bad Request
⦁ Internal error → 500 Internal Server Error (with server traceback)

▶️ Run the API

⦁ python src/api.py

Server runs on:

http://localhost:8002

Interactive Swagger UI:

http://localhost:8002/docs

![FastAPI Swagger](screenshots/api_swagger.png)
![API Prediction](screenshots/api_predict.png)

📊 Results and Validation

Significant reduction of false HARD classifications

Proper handling of edge cases

Fully explainable decisions

System ready for global integration

🤝 Integration with Other Team Members

| Person   | Interaction                  |
| -------- | ---------------------------- |
| Person 1 | Knowledge Graph (Neo4j)      |
| Person 2 | Routing to Phi-4 / Diffusion |
| Person 4 | System-level integration     |

🏁 Module Status

✅ Development: COMPLETED
✅ Testing: VALIDATED
✅ Integration: READY


### Personne 4 : Habib Samia

- **Développement de l'Agent RAG** : Traitement des requêtes **EASY** en utilisant l'agent **RAG** pour générer des commandes simples de Nmap.
- **Correction automatique** des erreurs dans les requêtes et ajustements en fonction des critères.

### Personne 5 : El Guallaf Hafssa

- **Validation des Commandes Générées** : Vérification de la précision des commandes générées par les modèles pour s'assurer de leur validité avant l'exécution.
- **Prise de décision** sur l'exécution des commandes en fonction du type de requête et du contexte de sécurité.

## Installation et Utilisation

### Prérequis

- Python 3.8+ installé
- Pip pour gérer les packages

### Installation des dépendances

```bash
git clone https://github.com/HafOosa/NMAP-AI.git
cd NMAP-AI
pip install -r requirements.txt
