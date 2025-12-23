import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

print("\n" + "="*60)
print("TEST 6 : WORKFLOW COMPLET")
print("="*60)

try:
    from agents.generator_medium_agent import MediumGeneratorAgent
    from agents.command_processor import NmapCommandProcessor
    
    print("→ Chargement des agents...\n")
    agent = MediumGeneratorAgent()
    processor = NmapCommandProcessor()
    
    # Tests end-to-end
    queries = [
        "Scan port 22 on 192.168.1.0/24",
        "Detect OS version on 10.0.0.1",
        "Ping scan on 172.16.0.0/24"
    ]
    
    success = 0
    
    for query in queries:
        print(f"Query: {query}")
        
        # Génération
        cmd = agent.generate(query)
        
        # Post-processing
        cmd = processor.process(cmd, query)
        
        print(f"  → {cmd}")
        
        if cmd.startswith("nmap"):
            print("  ✅ OK\n")
            success += 1
        else:
            print("  ⚠️  Suspect\n")
    
    print("="*60)
    rate = (success / len(queries)) * 100
    print(f"Taux de réussite : {rate:.0f}%")
    
    if rate >= 80:
        print("✅ SYSTÈME COMPLET FONCTIONNE")
    elif rate >= 50:
        print("⚠️  SYSTÈME FONCTIONNE PARTIELLEMENT")
    else:
        print("❌ PROBLÈMES DÉTECTÉS")
        
except Exception as e:
    print(f"\n❌ ERREUR : {e}")