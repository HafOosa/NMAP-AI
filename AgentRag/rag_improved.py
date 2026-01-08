# rag_improved.py - VERSION FINALE OPTIMISÉE
from .utils import Neo4jKGWithCache
import re

class ImprovedRAG:
    def __init__(self):
        self.kg = Neo4jKGWithCache()

    def generate_command(self, user_query: str) -> str:
        features = extract_features(user_query)
        target = features["target"] or "192.168.1.1"
        lower = user_query.lower()

        # Détection d'intent principal
        options = set()

        # 1. Intent prioritaire
        if any(w in lower for w in ["version", "service", "détection de version", "services"]):
            options.add("-sV")
        if any(w in lower for w in ["os", "système d'exploitation", "operating system"]):
            options.add("-O")
        if any(w in lower for w in ["agressif", "aggressive", "thorough"]):
            options.add("-A")
        if any(w in lower for w in ["syn", "rapide", "stealth", "tcp connect"]):
            options.add("-sS")
        if "udp" in lower:
            options.add("-sU")

        # 2. Port scanning
        if any(w in lower for w in ["port", "ouverts", "tout", "all", "complet", "65535"]):
            options.add("-p-")
        elif any(w in lower for w in ["défaut", "common", "top"]):
            options.add("-F")  # Fast scan top ports

        # 3. Scripts NSE seulement si explicitement demandé
        if any(w in lower for w in ["script", "scripts", "nse"]):
            options.add("--script")

        # 4. Timing seulement si demandé
        if any(w in lower for w in ["rapide", "fast", "agressif"]):
            options.add("-T4")
        elif any(w in lower for w in ["lent", "slow", "discret"]):
            options.add("-T2")

        # 5. Recherche KG seulement pour complément (ex: -f si "fragment")
        keywords = features["keywords"]
        if keywords:
            kw_list = ", ".join([f"'{k}'" for k in keywords[:8]])
            cypher = f"""
            MATCH (o:Option)
            WHERE ANY(k IN [{kw_list}] 
                      WHERE toLower(o.name) CONTAINS k OR toLower(o.description) CONTAINS k)
              AND o.flag IN ['-f', '--traceroute', '-D', '-g']
            RETURN o.flag
            """
            extra = self.kg.cached_query(cypher)
            for e in extra:
                if "fragment" in lower or "éviter" in lower: options.add("-f")
                if "traceroute" in lower: options.add("--traceroute")

        # Ordre logique des options
        order = ["-A", "-O", "-sV", "-sS", "-sU", "-p-", "-F", "-T4", "-T2", "--script", "-f", "--traceroute"]
        final_options = [opt for opt in order if opt in options]
        final_options += [opt for opt in options if opt not in order]

        cmd = f"nmap {' '.join(final_options)} {target}".strip()
        return re.sub(r'\s+', ' ', cmd) or f"nmap {target}"

    def close(self):
        self.kg.close()