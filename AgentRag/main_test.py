# main_test.py
from rag_improved import ImprovedRAG
from self_correction import SelfCorrection

def test_all():
    print("=== PARTIE A : RAG Amélioré ===\n")
    rag = ImprovedRAG()
    
    queries = [
        "Scanne les ports ouverts sur 192.168.1.1 avec détection de version",
        "Fais un scan rapide SYN sur scanme.nmap.org",
        "Détecte l'OS et les services sur 10.0.0.1",
        "Je veux un scan agressif avec scripts sur mon réseau local"
    ]

    generated = []
    for query in queries:
        cmd = rag.generate_command(query)
        print(f"Query : {query}")
        print(f"→ Commande : {cmd}\n")
        generated.append(cmd)
    
    rag.close()

    print("\n=== PARTIE B : Self-Correction ===\n")
    corrector = SelfCorrection()

    test_commands = generated + [
        "nmap -badoption -sS -sU 192.168.1.1",
        "nmap -sV --script unknown 10.0.0.1",
        "nmap -O -sV --version-light scanme.nmap.org"
    ]

    for cmd in test_commands:
        result = corrector.correct(cmd)
        print(f"Original   : {result['original']}")
        print(f"Finale     : {result['final_command']}")
        print(f"Analyse :\n{result['analysis']}")
        print("-" * 80)

    corrector.close()

if __name__ == "__main__":
    test_all()