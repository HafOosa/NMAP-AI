"""
=================================================================
COMPREHENSION AGENT - Vérification de pertinence NMAP
=================================================================
Étape 1 du pipeline - Vérifie si la requête est pertinente pour NMAP
"""

from dataclasses import dataclass
from typing import Tuple
import re

@dataclass
class ComprehensionResult:
    is_relevant: bool
    reason: str
    confidence: float
    keywords_found: list

class ComprehensionAgent:
    """
    Agent de compréhension qui vérifie la pertinence d'une requête NMAP
    """
    
    # Mots-clés NMAP importants
    NMAP_KEYWORDS = {
        # Commandes NMAP
        'nmap', 'scan', 'scanner', 'scanning',
        'port', 'ports', 'portage',
        'host', 'hosts', 'serveur', 'serveurs',
        'ip', 'adresse', 'réseau', 'network',
        
        # Types de scan
        'tcp', 'udp', 'icmp', 'ping',
        'syn', 'connect', 'ack', 'fin', 'xmas',
        'null', 'maitre', 'idle',
        
        # Détection
        'détection', 'detection', 'identify', 'discovery',
        'version', 'service', 'service detection',
        'os', 'système opérationnel', 'operating system',
        'fingerprint', 'empreinte',
        
        # Options NMAP
        'timeout', 'timing', 'aggressif', 'aggressive',
        'stealth', 'furtif', 'quiet', 'silencieux',
        'evasion', 'évasion', 'ids', 'firewall',
        'fragmentation', 'decoy', 'leurre',
        'script', 'nse', 'output', 'save',
        
        # Cibles
        '192', '10.', '172', '127', 'localhost',
        'subnet', 'sous-réseau', 'range',
        
        # Variantes
        'réseau', 'network', 'analyse', 'analysis',
        'vuln', 'vulnerability', 'vulnerabilité'
    }
    
    # Mots-clés NON-NMAP (à rejeter)
    NON_NMAP_KEYWORDS = {
        'weather', 'météo', 'temps',
        'recipe', 'recette', 'cuisine',
        'movie', 'film', 'cinéma',
        'book', 'livre', 'histoire',
        'music', 'musique', 'chanson',
        'sport', 'football', 'basketball',
        'game', 'jeu', 'vidéo',
        'love', 'amour', 'relation',
        'python', 'java', 'javascript', 'programming',
        'math', 'mathématiques', 'algebra',
        'histoire', 'géographie', 'science',
        'hello', 'bonjour', 'comment allez-vous'
    }
    
    def __init__(self):
        self.name = "Comprehension Agent"
    
    def understand(self, query: str) -> ComprehensionResult:
        """Analyse une requête pour vérifier sa pertinence NMAP"""
        
        query_lower = query.lower()
        
        # ÉTAPE 1: Vérifier les mots-clés NMAP
        nmap_keywords_found = self._find_keywords(query_lower, self.NMAP_KEYWORDS)
        
        # ÉTAPE 2: Vérifier les mots-clés NON-NMAP
        non_nmap_keywords_found = self._find_keywords(query_lower, self.NON_NMAP_KEYWORDS)
        
        # ÉTAPE 3: Vérifier les patterns NMAP
        has_nmap_pattern = self._check_nmap_patterns(query_lower)
        
        # ÉTAPE 4: Décision finale
        nmap_score = self._calculate_relevance_score(
            len(nmap_keywords_found),
            len(non_nmap_keywords_found),
            has_nmap_pattern,
            len(query)
        )
        
        # ÉTAPE 5: Déterminer la pertinence
        is_relevant = nmap_score >= 0.5
        reason = self._generate_reason(
            is_relevant,
            nmap_keywords_found,
            non_nmap_keywords_found,
            nmap_score
        )
        
        return ComprehensionResult(
            is_relevant=is_relevant,
            reason=reason,
            confidence=nmap_score,
            keywords_found=nmap_keywords_found
        )
    
    def _find_keywords(self, text: str, keywords: set) -> list:
        """Cherche les mots-clés dans le texte"""
        found = []
        for keyword in keywords:
            # Chercher le mot-clé complet ou comme partie d'un mot
            if keyword in text or self._word_in_text(keyword, text):
                found.append(keyword)
        return found
    
    def _word_in_text(self, word: str, text: str) -> bool:
        """Vérifie si un mot est dans le texte (avec limites de mots)"""
        pattern = r'\b' + re.escape(word) + r'\b'
        return bool(re.search(pattern, text))
    
    def _check_nmap_patterns(self, query: str) -> bool:
        """Vérifie les patterns typiques NMAP"""
        patterns = [
            r'\b(nmap|scan)\b',
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',  # IP
            r'-[a-zA-Z]+\s',  # Options style NMAP
            r'(port|service|host|target)',
            r'(tcp|udp|icmp|syn|stealth)',
        ]
        
        for pattern in patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return True
        
        return False
    
    def _calculate_relevance_score(self, nmap_count: int, non_nmap_count: int, 
                                   has_pattern: bool, query_length: int) -> float:
        """Calcule le score de pertinence NMAP"""
        
        score = 0.0
        
        # Points pour mots-clés NMAP
        score += min(nmap_count * 0.15, 0.6)  # Max 0.6
        
        # Points pour pattern NMAP
        if has_pattern:
            score += 0.2
        
        # Pénalité pour mots-clés NON-NMAP
        score -= non_nmap_count * 0.2
        
        # Bonus pour requête de longueur raisonnable
        if 10 <= query_length <= 200:
            score += 0.1
        
        # Assurer que le score est entre 0 et 1
        score = max(0.0, min(1.0, score))
        
        return score
    
    def _generate_reason(self, is_relevant: bool, nmap_keywords: list, 
                         non_nmap_keywords: list, score: float) -> str:
        """Génère une raison explicative"""
        
        if is_relevant:
            if not nmap_keywords:
                return f"Query is relevant to NMAP (pattern match, score: {score:.0%})"
            else:
                keywords_str = ", ".join(nmap_keywords[:3])
                if len(nmap_keywords) > 3:
                    keywords_str += f", ... (+{len(nmap_keywords)-3} more)"
                return f"Query is relevant to NMAP (keywords: {keywords_str})"
        else:
            if non_nmap_keywords:
                reason = f"Query appears to be about: {', '.join(non_nmap_keywords[:2])}"
                return f"Query is NOT relevant to NMAP. {reason}"
            else:
                return f"Query is NOT relevant to NMAP (insufficient NMAP keywords)"

# ==================== ASYNC WRAPPER ====================

async def analyze_comprehension(query: str) -> ComprehensionResult:
    """Wrapper async pour l'agent de compréhension"""
    agent = ComprehensionAgent()
    return agent.understand(query)

# ==================== EXAMPLE ====================

if __name__ == "__main__":
    agent = ComprehensionAgent()
    
    # Test queries
    test_queries = [
        "Scan port 80 sur 192.168.1.1",
        "Détector les services sur 192.168.1.100",
        "Scan furtif avec évasion IDS",
        "Bonjour comment allez-vous",
        "Quelle est la meilleure recette de pizza",
        "nmap -sV 192.168.0.0/24",
        "Scan network 10.0.0.0/8",
    ]
    
    print("=" * 80)
    print("COMPREHENSION AGENT - TEST RESULTS")
    print("=" * 80 + "\n")
    
    for query in test_queries:
        result = agent.understand(query)
        status = "✅ RELEVANT" if result.is_relevant else "❌ NOT RELEVANT"
        print(f"Query: {query}")
        print(f"Status: {status}")
        print(f"Reason: {result.reason}")
        print(f"Confidence: {result.confidence:.0%}")
        print(f"Keywords: {result.keywords_found[:5]}")
        print("-" * 80 + "\n")