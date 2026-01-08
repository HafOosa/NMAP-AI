# 📘 Module Personne 3 — Classification de la complexité Nmap

## 🎯 Objectif du module

Ce module correspond au travail de la **Personne 3** dans le projet **NMAP-AI**.  
Il a pour objectif d’**analyser une requête Nmap en langage naturel** et de **déterminer automatiquement son niveau de complexité** parmi :

- 🟢 **EASY** → Routage vers RAG (Personne 1)
- 🟡 **MEDIUM** → Routage vers Phi-4 (Personne 2)
- 🔴 **HARD** → Routage vers Diffusion (Personne 2)

La classification repose sur une **approche hybride** combinant :

- Extraction de features NLP avancées
- Apprentissage automatique (Random Forest)
- Règles métier expertes
- Enrichissement optionnel via Knowledge Graph (Neo4j)

---

## 🧠 Fonctionnalités implémentées (état actuel : TERMINÉ À 100%)

### ✅ 1. Extraction de features NLP avancées

Le module `extract_features.py` transforme une requête textuelle en un **vecteur numérique riche** (> 20 features), incluant :

- Statistiques NLP via **spaCy** (tokens, POS, entités nommées)
- Longueur et structure de la requête
- Détection d’IP, plages réseau et ports
- Mots-clés associés aux niveaux EASY / MEDIUM / HARD
- Options Nmap (scripts, UDP, OS detection, version, timing, evasion)
- Score de complexité pondéré
- Gestion du cas **"un seul port"**

---

### ✅ 2. Enrichissement via Knowledge Graph (Neo4j – Personne 1)

Le module `enrich_with_kg.py` permet un **enrichissement sémantique optionnel** basé sur le KG de la Personne 1.

**Labels exploités** : `Option`, `ScanType`, `Port`, `Script`  
**Features ajoutées** :

- Nombre d’options reconnues
- Nombre de relations associées
- Fréquence moyenne d’usage
- Score de complexité du type de scan
- Nombre de ports détectés
- Score de dangerosité des scripts

🔒 **Tolérance aux pannes** : si Neo4j est indisponible → valeurs par défaut.

---

### ✅ 3. Classification de la complexité (Machine Learning)

- `train_classifier.py` : entraînement du **Random Forest**, évaluation, sauvegarde du modèle (`complexity_classifier.pkl`)
- `router.py` : prédiction en temps réel avec :
  - **Calcul du score de confiance** (probabilités)
  - **Explication détaillée** de la décision (mots-clés, options détectées)

---

### ✅ 4. Vérificateur de pertinence (Relevance Checker)

Rejette automatiquement les requêtes **hors sujet** (ex : "Quelle est la météo ?") grâce à un score basé sur :

- Mots-clés Nmap
- Présence d’IP/réseau
- Options techniques

→ Retourne `IRRELEVANT` si non pertinent.

---

### ✅ 5. Router intelligent complet

Le module `router.py` fournit :

- Prédiction de complexité
- Score de confiance
- Explication lisible
- **Recommandation de routage clair** vers le bon moteur IA

**Mode test interactif** :

```bash
python src/router.py
```
