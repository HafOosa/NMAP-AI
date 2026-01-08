

import re
from typing import Dict, List, Tuple


class SyntaxChecker:
    """Validates Nmap command syntax"""
    
    def __init__(self):
        # Valid Nmap scan types
        self.scan_types = {
            '-sS': 'TCP SYN scan',
            '-sT': 'TCP connect scan',
            '-sU': 'UDP scan',
            '-sA': 'TCP ACK scan',
            '-sW': 'TCP Window scan',
            '-sM': 'TCP Maimon scan',
            '-sN': 'TCP Null scan',
            '-sF': 'TCP FIN scan',
            '-sX': 'TCP Xmas scan',
            '-sY': 'SCTP INIT scan',
            '-sZ': 'SCTP COOKIE-ECHO scan',
            '-sO': 'IP protocol scan',
            '-sV': 'Version detection'
        }
        
        # Valid single-character options
        self.valid_options = {
            '-A': 'Aggressive scan',
            '-O': 'OS detection',
            '-v': 'Verbose',
            '-d': 'Debug',
            '-n': 'No DNS resolution',
            '-R': 'Always resolve DNS',
            '-6': 'IPv6 scan',
            '-F': 'Fast scan',
            '-r': 'Don\'t randomize ports',
            '-Pn': 'Skip host discovery',
            '-PE': 'ICMP echo discovery',
            '-PP': 'ICMP timestamp discovery',
            '-PM': 'ICMP netmask discovery',
            '-PS': 'TCP SYN discovery',
            '-PA': 'TCP ACK discovery',
            '-PU': 'UDP discovery',
            '-PR': 'ARP discovery',
            '-PO': 'IP protocol discovery'
        }
        
        # Valid options with arguments
        self.options_with_args = {
            '-p': 'Port specification',
            '-T': 'Timing template',
            '-oN': 'Normal output',
            '-oX': 'XML output',
            '-oG': 'Grepable output',
            '-oA': 'All output formats',
            '--top-ports': 'Scan top N ports',
            '--script': 'NSE script',
            '--max-retries': 'Max retries',
            '--min-rate': 'Minimum packet rate',
            '--max-rate': 'Maximum packet rate',
            '--host-timeout': 'Host timeout',
            '--scan-delay': 'Scan delay',
            '--max-parallelism': 'Max parallelism',
            '-iL': 'Input from list',
            '-iR': 'Random targets',
            '--exclude': 'Exclude hosts',
            '--excludefile': 'Exclude file'
        }
        
        # Timing templates
        self.timing_templates = ['0', '1', '2', '3', '4', '5']
        
        self.errors = []
        self.warnings = []
    
    def check(self, command: str) -> Dict:
        """
        Main validation function
        
        Args:
            command: Nmap command string
            
        Returns:
            Dictionary with validation results
        """
        self.errors = []
        self.warnings = []
        
        # Basic structure check
        if not command.strip():
            self.errors.append("Empty command")
            return self._build_result(False)
        
        # Must start with 'nmap'
        if not command.strip().startswith('nmap'):
            self.errors.append("Command must start with 'nmap'")
            return self._build_result(False)
        
        # Parse command
        parts = command.split()
        if len(parts) < 2:
            self.errors.append("No target specified")
            return self._build_result(False)
        
        # Extract flags and target
        flags = []
        target = None
        
        i = 1  # Skip 'nmap'
        while i < len(parts):
            part = parts[i]
            
            if part.startswith('-'):
                # Check if it needs an argument
                if part in self.options_with_args:
                    if i + 1 < len(parts) and not parts[i + 1].startswith('-'):
                        flags.append((part, parts[i + 1]))
                        i += 2
                    else:
                        self.errors.append(f"Option {part} requires an argument")
                        i += 1
                else:
                    flags.append((part, None))
                    i += 1
            else:
                # This is the target
                target = part
                i += 1
        
        if not target:
            self.errors.append("No target specified")
        
        # Validate each flag
        self._validate_flags(flags)
        
        # Validate target
        if target:
            self._validate_target(target)
        
        # Validate port specification
        self._validate_ports(flags)
        
        return self._build_result(len(self.errors) == 0)
    
    def _validate_flags(self, flags: List[Tuple[str, str]]):
        """Validate individual flags"""
        scan_types_found = []
        
        for flag, arg in flags:
            # Check if it's a valid flag
            if flag not in self.scan_types and \
               flag not in self.valid_options and \
               flag not in self.options_with_args:
                self.errors.append(f"Unknown flag: {flag}")
                continue
            
            # Check scan types
            if flag in self.scan_types:
                scan_types_found.append(flag)
            
            # Validate timing template
            if flag == '-T' and arg:
                if arg not in self.timing_templates:
                    self.errors.append(f"Invalid timing template: {arg} (must be 0-5)")
            
            # Validate port specification
            if flag == '-p' and arg:
                if not self._is_valid_port_spec(arg):
                    self.errors.append(f"Invalid port specification: {arg}")
        
        # Check for multiple incompatible scan types
        if len(scan_types_found) > 1:
            incompatible = ['-sS', '-sT', '-sU']
            tcp_scans = [s for s in scan_types_found if s in incompatible]
            if len(tcp_scans) > 1:
                self.warnings.append(f"Multiple scan types detected: {', '.join(scan_types_found)}")
    
    def _is_valid_port_spec(self, port_spec: str) -> bool:
        """Validate port specification format"""
        # Examples: 22, 80,443, 1-1000, 1-65535
        if port_spec == '-':
            return True  # All ports
        
        # Split by comma
        ranges = port_spec.split(',')
        for r in ranges:
            if '-' in r:
                # Port range
                try:
                    start, end = r.split('-')
                    start = int(start)
                    end = int(end)
                    if start < 1 or end > 65535 or start > end:
                        return False
                except:
                    return False
            else:
                # Single port
                try:
                    port = int(r)
                    if port < 1 or port > 65535:
                        return False
                except:
                    return False
        return True
    
    def _validate_target(self, target: str):
        """Validate target specification"""
        # IPv4 pattern
        ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}(/\d{1,2})?$'
        # Domain pattern
        domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$'
        
        if not re.match(ipv4_pattern, target) and not re.match(domain_pattern, target):
            # Check if it's IP range like 192.168.1.1-254
            if '-' in target:
                # IP range validation (simplified)
                pass
            else:
                self.warnings.append(f"Target format may be invalid: {target}")
    
    def _validate_ports(self, flags: List[Tuple[str, str]]):
        """Validate port-related options"""
        has_port_spec = any(flag == '-p' for flag, _ in flags)
        has_top_ports = any(flag == '--top-ports' for flag, _ in flags)
        
        if has_port_spec and has_top_ports:
            self.warnings.append("Both -p and --top-ports specified")
    
    def _build_result(self, valid: bool) -> Dict:
        """Build validation result dictionary"""
        return {
            'valid': valid,
            'score': 100 if valid and not self.warnings else (50 if valid else 0),
            'errors': self.errors,
            'warnings': self.warnings,
            'component': 'syntax_checker'
        }


# Test function
if __name__ == "__main__":
    checker = SyntaxChecker()
    
    test_commands = [
        "nmap -sS -p 80,443 192.168.1.1",
        "nmap -sS -sT 192.168.1.1",  # Warning: multiple scans
        "nmap -A -v target.com",
        "nmap -p 99999 target.com",  # Invalid port
        "nmap",  # No target
        "scan -sS target.com"  # Doesn't start with nmap
    ]
    
    for cmd in test_commands:
        print(f"\nTesting: {cmd}")
        result = checker.check(cmd)
        print(f"Valid: {result['valid']}")
        print(f"Score: {result['score']}")
        if result['errors']:
            print(f"Errors: {result['errors']}")
        if result['warnings']:
            print(f"Warnings: {result['warnings']}")