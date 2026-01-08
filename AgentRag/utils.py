# utils.py
import spacy
import re
from neo4j import GraphDatabase
from functools import lru_cache

# Modèle français pour mieux comprendre les queries
nlp = spacy.load("fr_core_news_sm")

class Neo4jKGWithCache:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="nmap_ai_2024"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def _run_query(self, cypher_query):
        with self.driver.session() as session:
            result = session.run(cypher_query)
            return [record.data() for record in result]

    @lru_cache(maxsize=200)
    def cached_query(self, cypher_query: str):
        return self._run_query(cypher_query)

def extract_features(query: str) -> dict:
    doc = nlp(query.lower())
    # Entités + détection IP/hostname
    ip_host = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b|scanme\.nmap\.org|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', query)
    keywords = [token.lemma_ for token in doc if token.pos_ in ["NOUN", "VERB", "ADJ"] and not token.is_stop]
    return {
        "keywords": keywords,
        "target": ip_host[0] if ip_host else None
    }

def parse_nmap_command(command: str):
    parts = re.split(r'\s+', command.strip())
    options = [p for p in parts if p.startswith("-")]
    target = next((p for p in parts if re.match(r'^(?:\d{1,3}\.){3}\d{1,3}$|^scanme\.nmap\.org$|^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', p)), "TARGET")
    return {"options": options, "target": target, "full": command}