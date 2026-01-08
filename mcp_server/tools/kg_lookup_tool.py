import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from AgentRag.utils import Neo4jKGWithCache

# Initialize KG client (singleton)
_kg_client = None

def get_kg_client():
    global _kg_client
    if _kg_client is None:
        _kg_client = Neo4jKGWithCache()
    return _kg_client

async def kg_lookup(option: str) -> dict:
    """
    Lookup option in Neo4j Knowledge Graph
    
    Args:
        option: Nmap option (e.g., "-sS", "-O")
        
    Returns:
        {
            "flag": "-sS",
            "name": "SYN Scan",
            "description": "...",
            "conflicts_with": [...],
            "commonly_used_with": [...]
        }
    """
    try:
        kg = get_kg_client()
        
        # Get option details
        option_query = f"""
        MATCH (o:Option {{flag: '{option}'}})
        RETURN o.flag as flag, o.name as name, o.description as description
        """
        option_result = kg.cached_query(option_query)
        
        if not option_result:
            return {"error": f"Option {option} not found in KG"}
        
        option_data = option_result[0]
        
        # Get conflicts
        conflicts_query = f"""
        MATCH (o:Option {{flag: '{option}'}})-[:CONFLICTS_WITH]->(c:Option)
        RETURN c.flag as conflict
        """
        conflicts = [r['conflict'] for r in kg.cached_query(conflicts_query)]
        
        # Get common associations
        common_query = f"""
        MATCH (o:Option {{flag: '{option}'}})-[r:COMMONLY_USED_WITH]->(c:Option)
        RETURN c.flag as option, r.frequency as freq
        ORDER BY r.frequency DESC
        LIMIT 5
        """
        commonly_used = [
            {"option": r['option'], "frequency": r['freq']} 
            for r in kg.cached_query(common_query)
        ]
        
        return {
            "flag": option_data['flag'],
            "name": option_data['name'],
            "description": option_data['description'],
            "conflicts_with": conflicts,
            "commonly_used_with": commonly_used
        }
        
    except Exception as e:
        import traceback
        return {
            "error": str(e),
            "error_details": traceback.format_exc()
        }