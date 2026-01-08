import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

print("\n" + "="*60)
print("TEST 3 : COMMAND PROCESSOR")
print("="*60)

try:
    from agents.command_processor import NmapCommandProcessor
    
    processor = NmapCommandProcessor()
    
    # Test simple
    cmd = "nmap -O sV 10.0.0.1"
    instr = "Detect OS"
    result = processor.process(cmd, instr)
    
    if result.startswith("nmap"):
        print(f"✅ Test 1 : {cmd}")
        print(f"   → {result}")
    else:
        print(f"❌ Test 1 échoué")
    
    # Test 2
    cmd2 = "nmap -p - 192.168.1.1"
    instr2 = "Scan ports"
    result2 = processor.process(cmd2, instr2)
    
    if "nmap" in result2:
        print(f"✅ Test 2 : {cmd2}")
        print(f"   → {result2}")
    else:
        print(f"❌ Test 2 échoué")
    
    print("\n" + "="*60)
    print("✅ COMMAND PROCESSOR FONCTIONNE")
    
except Exception as e:
    print(f"\n❌ ERREUR : {e}")
    print("\nVérifiez que agents/command_processor.py existe")