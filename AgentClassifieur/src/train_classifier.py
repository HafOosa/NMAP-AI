import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os
from extract_features import extract_features

# ================= CONFIGURATION =================
DATA_PATH = "data/data_personn3.csv"  

if not os.path.exists(DATA_PATH):
    print("ERREUR : Le fichier CSV n'existe pas !")
    print(f"Chemin attendu : {os.path.abspath(DATA_PATH)}")
    exit()

# ================= CHARGEMENT ET NETTOYAGE =================
print("Fichier CSV trouvé ! Chargement...")
df = pd.read_csv(DATA_PATH)
print(f"{len(df)} exemples chargés.\n")

print("Colonnes du CSV :", df.columns.tolist())
print("Valeurs uniques dans 'complexity' avant normalisation :", df["complexity"].unique())

# Normalisation de la colonne complexity (au cas où il y ait des espaces ou majuscules)
df["complexity"] = df["complexity"].str.strip().str.lower()

print("Valeurs uniques dans 'complexity' après normalisation :", df["complexity"].unique())

# ================= EXTRACTION DES FEATURES =================
print("\nExtraction des features en cours...")
X = [extract_features(q) for q in df["query"]]

# ================= MAPPING DES CLASSES =================
complexity_mapping = {"easy": 0, "medium": 1, "hard": 2}
y = df["complexity"].map(complexity_mapping)

# Vérification finale des valeurs inconnues
if y.isna().any():
    unknown = df[y.isna()]["complexity"].unique()
    print(f"\nERREUR : Valeurs de complexité inconnues détectées : {unknown}")
    print("Valeurs attendues : 'easy', 'medium', 'hard'")
    exit()
else:
    print("Toutes les complexités sont valides !\n")

# ================= ENTRAÎNEMENT =================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print("Entraînement du modèle Random Forest...")
model = RandomForestClassifier(
    n_estimators=300,
    random_state=42,
    n_jobs=-1,
    class_weight="balanced"
)
model.fit(X_train, y_train)

# ================= ÉVALUATION =================
preds = model.predict(X_test)
accuracy = accuracy_score(y_test, preds)
print(f"Précision sur le jeu de test : {accuracy * 100:.2f} %\n")

print("Rapport de classification détaillé :")
print(classification_report(y_test, preds, target_names=["EASY", "MEDIUM", "HARD"]))

# ================= SAUVEGARDE DU MODÈLE =================
MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)
MODEL_PATH = os.path.join(MODEL_DIR, "complexity_classifier.pkl")
joblib.dump(model, MODEL_PATH)
print(f"\nModèle sauvegardé avec succès : {MODEL_PATH}")

print("\nTout est prêt ! Tu peux maintenant utiliser le classifieur dans classifier.py")