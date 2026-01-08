"""
Générer dataset HARD avec commandes complexes d'évasion IDS/Firewall
"""

import json
import random

OUTPUT_JSON = "data/nmap_hard_dataset.json"

class HardDatasetCreator:
    """Créer dataset pour scans complexes et évasion"""
    
    def __init__(self):
        self.targets = [
            "192.168.1.0/24", "10.0.0.0/24", "172.16.0.0/24",
            "192.168.100.0/24", "192.168.1.1", "10.0.0.1"
        ]
        
        self.services = ['HTTP', 'HTTPS', 'SSH', 'FTP', 'MySQL', 'RDP']
        self.service_ports = {
            'HTTP': '80', 'HTTPS': '443', 'SSH': '22',
            'FTP': '21', 'MySQL': '3306', 'RDP': '3389'
        }
    
    def create_stealth_scans(self, n=300):
        """Scans furtifs avec timing lent"""
        examples = []
        
        instructions = [
            "Stealthy scan of {target} with slow timing",
            "Covert scan on {target} to avoid detection",
            "Sneaky scan of {target} using paranoid timing",
            "Silent scan of {target} with minimal footprint",
            "Low-profile scan on {target} evading IDS",
        ]
        
        for _ in range(n):
            target = random.choice(self.targets)
            instr = random.choice(instructions).format(target=target)
            timing = random.choice(['-T0', '-T1', '-T2'])
            
            examples.append({
                'instruction': instr,
                'input': '',
                'output': f"nmap -sS {timing} {target}"
            })
        
        return examples
    
    def create_fragmentation_scans(self, n=300):
        """Scans avec fragmentation"""
        examples = []
        
        instructions = [
            "Fragmented scan of {target} to bypass firewall",
            "Fragment packets when scanning {target}",
            "Use packet fragmentation on {target}",
            "Evade firewall on {target} using fragmentation",
            "Bypass IDS on {target} with fragmented packets",
        ]
        
        for _ in range(n):
            target = random.choice(self.targets)
            instr = random.choice(instructions).format(target=target)
            
            examples.append({
                'instruction': instr,
                'input': '',
                'output': f"nmap -f {target}"
            })
        
        return examples
    
    def create_decoy_scans(self, n=300):
        """Scans avec decoys"""
        examples = []
        
        instructions = [
            "Scan {target} using decoy hosts",
            "Hide scan origin on {target} with decoys",
            "Use multiple decoys when scanning {target}",
            "Mask real IP when probing {target}",
            "Decoy scan to confuse IDS on {target}",
        ]
        
        for _ in range(n):
            target = random.choice(self.targets)
            instr = random.choice(instructions).format(target=target)
            decoys = random.choice(['RND:5', 'RND:10', 'ME'])
            
            examples.append({
                'instruction': instr,
                'input': '',
                'output': f"nmap -D {decoys} {target}"
            })
        
        return examples
    
    def create_spoofing_scans(self, n=200):
        """Scans avec spoofing"""
        examples = []
        
        instructions = [
            "Spoof source address when scanning {target}",
            "Hide source IP while probing {target}",
            "Use spoofed MAC address on {target}",
            "Mask identity when scanning {target}",
        ]
        
        for _ in range(n):
            target = random.choice(self.targets)
            instr = random.choice(instructions).format(target=target)
            
            if random.random() > 0.5:
                examples.append({
                    'instruction': instr,
                    'input': '',
                    'output': f"nmap --spoof-mac 0 {target}"
                })
            else:
                examples.append({
                    'instruction': instr,
                    'input': '',
                    'output': f"nmap -S 10.0.0.99 {target}"
                })
        
        return examples
    
    def create_udp_scans(self, n=200):
        """Scans UDP complexes"""
        examples = []
        
        instructions = [
            "UDP scan on {target} with stealth",
            "Scan UDP ports on {target} slowly",
            "Covert UDP scan of {target}",
            "UDP scan with evasion on {target}",
        ]
        
        for _ in range(n):
            target = random.choice(self.targets)
            instr = random.choice(instructions).format(target=target)
            timing = random.choice(['-T0', '-T1', '-T2'])
            
            examples.append({
                'instruction': instr,
                'input': '',
                'output': f"nmap -sU {timing} {target}"
            })
        
        return examples
    
    def create_combined_evasion(self, n=400):
        """Combinaisons complexes d'évasion"""
        examples = []
        
        combinations = [
            {
                'instruction': "Complete stealth scan of {target} with fragmentation and decoys",
                'output': "nmap -sS -f -D RND:10 -T1 {target}"
            },
            {
                'instruction': "Advanced evasion scan on {target} bypassing IDS",
                'output': "nmap -sS -f --data-length 25 -T0 {target}"
            },
            {
                'instruction': "Multi-layer evasion scan of {target}",
                'output': "nmap -sS -f -D RND:5 --randomize-hosts {target}"
            },
            {
                'instruction': "Covert scan with maximum stealth on {target}",
                'output': "nmap -sS -f -T0 --max-retries 1 {target}"
            },
            {
                'instruction': "IDS evasion scan of {service} on {target}",
                'output': "nmap -p {port} -sS -f -T1 {target}"
            },
            {
                'instruction': "Firewall bypass scan on {target} with spoofing",
                'output': "nmap -sS --spoof-mac 0 -D RND:10 {target}"
            },
        ]
        
        for _ in range(n):
            combo = random.choice(combinations)
            target = random.choice(self.targets)
            
            if '{service}' in combo['instruction']:
                service = random.choice(self.services)
                port = self.service_ports[service]
                instr = combo['instruction'].format(service=service, target=target)
                output = combo['output'].format(port=port, target=target)
            else:
                instr = combo['instruction'].format(target=target)
                output = combo['output'].format(target=target)
            
            examples.append({
                'instruction': instr,
                'input': '',
                'output': output
            })
        
        return examples
    
    def create_dataset(self):
        """Créer dataset complet HARD"""
        
        print("\n🔥 CRÉATION DATASET HARD (ÉVASION)\n")
        
        all_examples = []
        
        print("  → Stealth scans (300)...")
        all_examples.extend(self.create_stealth_scans(300))
        
        print("  → Fragmentation (300)...")
        all_examples.extend(self.create_fragmentation_scans(300))
        
        print("  → Decoy scans (300)...")
        all_examples.extend(self.create_decoy_scans(300))
        
        print("  → Spoofing (200)...")
        all_examples.extend(self.create_spoofing_scans(200))
        
        print("  → UDP scans (200)...")
        all_examples.extend(self.create_udp_scans(200))
        
        print("  → Combined evasion (400)...")
        all_examples.extend(self.create_combined_evasion(400))
        
        random.shuffle(all_examples)
        
        print(f"\n✅ Total : {len(all_examples)} exemples")
        
        return all_examples


def main():
    creator = HardDatasetCreator()
    dataset = creator.create_dataset()
    
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Sauvegardé : {OUTPUT_JSON}")
    
    from collections import Counter
    flag_counts = Counter()
    
    for item in dataset:
        cmd = item['output']
        for flag in ['-sS', '-sU', '-f', '-D', '-T0', '-T1', '-T2', '--spoof-mac', '-S']:
            if flag in cmd:
                flag_counts[flag] += 1
    
    print("\n📊 DISTRIBUTION FLAGS HARD :")
    for flag, count in sorted(flag_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   {flag:15} : {count:4} ({100*count/len(dataset):.1f}%)")
    
    print("\n📋 EXEMPLES :")
    for i in range(5):
        print(f"\n[{i+1}]")
        print(f"  In : {dataset[i]['instruction']}")
        print(f"  Out: {dataset[i]['output']}")


if __name__ == "__main__":
    main()