"""
Post-processor intelligent pour corriger les commandes Nmap générées
"""

import re

class NmapCommandProcessor:
    """
    Corrige et améliore les commandes Nmap générées par le modèle
    """
    
    def __init__(self):
        # Services → Ports
        self.service_ports = {
            'ssh': '22',
            'ftp': '21',
            'http': '80',
            'https': '443',
            'smtp': '25',
            'dns': '53',
            'mysql': '3306',
            'rdp': '3389',
            'telnet': '23',
            'snmp': '161'
        }
    
    def process(self, command: str, instruction: str) -> str:
        """
        Traiter et corriger une commande
        
        Args:
            command: Commande générée par le modèle
            instruction: Instruction originale de l'utilisateur
            
        Returns:
            Commande corrigée
        """
        
        # 1. Corriger syntaxe de base
        command = self._fix_syntax(command)
        
        # 2. Ajouter flags manquants basés sur l'instruction
        command = self._add_missing_flags(command, instruction)
        
        # 3. Ajouter ports spécifiques si services mentionnés
        command = self._add_service_ports(command, instruction)
        
        # 4. Nettoyer duplications
        command = self._remove_duplicates(command)
        
        # 5. Ordonner les flags logiquement
        command = self._order_flags(command)
        
        return command
    
    def _fix_syntax(self, command: str) -> str:
        """Corriger erreurs syntaxiques communes"""
        
        # "nmap -O sV" → "nmap -O -sV"
        command = re.sub(r'-O\s+sV', '-O -sV', command)
        command = re.sub(r'-sV\s+O', '-sV -O', command)
        
        # "nmap -p -" → "nmap -p-"
        command = re.sub(r'-p\s+-(?!\d)', '-p-', command)
        
        # Supprimer espaces multiples
        command = re.sub(r'\s+', ' ', command).strip()
        
        # S'assurer que ça commence par nmap
        if not command.startswith('nmap'):
            command = f"nmap {command}"
        
        return command
    
    def _add_missing_flags(self, command: str, instruction: str) -> str:
        """Ajouter flags manquants basés sur l'instruction"""
        
        instruction_lower = instruction.lower()
        
        # OS detection
        if any(word in instruction_lower for word in ['os', 'operating system', 'fingerprint']):
            if '-O' not in command and '-A' not in command:
                # Insérer avant le target
                command = self._insert_flag(command, '-O')
        
        # Version detection
        if any(word in instruction_lower for word in ['version', 'service']):
            if '-sV' not in command and '-A' not in command:
                command = self._insert_flag(command, '-sV')
        
        # Ping scan
        if 'ping' in instruction_lower:
            if '-sn' not in command:
                # Remplacer autres scans par -sn si ping demandé
                command = re.sub(r'-p-?(\s+\d+)?', '', command)
                command = self._insert_flag(command, '-sn')
        
        # Aggressive scan
        if 'aggressive' in instruction_lower:
            if '-A' not in command:
                # Remplacer -O et -sV par -A
                command = command.replace('-O', '').replace('-sV', '')
                command = self._insert_flag(command, '-A')
        
        return command
    
    def _add_service_ports(self, command: str, instruction: str) -> str:
        """Ajouter ports spécifiques si services mentionnés"""
        
        instruction_lower = instruction.lower()
        
        # Détecter services mentionnés
        mentioned_services = []
        for service in self.service_ports.keys():
            if service in instruction_lower:
                mentioned_services.append(service)
        
        if not mentioned_services:
            return command
        
        # Si pas de -p déjà présent
        if not re.search(r'-p\s*[\d,-]+', command) and '-p-' not in command:
            # Ajouter les ports
            ports = [self.service_ports[s] for s in mentioned_services]
            port_spec = ','.join(ports)
            command = self._insert_flag(command, f'-p {port_spec}')
        
        return command
    
    def _insert_flag(self, command: str, flag: str) -> str:
        """Insérer un flag avant le target"""
        
        parts = command.split()
        
        # Trouver le target (dernière partie qui ressemble à une IP)
        target_idx = -1
        for i in range(len(parts) - 1, -1, -1):
            if re.search(r'\d+\.\d+\.\d+\.\d+', parts[i]):
                target_idx = i
                break
        
        if target_idx == -1:
            # Pas de target trouvé, ajouter à la fin
            return f"{command} {flag}"
        
        # Insérer avant le target
        parts.insert(target_idx, flag)
        return ' '.join(parts)
    
    def _remove_duplicates(self, command: str) -> str:
        """Supprimer flags dupliqués"""
        
        parts = command.split()
        seen = set()
        result = []
        
        for part in parts:
            if part not in seen or part.startswith(('192.', '10.', '172.')):
                result.append(part)
                seen.add(part)
        
        return ' '.join(result)
    
    def _order_flags(self, command: str) -> str:
        """Ordonner les flags de manière logique"""
        
        parts = command.split()
        
        # Séparer : nmap, flags, target
        if parts[0] != 'nmap':
            return command
        
        # Trouver target
        target = None
        flags = []
        
        for part in parts[1:]:
            if re.search(r'\d+\.\d+\.\d+\.\d+', part):
                target = part
            else:
                flags.append(part)
        
        # Ordre préféré : scan type, ports, detection, scripts, timing, output
        order_priority = {
            '-sS': 1, '-sT': 1, '-sU': 1, '-sn': 1,
            '-p': 2, '-p-': 2, '-F': 2,
            '-O': 3, '-sV': 3, '-A': 3,
            '--script': 4,
            '-T': 5,
            '-o': 6
        }
        
        def get_priority(flag):
            for key, pri in order_priority.items():
                if flag.startswith(key):
                    return pri
            return 99
        
        flags.sort(key=get_priority)
        
        result = ['nmap'] + flags
        if target:
            result.append(target)
        
        return ' '.join(result)


# ============================================
# TESTS
# ============================================

if __name__ == "__main__":
    processor = NmapCommandProcessor()
    
    tests = [
        ("nmap -O sV 172.16.0.5", "Perform OS detection with version scan on 172.16.0.5"),
        ("nmap -p- 192.168.1.100", "Check if HTTP and HTTPS are open on 192.168.1.100"),
        ("nmap -sV 192.168.0.50", "Scan SSH and FTP services on 192.168.0.50"),
        ("nmap -sn 192.168.1.1", "Full aggressive scan on 192.168.1.1"),
        ("nmap -p- 10.0.0.0/24", "Scan all ports with service detection on 192.168.100.0/24"),
    ]
    
    print("="*70)
    print("🧪 TEST POST-PROCESSOR")
    print("="*70)
    
    for cmd, instr in tests:
        corrected = processor.process(cmd, instr)
        print(f"\n📝 Instruction: {instr}")
        print(f"❌ Before:      {cmd}")
        print(f"✅ After:       {corrected}")