"""
Test simple du modèle Medium – SANS scoring
Affiche uniquement :
- Instruction
- Commande générée
Tu valides manuellement.
"""

import sys
import os

# Ajout du path du projet
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.generator_medium_agent import MediumGeneratorAgent


def main():
    print("="*70)
    print("🔍 TEST SIMPLE DU MODÈLE MEDIUM".center(70))
    print("="*70)

    agent = MediumGeneratorAgent()

    # Liste de tests — tu peux en ajouter
    tests = [
        "Scan port 22 on 192.168.1.0/24",
        "Detect OS version on 10.0.0.1",
        "Check all ports on 172.16.0.0/24",
        "Scan all ports with service detection on 192.168.100.0/24",
        "Run a quick ping scan on 10.10.10.0/24",
        "Check if HTTP and HTTPS are open on 192.168.1.100",
        "Perform OS detection with version scan on 172.16.0.5",
        "Scan SSH and FTP services on 192.168.0.50",
        "Quick scan of top 100 ports on 10.0.0.0/24",
        "Full aggressive scan on 192.168.1.1"
    ]

    for i, instruction in enumerate(tests, 1):
        print("\n" + "-"*70)
        print(f"Test {i}/{len(tests)}")
        print("-"*70)
        print(f"📝 Instruction : {instruction}")

        try:
            generated = agent.generate(instruction)
            print(f"💻 Commande générée : {generated}")

        except Exception as e:
            print(f"❌ ERREUR : {e}")

    print("\n" + "="*70)
    print("Fin du test (analyse manuelle requise)".center(70))
    print("="*70)


if __name__ == "__main__":
    main()
