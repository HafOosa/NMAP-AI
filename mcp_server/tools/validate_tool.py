"""
Validation - Utilise AgentValidator (déjà fonctionnel!)
"""
import sys
from pathlib import Path

# Setup paths
project_root = Path(__file__).parent.parent.parent
validator_path = project_root / "AgentValidator"
validators_path = validator_path / "validators"

sys.path.insert(0, str(project_root))
sys.path.insert(0, str(validator_path))
sys.path.insert(0, str(validators_path))

try:
    from AgentValidator.validator import NmapValidator
    _validator = None
    
    def get_validator():
        global _validator
        if _validator is None:
            _validator = NmapValidator()
        return _validator
    
    VALIDATOR_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Validator not available: {e}")
    VALIDATOR_AVAILABLE = False

async def validate_command(command: str) -> dict:
    """Valide une commande Nmap"""
    
    if not VALIDATOR_AVAILABLE:
        return {
            "valid": False,
            "score": 0,
            "grade": "F",
            "errors": ["Validator not available"],
            "warnings": [],
            "suggestions": []
        }
    
    try:
        validator = get_validator()
        result = validator.validate_single_command(command, verbose=False)
        return result
    except Exception as e:
        import traceback
        return {
            "valid": False,
            "score": 0,
            "grade": "F",
            "errors": [str(e)],
            "warnings": [],
            "suggestions": [],
            "error_details": traceback.format_exc()
        }