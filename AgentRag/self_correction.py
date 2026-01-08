# self_correction.py
from utils import Neo4jKGWithCache, parse_nmap_command
import re

class SelfCorrection:
    def __init__(self):
        self.kg = Neo4jKGWithCache()
        self.max_iterations = 3

    def _is_valid_flag(self, flag):
        result = self.kg.cached_query(f"MATCH (o:Option {{flag: '{flag}'}}) RETURN o.flag LIMIT 1")
        return len(result) > 0

    def correct(self, raw_command: str) -> dict:
        command = raw_command.strip()
        history = [command]
        analysis = []

        for it in range(1, self.max_iterations + 1):
            parsed = parse_nmap_command(command)
            options = parsed["options"]
            target = parsed["target"]

            invalid = [opt for opt in options if not self._is_valid_flag(opt)]

            if not invalid:
                analysis.append(f"Itération {it} : Toutes les options sont valides → Commande OK !")
                break

            analysis.append(f"Itération {it} : Options invalides détectées → {invalid}")
            # On retire simplement les invalides
            options = [opt for opt in options if opt not in invalid]
            command = f"nmap {' '.join(options)} {target}".strip()
            command = re.sub(r'\s+', ' ', command)
            history.append(command)

        return {
            "original": raw_command,
            "final_command": command,
            "history": history,
            "analysis": "\n".join(analysis)
        }

    def close(self):
        self.kg.close()