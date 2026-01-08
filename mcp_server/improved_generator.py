#!/usr/bin/env python3
"""
🔥 IMPROVED GENERATOR - Better port extraction and complexity detection
"""

import re
from typing import Optional

class ImprovedCommandGenerator:
    """
    Enhanced generator with better port extraction and keyword recognition
    """
    
    # Enhanced keyword dictionaries
    HARD_KEYWORDS = [
        'furtif', 'stealth', 'discret', 'dissimul',  # French/English stealth
        'évasion', 'evasion', 'evade', 'bypass',      # Evasion tactics
        'ids', 'ids/ips', 'intrusion',                # IDS/IPS detection
        'fragment', 'fragmenté', 'fragmented',        # Fragmentation
        'spoof', 'usurp', 'falsifi',                  # Spoofing
        'decoy', 'leurre',                            # Decoys
        'timing', 'paranoiac', '-t0', '-t1', '-t2',   # Slow timing
        'syn', 'ack', 'fin', 'xmas', 'null',          # Scan types
        'zombie', 'idle',                              # Advanced scans
    ]
    
    MEDIUM_KEYWORDS = [
        'version', 'service', 'détecte', 'identify',
        'os', 'system', 'operating',
        'script', 'scripte', 'vulnerability', 'vuln',
        'aggressive', '-a', '-a+',
        'full', 'complet', 'complete',
    ]
    
    @staticmethod
    def extract_ports(query: str) -> str:
        """
        Extract port specification from query
        Handles: "port 22", "ports 22,80", "port 22 et 80", etc.
        """
        query_lower = query.lower()
        
        # Match various port patterns
        port_patterns = [
            r'port[s]?\s+([\d,\s\-\.]+?)(?:\s+sur|\s+on|\s+à|$)',  # port 22,80 sur IP
            r'port[s]?\s+([\d,\s\-\.]+?)(?:\s|$)',                    # port 22,80
            r'ports?\s*:?\s*([\d,\s\-\.]+)',                          # port: 22,80
        ]
        
        for pattern in port_patterns:
            match = re.search(pattern, query_lower, re.IGNORECASE)
            if match:
                ports_raw = match.group(1)
                # Clean: replace "et", "and", "ou" with comma
                ports_raw = re.sub(r'\s+(et|and|ou|or)\s+', ',', ports_raw, flags=re.IGNORECASE)
                ports_raw = re.sub(r'\s+', '', ports_raw)  # Remove spaces
                ports_raw = re.sub(r',+', ',', ports_raw)   # Remove double commas
                ports_raw = ports_raw.strip(',')             # Remove leading/trailing commas
                
                if ports_raw:
                    return ports_raw
        
        return "1-65535"
    
    @staticmethod
    def extract_target(query: str) -> str:
        """Extract target IP/hostname from query"""
        # Look for IP addresses (IPv4)
        ip_pattern = r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
        match = re.search(ip_pattern, query)
        if match:
            return match.group()
        
        # Look for hostnames/domains
        domain_pattern = r'\b(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}\b'
        match = re.search(domain_pattern, query, re.IGNORECASE)
        if match:
            return match.group()
        
        # Look for CIDR notation
        cidr_pattern = r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)/\d+\b'
        match = re.search(cidr_pattern, query)
        if match:
            return match.group()
        
        return "192.168.1.0/24"  # Default
    
    @staticmethod
    def detect_complexity(query: str) -> str:
        """
        Detect complexity from keywords
        Better than the ML classifier fallback
        """
        query_lower = query.lower()
        
        # Count hard keywords
        hard_count = sum(1 for kw in ImprovedCommandGenerator.HARD_KEYWORDS 
                        if kw in query_lower)
        
        # Count medium keywords
        medium_count = sum(1 for kw in ImprovedCommandGenerator.MEDIUM_KEYWORDS 
                          if kw in query_lower)
        
        # Decision logic
        if hard_count >= 2:
            return "HARD"
        elif hard_count >= 1:
            return "HARD"  # If even one hard keyword, likely HARD
        elif medium_count >= 2:
            return "MEDIUM"
        elif medium_count >= 1:
            return "MEDIUM"
        else:
            return "EASY"
    
    @classmethod
    def generate_command(cls, query: str, complexity: Optional[str] = None) -> str:
        """
        Generate NMAP command based on query and complexity
        """
        target = cls.extract_target(query)
        ports = cls.extract_ports(query)
        
        # If complexity not specified, detect it
        if complexity is None:
            complexity = cls.detect_complexity(query)
        
        complexity = complexity.upper()
        
        # Build command based on complexity
        if complexity == "HARD":
            return cls._generate_hard(query, target, ports)
        elif complexity == "MEDIUM":
            return cls._generate_medium(query, target, ports)
        else:  # EASY
            return cls._generate_easy(query, target, ports)
    
    @staticmethod
    def _generate_easy(query: str, target: str, ports: str) -> str:
        """Generate EASY command"""
        if 'ping' in query.lower():
            return f"nmap -sn {target}"
        else:
            return f"nmap -p {ports} {target}"
    
    @staticmethod
    def _generate_medium(query: str, target: str, ports: str) -> str:
        """Generate MEDIUM command"""
        options = ["-p", ports]
        query_lower = query.lower()
        
        if any(kw in query_lower for kw in ['version', 'service']):
            options.append("-sV")
        
        if any(kw in query_lower for kw in ['os', 'system']):
            options.append("-O")
        
        if any(kw in query_lower for kw in ['script', 'vulnerability']):
            options.append("--script vuln")
        
        if 'aggressive' in query_lower:
            options.append("-T5")
            options.append("-A")
        elif any(kw in query_lower for kw in ['fast', 'rapide']):
            options.append("-T5")
        else:
            options.append("-T4")
        
        return f"nmap {' '.join(options)} {target}"
    
    @staticmethod
    def _generate_hard(query: str, target: str, ports: str) -> str:
        """Generate HARD command"""
        options = ["-sS"]  # Default: SYN scan (stealth)
        query_lower = query.lower()
        
        # Add stealth/evasion options
        if any(kw in query_lower for kw in ['furtif', 'stealth', 'discret']):
            options.append("-f")  # Fragment packets
            options.append("-T1")  # Paranoid timing
        
        if 'évasion' in query_lower or 'evasion' in query_lower:
            options.append("-f")
            options.append("--spoof-mac 0")
        
        if any(kw in query_lower for kw in ['ids', 'firewall']):
            options.append("-f")
            options.append("--spoof-mac 0")
            options.append("-T0")
        
        if 'decoy' in query_lower or 'leurre' in query_lower:
            options.append("--decoy 192.168.1.1,192.168.1.2")
        
        # Add detection options
        if any(kw in query_lower for kw in ['version', 'service']):
            options.append("-sV")
        
        if any(kw in query_lower for kw in ['os', 'system']):
            options.append("-O")
        
        if any(kw in query_lower for kw in ['script', 'vulnerability']):
            options.append("--script vuln")
        
        # Port specification
        if ports != "1-65535":
            options.extend(["-p", ports])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_options = []
        for opt in options:
            if opt not in seen:
                seen.add(opt)
                unique_options.append(opt)
        
        return f"nmap {' '.join(unique_options)} {target}"


# Test the improved generator
if __name__ == "__main__":
    test_cases = [
        "Scan furtif avec évasion IDS sur 10.0.0.1",
        "scan port 22 sur ip 192.168.124.32",
        "scan port 22, 80 sur ip 192.168.124.32",
        "scan port 22 et 80 sur ip 192.168.124.32",
        "Détecte les services et version sur 192.168.1.1",
        "Scan agressif avec scripts de vulnérabilité sur 10.0.0.0/24",
    ]
    
    print("🧪 TESTING IMPROVED GENERATOR\n")
    print("="*80)
    
    for query in test_cases:
        complexity = ImprovedCommandGenerator.detect_complexity(query)
        ports = ImprovedCommandGenerator.extract_ports(query)
        target = ImprovedCommandGenerator.extract_target(query)
        command = ImprovedCommandGenerator.generate_command(query)
        
        print(f"\n📝 Query: {query}")
        print(f"   Complexity: {complexity}")
        print(f"   Ports: {ports}")
        print(f"   Target: {target}")
        print(f"   Command: {command}")
    
    print("\n" + "="*80)
    print("✅ Testing complete!")