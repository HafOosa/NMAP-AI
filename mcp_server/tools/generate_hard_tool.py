"""
Générateur HARD - HardGeneratorAgent CORRIGE
"""
import sys
from pathlib import Path

# Setup paths
project_root = Path(__file__).parent.parent.parent
agents_path = project_root / "AgentModels" / "agents"
sys.path.insert(0, str(agents_path))

# Import direct
try:
    from generator_hard_agent import HardGeneratorAgent
    _agent = None
    
    def get_agent():
        global _agent
        if _agent is None:
            _agent = HardGeneratorAgent()
        return _agent
    
    AGENT_AVAILABLE = True
except Exception as e:
    print(f"Warning: HardGeneratorAgent not available: {e}")
    AGENT_AVAILABLE = False

async def generate_nmap_hard(query: str) -> str:
    """Génère commande HARD via Diffusion (IDS evasion)"""
    
    if not AGENT_AVAILABLE:
        # Fallback command if agent not available
        return "nmap -sS -T1 -f 192.168.1.1"
    
    try:
        agent = get_agent()
        result = agent.generate(query)
        
        # Validation: S'assurer que c'est une string
        if result is None:
            return "nmap -sS -T1 -f 192.168.1.1"
        
        # Convertir en string si nécessaire
        command = str(result).strip()
        
        # Vérifier que ce n'est pas "self" ou autre garbage
        if not command or command == "self" or command == "<generator_hard_agent.HardGeneratorAgent object" in command or not command.startswith("nmap"):
            # Si mauvais résultat, utiliser fallback
            print(f"Warning: Invalid command returned: {command}")
            return "nmap -sS -T1 -f 192.168.1.1"
        
        return command
        
    except Exception as e:
        print(f"Error in generate_nmap_hard: {e}")
        import traceback
        traceback.print_exc()
        # Fallback command
        return "nmap -sS -T1 -f 192.168.1.1"