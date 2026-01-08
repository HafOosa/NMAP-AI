import joblib
import os
from extract_features import extract_features  # ← Retourne une LISTE

# ================= CONFIGURATION =================
MODEL_PATH = "models/complexity_classifier.pkl"
LABELS = ["EASY", "MEDIUM", "HARD"]

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Modèle non trouvé : {MODEL_PATH}. Lance d'abord train_classifier.py")

print("Chargement du modèle de classification de complexité...")
classifier = joblib.load(MODEL_PATH)
print("Modèle chargé avec succès !\n")

# ================= 1. VÉRIFICATEUR DE PERTINENCE =================
def is_relevant_to_nmap(query: str, threshold: float = 0.3) -> tuple[bool, str]:
    """
    Vérifie si la requête concerne Nmap.
    """
    query_lower = query.lower()
    features_list = extract_features(query)  # liste, on utilise ce qu'on peut
    
    relevance_score = 0.0
    
    # Mots-clés forts
    strong_keywords = ["nmap", "scan", "port", "ports", "host", "discovery", "version", "os detection", "script", "vuln", "traceroute", "ping", "syn", "udp", "tcp", "fragment", "decoy", "spoof", "stealth", "evasion", "timing"]
    keyword_hits = sum(1 for kw in strong_keywords if kw in query_lower)
    relevance_score += keyword_hits * 0.2
    
    # Présence d'IP classique
    if any(net in query_lower for net in ["192.168", "10.", "172.16", "127.0"]):
        relevance_score += 0.4
    
    # Présence d'options Nmap typiques
    if any(opt in query_lower for opt in ["-p", "-s", "-o", "-t", "--script", "-v"]):
        relevance_score += 0.3
    
    is_relevant = relevance_score >= threshold
    reason = "Pertinent (concerne Nmap)" if is_relevant else "Ne semble pas concerner Nmap"
    
    return is_relevant, reason

# ================= 2. EXPLICATION DE LA PRÉDICTION =================
def explain_prediction(query: str, predicted: str) -> str:
    query_lower = query.lower()
    parts = []
    
    if any(word in query_lower for word in ["fragment", "-f"]):
        parts.append("• Fragmentation de paquets détectée (-f)")
    if any(word in query_lower for word in ["decoy", "-d", "rnd"]):
        parts.append("• Utilisation de decoys (-D RND:...)")
    if any(word in query_lower for word in ["spoof", "mac", "--spoof-mac"]):
        parts.append("• Spoofing MAC ou source")
    if any(word in query_lower for word in ["t0", "t1", "paranoid", "sneaky", "idle"]):
        parts.append("• Timing très lent (furtif : -T0 ou -T1)")
    if "proxy" in query_lower or "bounce" in query_lower:
        parts.append("• Utilisation de proxy ou bounce")
    if "script" in query_lower and any(v in query_lower for v in ["vuln", "malware"]):
        parts.append("• Scripts vulnérabilités détectés")
    
    if not parts:
        parts.append("• Scan basique : ping, version, OS, ports simples ou tous ports")
    
    parts.append(f"→ **Classe prédite : {predicted.upper()}**")
    
    return "\n".join(parts)

# ================= 3. ROUTER PRINCIPAL =================
def predict_complexity(query: str):
    if not query or not query.strip():
        return {
            "predicted_complexity": "EMPTY",
            "confidence": 0.0,
            "all_probabilities": {"EASY": 0.0, "MEDIUM": 0.0, "HARD": 0.0},
            "explanation": "Requête vide"
        }
    
    # Vérification pertinence
    relevant, reason = is_relevant_to_nmap(query)
    if not relevant:
        return {
            "predicted_complexity": "IRRELEVANT",
            "confidence": 0.0,
            "all_probabilities": {"EASY": 0.0, "MEDIUM": 0.0, "HARD": 0.0},
            "explanation": reason
        }
    
    # Prédiction avec le modèle
    features = extract_features(query)  # ← liste
    prediction = classifier.predict([features])[0]
    probabilities = classifier.predict_proba([features])[0]
    
    max_proba = max(probabilities)
    predicted_label = LABELS[prediction]
    
    proba_dict = {label: round(prob, 3) for label, prob in zip(LABELS, probabilities)}
    
    explanation = explain_prediction(query, predicted_label)
    
    return {
        "predicted_complexity": predicted_label,
        "confidence": round(max_proba, 3),
        "all_probabilities": proba_dict,
        "explanation": explanation
    }

# ================= MODE INTERACTIF =================
if __name__ == "__main__":
    print("=== NMAP-AI COMPLEXITY ROUTER - Personne 3 ===\n")
    print("Entre une requête Nmap (ou 'quit' pour arrêter)\n")
    
    while True:
        user_input = input("Requête Nmap > ").strip()
        
        if user_input.lower() in ["quit", "exit", "q"]:
            print("\nBye ! Ton module Personne 3 est complet et prêt pour l'intégration ! 🚀")
            break
        
        result = predict_complexity(user_input)
        
        print(f"\n→ Résultat : {result['predicted_complexity']}")
        print(f"   Confiance : {result['confidence'] * 100:.1f} %")
        print(f"   Probabilités : {result['all_probabilities']}")
        print(f"   Explication :\n{result['explanation']}")
        
        if result["predicted_complexity"] == "EASY":
            print("   → Routage recommandé : RAG Agent (Personne 1)\n")
        elif result["predicted_complexity"] == "MEDIUM":
            print("   → Routage recommandé : Modèle Phi-4 (Personne 2)\n")
        elif result["predicted_complexity"] == "HARD":
            print("   → Routage recommandé : Modèle Diffusion (Personne 2)\n")
        elif result["predicted_complexity"] == "IRRELEVANT":
            print("   → Rejet : requête hors sujet\n")
        print("-" * 80)