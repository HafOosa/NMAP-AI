"""
Générateur EASY - Templates simples (pas de RAG pour éviter spaCy)
"""
import re

# Templates simples
TEMPLATES = {
    'ping': 'nmap -sn {target}',
    'quick': 'nmap -F {target}',
    'fast': 'nmap -F {target}',
    'basic': 'nmap {target}',
    'version': 'nmap -sV {target}',
    'os': 'nmap -O {target}',
    'ports': 'nmap -p {ports} {target}',
    'all_ports': 'nmap -p- {target}',
}

async def generate_nmap_easy(query: str) -> str:
    """Génération EASY par templates"""
    
    query_lower = query.lower()
    
    # Extraire target
    target_match = re.search(r'(\d+\.\d+\.\d+\.\d+(?:/\d+)?)', query)
    target = target_match.group(1) if target_match else '192.168.1.1'
    
    # Détecter intent
    if 'ping' in query_lower:
        return TEMPLATES['ping'].format(target=target)
    elif any(w in query_lower for w in ['quick', 'fast']):
        return TEMPLATES['quick'].format(target=target)
    elif 'version' in query_lower or 'service' in query_lower:
        return TEMPLATES['version'].format(target=target)
    elif 'os' in query_lower:
        return TEMPLATES['os'].format(target=target)
    elif 'all ports' in query_lower or 'all 65535' in query_lower:
        return TEMPLATES['all_ports'].format(target=target)
    elif 'port' in query_lower:
        # Extraire numéros de ports
        ports_match = re.findall(r'\b\d+\b', query)
        if ports_match:
            ports = ','.join(ports_match)
            return TEMPLATES['ports'].format(ports=ports, target=target)
        return TEMPLATES['basic'].format(target=target)
    else:
        return TEMPLATES['basic'].format(target=target)