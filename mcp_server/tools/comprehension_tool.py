"""
comprehension_tool.py - Outil NMAP pour le Comprehension Agent
À placer dans: mcp_server/tools/comprehension_tool.py
"""

import sys
import asyncio
from pathlib import Path

# Setup paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from comprehension_agent import ComprehensionAgent, analyze_comprehension
    AGENT_AVAILABLE = True
except Exception as e:
    print(f"Warning: ComprehensionAgent not available: {e}")
    AGENT_AVAILABLE = False

async def analyze_query_relevance(query: str) -> dict:
    """
    Analyse une requête pour vérifier si elle est pertinente pour NMAP
    
    Returns:
        dict: {
            'is_relevant': bool,
            'reason': str,
            'confidence': float (0-1),
            'keywords': list
        }
    """
    
    if not AGENT_AVAILABLE:
        # Fallback simple
        return {
            'is_relevant': 'nmap' in query.lower() or 'scan' in query.lower(),
            'reason': 'Simple keyword check (agent not available)',
            'confidence': 0.5,
            'keywords': []
        }
    
    try:
        result = await analyze_comprehension(query)
        
        return {
            'is_relevant': result.is_relevant,
            'reason': result.reason,
            'confidence': result.confidence,
            'keywords': result.keywords_found
        }
    
    except Exception as e:
        print(f"Error in analyze_query_relevance: {e}")
        return {
            'is_relevant': False,
            'reason': f'Error: {str(e)}',
            'confidence': 0.0,
            'keywords': []
        }

# ==================== SYNC WRAPPER ====================

def understand_query(query: str) -> dict:
    """Sync wrapper pour l'agent de compréhension"""
    try:
        agent = ComprehensionAgent()
        result = agent.understand(query)
        
        return {
            'is_relevant': result.is_relevant,
            'reason': result.reason,
            'confidence': result.confidence,
            'keywords': result.keywords_found
        }
    except Exception as e:
        return {
            'is_relevant': False,
            'reason': f'Error: {str(e)}',
            'confidence': 0.0,
            'keywords': []
        }