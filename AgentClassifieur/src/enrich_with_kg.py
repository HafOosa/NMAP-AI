from neo4j import GraphDatabase
import spacy

nlp = spacy.load("fr_core_news_sm")

driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "nmap_ai_2024")
)

def enrich_features_with_kg(query: str) -> list:
    """
    Retourne 6 features KG :
    [kg_options, kg_relations, kg_freq,
     kg_scan_score, kg_ports_count, kg_scripts_score]
    """

    doc = nlp(query.lower())
    terms = [t.text for t in doc if t.pos_ in ["NOUN", "VERB", "ADJ", "PROPN", "NUM"]]

    kg_options = 0
    kg_relations = 0
    kg_freq = 0.0
    kg_scan_score = 0
    kg_ports_count = 0
    kg_scripts_score = 0

    try:
        with driver.session() as session:

            # =========================
            # 1. Options + relations
            # =========================
            res = session.run("""
                UNWIND $terms AS term
                MATCH (o:Option {name: term})
                OPTIONAL MATCH (o)-[r]->()
                RETURN count(DISTINCT o) AS options, count(r) AS relations
            """, terms=terms).single()

            if res:
                kg_options = res["options"] or 0
                kg_relations = res["relations"] or 0

            # =========================
            # 2. Fréquence moyenne
            # =========================
            freqs = session.run("""
                UNWIND $terms AS term
                MATCH (o:Option {name: term})
                RETURN coalesce(o.frequency, 0) AS freq
            """, terms=terms)

            freq_values = [r["freq"] for r in freqs]
            kg_freq = sum(freq_values) / len(freq_values) if freq_values else 0.0

            # =========================
            # 3. ScanType → score
            # =========================
            scan_types = session.run("""
                UNWIND $terms AS term
                MATCH (s:ScanType {name: term})
                RETURN s.name AS name
            """, terms=terms)

            for r in scan_types:
                st = r["name"].lower()
                if st in ["syn", "tcp"]:
                    kg_scan_score += 2
                elif st in ["udp"]:
                    kg_scan_score += 3
                elif st in ["fin", "null", "xmas"]:
                    kg_scan_score += 4
                elif st in ["idle"]:
                    kg_scan_score += 5

            # =========================
            # 4. Ports détectés
            # =========================
            ports = session.run("""
                UNWIND $terms AS term
                MATCH (p:Port {number: term})
                RETURN p.number AS port
            """, terms=terms)

            ports_list = [r["port"] for r in ports]
            kg_ports_count = len(set(ports_list))

            # =========================
            # 5. Scripts (dangerosité)
            # =========================
            scripts = session.run("""
                UNWIND $terms AS term
                MATCH (s:Script {name: term})
                RETURN s.category AS category
            """, terms=terms)

            for r in scripts:
                cat = (r["category"] or "").lower()
                if cat in ["default", "safe"]:
                    kg_scripts_score += 1
                elif cat in ["vuln"]:
                    kg_scripts_score += 3
                elif cat in ["exploit", "bruteforce"]:
                    kg_scripts_score += 5

    except Exception as e:
        print(f"⚠️ KG non accessible : {e}")
        return [0, 0, 0.0, 0, 0, 0]

    return [
        kg_options,
        kg_relations,
        kg_freq,
        kg_scan_score,
        kg_ports_count,
        kg_scripts_score
    ]


def close_kg_connection():
    driver.close()
