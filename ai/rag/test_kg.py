# test_kg.py
from neo4j import GraphDatabase

print("🔍 Test du Knowledge Graph NMAP-AI\n")

try:
    driver = GraphDatabase.driver(
        "bolt://localhost:7687",
        auth=("neo4j", "nmap_ai_2024")
    )
    
    with driver.session() as session:
        result = session.run("MATCH (n) RETURN count(n) as count")
        nodes = result.single()["count"]
        
        result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
        rels = result.single()["count"]
        
        print("="*50)
        print("✅ KNOWLEDGE GRAPH IMPORTÉ !")
        print("="*50)
        print(f"\n📊 Statistiques :")
        print(f"   Nœuds     : {nodes}")
        print(f"   Relations : {rels}")
        
        result = session.run("""
            MATCH (p:Port)
            RETURN p.service as service, p.number as port
            ORDER BY p.number
            LIMIT 5
        """)
        
        print(f"\n🔌 Exemples de ports :")
        for record in result:
            print(f"   Port {record['port']:5d} → {record['service']}")
        
        print("\n" + "="*50)
        print("✅ TEST RÉUSSI !")
        print("="*50)
        
    driver.close()
    
except Exception as e:
    print(f"❌ ERREUR : {e}")

input("\nAppuyez sur Entrée...")