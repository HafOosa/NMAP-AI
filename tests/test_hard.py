"""
Tests complets agent HARD avec évaluation qualitative des techniques d'évasion
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.generator_hard_agent import HardGeneratorAgent


def evaluate_hard_command(generated, instruction):
    """Fournit un diagnostic textuel (sans score) sur la qualité des techniques d'évasion"""

    feedback = []
    instr_lower = instruction.lower()

    # Base: nmap
    if generated.startswith('nmap'):
        feedback.append("✅ Commence par 'nmap'")
    else:
        feedback.append("❌ Ne commence pas par 'nmap'")

    # Cible présente
    import re
    if re.search(r'\d+\.\d+\.\d+\.\d+', generated):
        feedback.append("✅ Target détectée")
    else:
        feedback.append("❌ Pas de target détectée")

    # Timing lent
    if 'stealth' in instr_lower or 'covert' in instr_lower or 'sneaky' in instr_lower:
        if any(t in generated for t in ['-T0', '-T1', '-T2']):
            feedback.append("✅ Timing lent (évasion IDS)")
        else:
            feedback.append("❌ Timing lent manquant")

    # Fragmentation
    if 'fragment' in instr_lower or 'fragmented' in instr_lower:
        if '-f' in generated:
            feedback.append("✅ Fragmentation (-f) détectée")
        else:
            feedback.append("❌ Fragmentation (-f) manquante")

    # Decoys
    if 'decoy' in instr_lower or 'hide' in instr_lower:
        if '-D' in generated:
            feedback.append("✅ Utilisation de decoys (-D)")
        else:
            feedback.append("❌ Option -D manquante")

    # UDP
    if 'udp' in instr_lower:
        if '-sU' in generated:
            feedback.append("✅ Scan UDP (-sU)")
        else:
            feedback.append("❌ -sU manquant pour UDP")

    # Spoofing
    if 'spoof' in instr_lower or 'mask' in instr_lower:
        if any(f in generated for f in ['--spoof-mac', '-S']):
            feedback.append("✅ Spoofing détecté (MAC/IP)")
        else:
            feedback.append("❌ Spoofing manquant")

    # Combinaisons complexes
    evasion_flags = ['-T0', '-T1', '-T2', '-f', '-D', '--spoof-mac', '-S']
    detected = [f for f in evasion_flags if f in generated]

    if len(detected) >= 3:
        feedback.append(f"🔷 Combinaison multiple de techniques d'évasion ({len(detected)})")
    elif len(detected) == 0:
        feedback.append("❗ Aucune technique d'évasion détectée")

    return feedback


def main():
    print("="*70)
    print("🔥 TEST AGENT HARD — ÉVALUATION QUALITATIVE".center(70))
    print("="*70)

    agent = HardGeneratorAgent()

    tests = [
        "Stealthy scan of 192.168.1.0/24 with slow timing",
        "Fragment packets when scanning 10.0.0.0/24",
        "Use decoy hosts on 172.16.0.0/24",
        "Covert UDP scan on 192.168.100.0/24",
        "Spoof source address on 10.10.10.0/24",
        "Complete stealth with fragmentation and decoys on 192.168.1.1",
        "Maximum IDS evasion on 172.16.0.5",
        "Bypass firewall with all evasion techniques on 10.0.0.1",
        "Sneaky scan with minimal footprint on 192.168.0.0/24",
        "Advanced evasion scan bypassing IDS on 10.0.0.0/24"
    ]

    for i, instr in enumerate(tests, 1):
        print(f"\n{'─'*70}")
        print(f"Test {i}/{len(tests)}")
        print(f"{'─'*70}")
        print(f"📝 Instruction: {instr}")

        try:
            generated = agent.generate(instr)
            print(f"💻 Commande générée : {generated}")

            feedback = evaluate_hard_command(generated, instr)

            print("\n🔍 Analyse :")
            for fb in feedback:
                print(f"   - {fb}")

        except Exception as e:
            print(f"❌ ERREUR: {e}")

    print("\n" + "="*70)
    print("🔚 FIN DES TESTS HARD — ANALYSE QUALITATIVE".center(70))
    print("="*70)
    print("\n💡 Note : L'utilisation de techniques d'évasion doit être éthique et légale.")


if __name__ == "__main__":
    main()
