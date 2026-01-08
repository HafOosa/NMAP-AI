import spacy
import re

nlp = spacy.load("fr_core_news_sm")

# ==============================
# Mots-clés
# ==============================
EASY_KEYWORDS = ["simple", "basique", "rapide", "défaut", "ouvert", "ping", "liste", "localhost", "local", "default", "quick"]
MEDIUM_KEYWORDS = ["version", "service", "os", "détection", "udp", "détecte", "syn", "agressif", "aggressive", "timing", "t2", "t3", "t4", "t5", "script", "vuln", "insane"]
HARD_KEYWORDS = ["furtif", "stealth", "idle", "zombie", "decoy", "spoof", "fragment", "proxy", "bounce", "badsum", "null", "fin", "xmas", "t0", "t1", "parano", "paranoid", "evasion", "ids", "firewall", "mtu", "évite", "évasion"]

def single_port_reduction(query: str) -> int:
    q = query.lower()
    if "un port" in q or "seulement un port" in q or "port unique" in q or re.search(r"-p\s*\d+(?!\s*-|\s*/)", q):
        return -1
    return 0

# ==============================
# VERSION LISTE POUR LE MODÈLE (comme lors de l'entraînement)
# ==============================
def extract_features(query: str) -> list:
    if not query:
        query = ""
    query_lower = query.lower()
    doc = nlp(query_lower)

    features = []

    # Statistiques
    features.append(len(doc))
    features.append(sum(1 for t in doc if t.pos_ == "VERB"))
    features.append(sum(1 for t in doc if t.pos_ == "NOUN"))
    features.append(sum(1 for t in doc if t.pos_ == "ADJ"))
    features.append(len(query))

    # IP
    features.append(1 if re.search(r'\d+\.\d+\.\d+\.\d+', query_lower) else 0)
    features.append(1 if "/" in query_lower or "-" in query_lower else 0)
    features.append(len(re.findall(r'\d+\.\d+\.\d+\.\d+', query_lower)))

    # Mots-clés
    nb_easy = sum(1 for t in doc if t.text in EASY_KEYWORDS)
    nb_medium = sum(1 for t in doc if t.text in MEDIUM_KEYWORDS)
    nb_hard = sum(1 for t in doc if t.text in HARD_KEYWORDS)
    features.extend([nb_easy, nb_medium, nb_hard])
    features.append(nb_hard / (len(doc) + 1))

    # Options
    features.append(1 if re.search(r't[0-5]|timing', query_lower) else 0)
    features.append(1 if "script" in query_lower else 0)
    features.append(1 if "udp" in query_lower else 0)
    features.append(1 if "os" in query_lower else 0)
    features.append(1 if "version" in query_lower else 0)
    features.append(1 if any(k in query_lower for k in HARD_KEYWORDS) else 0)
    features.append(sum(1 for kw in HARD_KEYWORDS + MEDIUM_KEYWORDS if kw in query_lower))

    # Avancé
    features.append(len(doc.ents))
    features.append(1 if "proxy" in query_lower else 0)
    features.append(1 if "decoy" in query_lower else 0)

    # Scripts
    nb_scripts = 10 if "script" in query_lower else 0
    features.append(nb_scripts)

    # Score
    features.append(nb_hard * 5 + nb_medium * 2 + nb_easy + single_port_reduction(query))

    # KG (fallback si indisponible)
    kg = [0, 0, 0.0, 0, 0, 0]
    try:
        from enrich_with_kg import enrich_features_with_kg
        kg_result = enrich_features_with_kg(query)
        if isinstance(kg_result, list) and len(kg_result) >= 6:
            kg = kg_result[:6]
    except:
        pass
    features.extend(kg)

    return features

# ==============================
# VERSION DICT POUR LE ROUTER ET L'EXPLICATION
# ==============================
def extract_features_dict(query: str) -> dict:
    if not query:
        query = ""
    query_lower = query.lower()
    doc = nlp(query_lower)

    features = {}
    features["num_tokens"] = len(doc)
    features["has_ip"] = bool(re.search(r'\d+\.\d+\.\d+\.\d+', query_lower))
    features["has_range"] = "/" in query_lower or "-" in query_lower
    features["nb_hard_keywords"] = sum(1 for t in doc if t.text in HARD_KEYWORDS)
    features["has_timing"] = bool(re.search(r't[0-5]|timing', query_lower))
    features["has_scripts"] = "script" in query_lower
    features["has_evasion"] = any(k in query_lower for k in HARD_KEYWORDS)
    features["has_decoy"] = "decoy" in query_lower
    features["nmap_keywords"] = [t.text for t in doc if t.text in EASY_KEYWORDS + MEDIUM_KEYWORDS + HARD_KEYWORDS]

    return features

# ==============================
# Test
# ==============================
if __name__ == "__main__":
    print("Liste pour modèle :", len(extract_features("test")))
    print("Dict pour explication :", extract_features_dict("test"))