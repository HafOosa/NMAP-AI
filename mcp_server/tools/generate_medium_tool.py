"""
Générateur MEDIUM - MediumGeneratorAgent
"""
import sys
from pathlib import Path

# Setup paths
project_root = Path(__file__).parent.parent.parent
agents_path = project_root / "AgentModels" / "agents"
sys.path.insert(0, str(agents_path))

# Import direct
try:
    from generator_medium_agent import MediumGeneratorAgent
    _agent = None
    
    def get_agent():
        global _agent
        if _agent is None:
            _agent = MediumGeneratorAgent()
        return _agent
    
    AGENT_AVAILABLE = True
except Exception as e:
    print(f"⚠️ MediumGeneratorAgent not available: {e}")
    AGENT_AVAILABLE = False

async def generate_nmap_medium(query: str) -> str:
    """Génère commande MEDIUM via T5-small + LoRA"""
    
    if not AGENT_AVAILABLE:
        return f"nmap -sV 192.168.1.1  # Error: Agent not available"
    
    try:
        agent = get_agent()
        command = agent.generate(query)
        return command
    except Exception as e:
        import traceback
        return f"nmap -sV 192.168.1.1  # Error: {str(e)}\n# {traceback.format_exc()}"