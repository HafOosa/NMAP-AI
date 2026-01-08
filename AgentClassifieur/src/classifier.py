import joblib
import re
from extract_features import extract_features

# ================================
# Chargement du modèle ML
# ================================
MODEL_PATH = "models/complexity_classifier.pkl"
model = joblib.load(MODEL_PATH)

LABELS = ["EASY", "MEDIUM", "HARD"]

# ================================
# Règles métier post-prédiction
# ================================
def post_rule_adjustment(pred_label: str, query: str) -> str:
    """
    Ajuste la prédiction ML avec des règles métier expertes
    (approche hybride ML + Expert Rules)
    """
    q = query.lower()

    # =========================
    # RÈGLE PRIORITAIRE : EASY
    # =========================
    # Scan simple = 1 port, pas d’options avancées
    simple_keywords = ["scan", "port"]
    advanced_keywords = [
        "service", "version", "os", "detect",
        "script", "vuln", "udp", "aggressive",
        "stealth", "furtif", "evasion", "ids",
        "firewall", "bypass", "timing"
    ]

    single_port = (
        re.search(r"\bport\s+\d+\b", q)
        or re.search(r"-p\s*\d+\b", q)
    )

    network_scan = any(
        k in q for k in ["/24", "/16", "/8", "plage", "réseau", "subnet"]
    )

    if (
        all(k in q for k in simple_keywords)
        and single_port
        and not network_scan
        and not any(k in q for k in advanced_keywords)
    ):
        return "EASY"

    # =========================
    # Détection avancée
    # =========================
    uses_script = "script" in q or "vuln" in q
    uses_service_detection = any(k in q for k in ["service", "version", "os"])

    # =========================
    # Évasion critique
    # =========================
    critical_evasion = any(
        k in q for k in [
            "proxy", "decoy", "idle", "zombie",
            "spoof", "fragment", "badsum",
            "furtif", "stealth", "t0", "t1",
            "parano", "ids", "evasion"
        ]
    )

    # HARD absolu sauf cas très limité
    if critical_evasion:
        if single_port and not network_scan and not uses_script:
            return "MEDIUM"
        return "HARD"

    # =========================
    # Ajustement HARD → MEDIUM
    # =========================
    if pred_label == "HARD":
        if single_port and not network_scan and not uses_script:
            return "MEDIUM"

    # =========================
    # Ajustement EASY → MEDIUM
    # =========================
    if pred_label == "EASY":
        if uses_script or uses_service_detection or network_scan:
            return "MEDIUM"

    return pred_label

# ================================
# Fonction principale
# ================================
def get_complexity(query: str) -> str:
    """
    Retourne la complexité finale (EASY / MEDIUM / HARD)
    """
    features = extract_features(query)
    pred_idx = model.predict([features])[0]
    pred_label = LABELS[pred_idx]

    final_label = post_rule_adjustment(pred_label, query)
    return final_label

# ================================
# Mode interactif (debug)
# ================================
if __name__ == "__main__":
    print("🧠 Classificateur NMAP-AI prêt !")
    print("Tape 'quit' pour quitter.\n")

    while True:
        q = input("➤ Requête Nmap > ").strip()
        if q.lower() == "quit":
            print("👋 Fin du programme.")
            break
        if not q:
            continue

        complexity = get_complexity(q)
        print(f"✅ Complexité détectée : {complexity}\n")
