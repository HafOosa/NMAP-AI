# debug_kg.py
from utils import Neo4jKGWithCache

kg = Neo4jKGWithCache(password="nmap_ai_2024")

print("=== Labels présents ===")
labels = kg.cached_query("CALL db.labels()")
print([l['label'] for l in labels])

print("\n=== Propriétés des nœuds liés à Nmap ===")
samples = kg.cached_query("MATCH (n) WHERE n.name =~ '(?i).*sS|.*sV|.*p.*' RETURN n LIMIT 20")
for s in samples:
    print(s)

print("\n=== Exemples de relations CONFLICTS_WITH ===")
conflicts = kg.cached_query("MATCH (a)-[:CONFLICTS_WITH]->(b) RETURN a.name, b.name LIMIT 10")
print(conflicts)

kg.close()