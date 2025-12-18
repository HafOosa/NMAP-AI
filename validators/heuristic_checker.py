from typing import Dict, List


class HeuristicChecker:
    """Validates Nmap commands against best practices"""
    
    def __init__(self):
        self.warnings = []
        self.suggestions = []
    
    def check(self, command: str) -> Dict:
        """
        Check command against heuristics and best practices
        
        Args:
            command: Nmap command string
            
        Returns:
            Dictionary with heuristic validation results
        """
        self.warnings = []
        self.suggestions = []
        
        parts = command.split()
        flags = [p for p in parts if p.startswith('-')]
        
        # Run all heuristic checks
        self._check_timing(flags)
        self._check_verbosity(flags)
        self._check_aggressive_scan(flags)
        self._check_port_specification(flags, parts)
        self._check_stealth(flags)
        self._check_output_format(flags)
        self._check_version_detection(flags)
        self._check_os_detection(flags)
        self._check_script_usage(flags)
        
        # Calculate score
        score = self._calculate_heuristic_score()
        
        return {
            'valid': len(self.warnings) < 3,  # Too many warnings = invalid
            'score': score,
            'errors': [],
            'warnings': self.warnings,
            'suggestions': self.suggestions,
            'component': 'heuristic_checker'
        }
    
    def _check_timing(self, flags: List[str]):
        """Check timing template usage"""
        has_timing = any('-T' in f for f in flags)
        has_aggressive = '-A' in flags
        
        if not has_timing and has_aggressive:
            self.warnings.append("Using -A without timing template may be slow")
            self.suggestions.append("Add -T4 for faster scanning")
        
        # Check for too aggressive timing
        if '-T5' in flags:
            self.warnings.append("T5 timing is very aggressive and may cause issues")
            self.suggestions.append("Consider using -T4 instead")
        
        # Check for too slow timing
        if '-T0' in flags or '-T1' in flags:
            self.warnings.append("Very slow timing template detected")
            self.suggestions.append("This scan will take a very long time")
    
    def _check_verbosity(self, flags: List[str]):
        """Check verbosity settings"""
        verbose_count = sum(1 for f in flags if f.startswith('-v'))
        
        if verbose_count == 0:
            self.suggestions.append("Add -v for verbose output to track progress")
        
        if verbose_count > 2:
            self.warnings.append("Too many verbose flags may clutter output")
    
    def _check_aggressive_scan(self, flags: List[str]):
        """Check aggressive scan usage"""
        if '-A' in flags:
            # -A includes -O, -sV, -sC, --traceroute
            redundant = []
            if '-O' in flags:
                redundant.append('-O')
            if '-sV' in flags:
                redundant.append('-sV')
            if '--script' in ' '.join(flags):
                redundant.append('--script')
            
            if redundant:
                self.warnings.append(
                    f"Redundant flags with -A: {', '.join(redundant)} "
                    "(already included in aggressive scan)"
                )
    
    def _check_port_specification(self, flags: List[str], parts: List[str]):
        """Check port specification best practices"""
        has_port = any('-p' in f for f in flags)
        has_top_ports = any('--top-ports' in f for f in flags)
        has_fast = '-F' in flags
        
        if not has_port and not has_top_ports and not has_fast:
            self.suggestions.append(
                "No port specification detected. "
                "Consider using -F (fast), -p (specific ports), or --top-ports"
            )
        
        # Check for scanning all ports
        if '-p-' in ' '.join(parts) or '-p 1-65535' in ' '.join(parts):
            self.warnings.append(
                "Scanning all 65535 ports will take a very long time"
            )
            self.suggestions.append("Consider scanning specific ports or use --top-ports")
    
    def _check_stealth(self, flags: List[str]):
        """Check stealth scan practices"""
        if '-sS' in flags:
            # SYN scan is stealthy
            if '-v' in flags or '-vv' in flags:
                self.suggestions.append(
                    "Using verbose mode may reduce stealth benefits"
                )
        
        if '-sT' in flags:
            self.suggestions.append(
                "-sT (TCP connect) is not stealthy. Consider -sS if you have privileges"
            )
    
    def _check_output_format(self, flags: List[str]):
        """Check output format specification"""
        output_flags = [f for f in flags if f.startswith('-o')]
        
        if not output_flags:
            self.suggestions.append(
                "No output format specified. Consider using -oN (normal) or -oA (all formats)"
            )
        
        if len(output_flags) > 3:
            self.warnings.append("Too many output formats specified")
    
    def _check_version_detection(self, flags: List[str]):
        """Check version detection usage"""
        if '-sV' in flags:
            has_timing = any('-T' in f for f in flags)
            if not has_timing:
                self.suggestions.append(
                    "Version detection (-sV) can be slow. Consider adding -T4"
                )
    
    def _check_os_detection(self, flags: List[str]):
        """Check OS detection usage"""
        if '-O' in flags:
            self.suggestions.append(
                "OS detection requires root/admin privileges"
            )
            
            if '-Pn' in flags:
                self.warnings.append(
                    "OS detection with -Pn (skip ping) may be less accurate"
                )
    
    def _check_script_usage(self, flags: List[str]):
        """Check NSE script usage"""
        script_flags = [f for f in flags if '--script' in f]
        
        if script_flags:
            # Check for dangerous scripts
            dangerous_scripts = ['broadcast', 'dos', 'exploit', 'external', 'fuzzer']
            for script in script_flags:
                for dangerous in dangerous_scripts:
                    if dangerous in script.lower():
                        self.warnings.append(
                            f"Potentially dangerous script detected: {script}"
                        )
    
    def _calculate_heuristic_score(self) -> int:
        """Calculate overall heuristic score"""
        base_score = 100
        
        # Deduct points for warnings
        score = base_score - (len(self.warnings) * 15)
        
        # Deduct fewer points for suggestions
        score -= (len(self.suggestions) * 5)
        
        return max(0, min(100, score))


# Test function
if __name__ == "__main__":
    checker = HeuristicChecker()
    
    test_commands = [
        "nmap -sS -p 80,443 -T4 -v 192.168.1.1",       # Good command
        "nmap -A 192.168.1.1",                          # Missing timing
        "nmap -sS -p- 192.168.1.1",                     # All ports warning
        "nmap -sT -v -vv -vvv target.com",              # Too verbose
        "nmap -A -O -sV target.com",                    # Redundant flags
        "nmap -T5 -sS target.com"                       # Too aggressive
    ]
    
    for cmd in test_commands:
        print(f"\n{'='*60}")
        print(f"Testing: {cmd}")
        print(f"{'='*60}")
        result = checker.check(cmd)
        print(f"Valid: {result['valid']}")
        print(f"Score: {result['score']}")
        
        if result['warnings']:
            print(f"\n⚠️  Warnings ({len(result['warnings'])}):")
            for warning in result['warnings']:
                print(f"  - {warning}")
        
        if result['suggestions']:
            print(f"\n💡 Suggestions ({len(result['suggestions'])}):")
            for suggestion in result['suggestions']:
                print(f"  - {suggestion}")