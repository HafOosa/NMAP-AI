"""
Créer un dataset PARFAITEMENT ÉQUILIBRÉ
avec distribution uniforme des flags
"""

import json
import random

OUTPUT_JSON = "data/nmap_balanced.json"

class BalancedDatasetCreator:
    """Créer dataset équilibré pour chaque type de commande"""
    
    def __init__(self):
        self.targets = [
            "192.168.1.0/24", "192.168.0.0/24", "10.0.0.0/24",
            "172.16.0.0/24", "192.168.100.0/24", "10.10.10.0/24",
            "192.168.1.1", "10.0.0.1", "172.16.0.1"
        ]
        
        # Services avec ports
        self.services = {
            "SSH": "22", "FTP": "21", "HTTP": "80", "HTTPS": "443",
            "SMTP": "25", "DNS": "53", "MySQL": "3306", "RDP": "3389",
            "Telnet": "23", "SNMP": "161"
        }
    
    def create_port_scan_examples(self, n=500):
        """Scans de ports spécifiques"""
        examples = []
        
        instructions = [
            "Scan port {port} on {target}",
            "Check if port {port} is open on {target}",
            "Test {service} on {target}",
            "Probe {service} service on {target}",
            "Scan {service} port on {target}"
        ]
        
        for _ in range(n):
            service = random.choice(list(self.services.keys()))
            port = self.services[service]
            target = random.choice(self.targets)
            
            instr = random.choice(instructions).format(
                port=port, service=service, target=target
            )
            
            examples.append({
                'instruction': instr,
                'input': '',
                'output': f"nmap -p {port} {target}"
            })
        
        return examples
    
    def create_os_detection_examples(self, n=500):
        """OS detection"""
        examples = []
        
        instructions = [
            "Detect operating system on {target}",
            "OS fingerprinting on {target}",
            "Identify OS on {target}",
            "Check what OS is running on {target}",
            "Perform OS detection on {target}"
        ]
        
        for _ in range(n):
            target = random.choice(self.targets)
            instr = random.choice(instructions).format(target=target)
            
            examples.append({
                'instruction': instr,
                'input': '',
                'output': f"nmap -O {target}"
            })
        
        return examples
    
    def create_version_detection_examples(self, n=500):
        """Version detection"""
        examples = []
        
        instructions = [
            "Detect service versions on {target}",
            "Check service versions on {target}",
            "Version scan on {target}",
            "Identify service versions on {target}",
            "Service fingerprinting on {target}"
        ]
        
        for _ in range(n):
            target = random.choice(self.targets)
            instr = random.choice(instructions).format(target=target)
            
            examples.append({
                'instruction': instr,
                'input': '',
                'output': f"nmap -sV {target}"
            })
        
        return examples
    
    def create_ping_scan_examples(self, n=500):
        """Ping scans"""
        examples = []
        
        instructions = [
            "Ping scan on {target}",
            "Host discovery on {target}",
            "Check which hosts are up on {target}",
            "Quick ping scan on {target}",
            "Discover active hosts on {target}"
        ]
        
        for _ in range(n):
            target = random.choice(self.targets)
            instr = random.choice(instructions).format(target=target)
            
            examples.append({
                'instruction': instr,
                'input': '',
                'output': f"nmap -sn {target}"
            })
        
        return examples
    
    def create_all_ports_examples(self, n=300):
        """Scan tous les ports (MOINS d'exemples!)"""
        examples = []
        
        instructions = [
            "Scan all ports on {target}",
            "Full port scan on {target}",
            "Check all 65535 ports on {target}",
            "Complete port scan on {target}"
        ]
        
        for _ in range(n):
            target = random.choice(self.targets)
            instr = random.choice(instructions).format(target=target)
            
            examples.append({
                'instruction': instr,
                'input': '',
                'output': f"nmap -p- {target}"
            })
        
        return examples
    
    def create_combined_examples(self, n=700):
        """Combinaisons - CORRIGÉ"""
        examples = []
        
        # Templates avec service/port
        service_combos = [
            {
                'instruction': "Scan port {port} with version detection on {target}",
                'output': "nmap -p {port} -sV {target}"
            },
            {
                'instruction': "Check {service} and detect OS on {target}",
                'output': "nmap -p {port} -O {target}"
            },
            {
                'instruction': "Scan {service} with OS detection on {target}",
                'output': "nmap -p {port} -O {target}"
            },
            {
                'instruction': "Version scan of {service} on {target}",
                'output': "nmap -p {port} -sV {target}"
            },
        ]
        
        # Templates sans service
        general_combos = [
            {
                'instruction': "Scan all ports with service detection on {target}",
                'output': "nmap -p- -sV {target}"
            },
            {
                'instruction': "OS detection with version scan on {target}",
                'output': "nmap -O -sV {target}"
            },
            {
                'instruction': "Full scan with OS detection on {target}",
                'output': "nmap -p- -O {target}"
            },
            {
                'instruction': "Complete scan with version detection on {target}",
                'output': "nmap -p- -sV {target}"
            },
            {
                'instruction': "Aggressive scan on {target}",
                'output': "nmap -A {target}"
            },
        ]
        
        # Générer moitié service, moitié general
        n_service = n // 2
        n_general = n - n_service
        
        # Avec service
        for _ in range(n_service):
            combo = random.choice(service_combos)
            target = random.choice(self.targets)
            service = random.choice(list(self.services.keys()))
            port = self.services[service]
            
            instr = combo['instruction'].format(
                service=service, port=port, target=target
            )
            output = combo['output'].format(port=port, target=target)
            
            examples.append({
                'instruction': instr,
                'input': '',
                'output': output
            })
        
        # Sans service (général)
        for _ in range(n_general):
            combo = random.choice(general_combos)
            target = random.choice(self.targets)
            
            instr = combo['instruction'].format(target=target)
            output = combo['output'].format(target=target)
            
            examples.append({
                'instruction': instr,
                'input': '',
                'output': output
            })
        
        return examples
    
    def create_balanced_dataset(self):
        """Créer dataset complet équilibré"""
        
        print("\n🔨 CRÉATION DATASET ÉQUILIBRÉ\n")
        
        all_examples = []
        
        # Port scans
        print("  → Port scans (500)...")
        all_examples.extend(self.create_port_scan_examples(500))
        
        # OS detection
        print("  → OS detection (500)...")
        all_examples.extend(self.create_os_detection_examples(500))
        
        # Version detection
        print("  → Version detection (500)...")
        all_examples.extend(self.create_version_detection_examples(500))
        
        # Ping scans
        print("  → Ping scans (500)...")
        all_examples.extend(self.create_ping_scan_examples(500))
        
        # All ports (MOINS!)
        print("  → All ports scan (300)...")
        all_examples.extend(self.create_all_ports_examples(300))
        
        # Combined
        print("  → Combined scans (700)...")
        all_examples.extend(self.create_combined_examples(700))
        
        # Mélanger
        random.shuffle(all_examples)
        
        print(f"\n✅ Total : {len(all_examples)} exemples")
        
        return all_examples


def main():
    creator = BalancedDatasetCreator()
    dataset = creator.create_balanced_dataset()
    
    # Sauvegarder
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Sauvegardé : {OUTPUT_JSON}")
    
    # Statistiques
    from collections import Counter
    flag_counts = Counter()
    
    for item in dataset:
        cmd = item['output']
        if '-O' in cmd:
            flag_counts['-O'] += 1
        if '-sV' in cmd:
            flag_counts['-sV'] += 1
        if '-sn' in cmd:
            flag_counts['-sn'] += 1
        if '-p-' in cmd:
            flag_counts['-p-'] += 1
        if '-p ' in cmd and '-p-' not in cmd:
            flag_counts['-p <port>'] += 1
        if '-A' in cmd:
            flag_counts['-A'] += 1
    
    print("\n📊 DISTRIBUTION DES FLAGS :")
    for flag, count in sorted(flag_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   {flag:15} : {count:4} ({100*count/len(dataset):.1f}%)")
    
    print("\n📋 EXEMPLES :")
    for i in range(5):
        print(f"\n[{i+1}]")
        print(f"  In : {dataset[i]['instruction']}")
        print(f"  Out: {dataset[i]['output']}")


if __name__ == "__main__":
    main()