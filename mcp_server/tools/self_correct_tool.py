import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from AgentRag.self_correction import SelfCorrection

# Initialize corrector (singleton)
_corrector = None

def get_corrector():
    global _corrector
    if _corrector is None:
        _corrector = SelfCorrection()
    return _corrector

async def self_correct_command(command: str) -> dict:
    """
    Self-correct invalid Nmap command
    
    Args:
        command: Potentially invalid command
        
    Returns:
        {
            "original": "...",
            "final_command": "...",
            "iterations": 2,
            "analysis": "..."
        }
    """
    try:
        corrector = get_corrector()
        result = corrector.correct(command)
        return result
    except Exception as e:
        import traceback
        return {
            "original": command,
            "final_command": command,
            "iterations": 0,
            "analysis": f"Error: {str(e)}",
            "error_details": traceback.format_exc()
        }