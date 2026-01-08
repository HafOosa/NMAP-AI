import subprocess
import re
import time
from typing import Dict, Optional


class DockerSandbox:
    """
    Safe sandbox for testing Nmap commands
    Uses Docker container or simulation mode
    """
    
    def __init__(self, mode: str = 'simulate'):
        """
        Initialize sandbox
        
        Args:
            mode: 'simulate' (safe, no real scanning) or 'docker' (use container)
        """
        self.mode = mode
        self.safe_targets = [
            'scanme.nmap.org',  # Official Nmap test target
            '127.0.0.1',         # Localhost
            'localhost'
        ]
        
        if mode == 'docker':
            self._check_docker()
        
        print(f"✅ Docker Sandbox initialized (mode: {mode})")
    
    def _check_docker(self):
        """Check if Docker is available"""
        try:
            result = subprocess.run(
                ['docker', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                print("⚠️  Docker not available, falling back to simulate mode")
                self.mode = 'simulate'
        except Exception as e:
            print(f"⚠️  Docker not available: {e}, using simulate mode")
            self.mode = 'simulate'
    
    def execute(self, command: str, timeout: int = 30) -> Dict:
        """
        Execute or simulate Nmap command
        
        Args:
            command: Nmap command string
            timeout: Maximum execution time in seconds
            
        Returns:
            Execution result with success status and output
        """
        # Safety checks
        if not self._is_safe_command(command):
            return {
                'success': False,
                'error': 'Unsafe command detected',
                'output': '',
                'execution_time': 0
            }
        
        if self.mode == 'simulate':
            return self._simulate_execution(command)
        else:
            return self._docker_execution(command, timeout)
    
    def _is_safe_command(self, command: str) -> bool:
        """
        Check if command is safe to execute
        
        Args:
            command: Command to check
            
        Returns:
            True if safe, False otherwise
        """
        # Must start with nmap
        if not command.strip().startswith('nmap'):
            return False
        
        # Block dangerous flags
        dangerous_flags = [
            '--script exploit',
            '--script brute',
            '--script dos',
            '-oS',  # Script kiddie output
            '&',    # Command chaining
            '|',    # Piping
            ';',    # Command separator
            '`',    # Command substitution
            '$('    # Command substitution
        ]
        
        for flag in dangerous_flags:
            if flag in command.lower():
                return False
        
        # Check target is safe (for real execution)
        if self.mode == 'docker':
            target = self._extract_target(command)
            if target and not self._is_safe_target(target):
                return False
        
        return True
    
    def _extract_target(self, command: str) -> Optional[str]:
        """Extract target from command"""
        parts = command.split()
        # Target is usually the last part
        if len(parts) > 1:
            target = parts[-1]
            # Remove if it's a flag
            if not target.startswith('-'):
                return target
        return None
    
    def _is_safe_target(self, target: str) -> bool:
        """Check if target is in safe list"""
        return target in self.safe_targets
    
    def _simulate_execution(self, command: str) -> Dict:
        """
        Simulate command execution without actually running it
        
        Args:
            command: Nmap command
            
        Returns:
            Simulated execution result
        """
        start_time = time.time()
        
        # Parse command
        parts = command.split()
        flags = [p for p in parts if p.startswith('-')]
        target = self._extract_target(command)
        
        # Simulate execution based on command type
        scan_type = self._detect_scan_type(flags)
        port_count = self._estimate_port_count(flags)
        
        # Simulate timing
        simulated_time = self._estimate_scan_time(scan_type, port_count)
        
        # Generate simulated output
        output = self._generate_simulated_output(command, scan_type, port_count)
        
        execution_time = time.time() - start_time
        
        return {
            'success': True,
            'simulated': True,
            'output': output,
            'execution_time': simulated_time,
            'scan_type': scan_type,
            'estimated_ports': port_count,
            'component': 'docker_sandbox'
        }
    
    def _detect_scan_type(self, flags: list) -> str:
        """Detect scan type from flags"""
        scan_types = {
            '-sS': 'SYN Scan',
            '-sT': 'TCP Connect',
            '-sU': 'UDP Scan',
            '-sA': 'ACK Scan',
            '-sV': 'Version Detection'
        }
        
        for flag in flags:
            if flag in scan_types:
                return scan_types[flag]
        
        return 'Default Scan'
    
    def _estimate_port_count(self, flags: list) -> int:
        """Estimate number of ports to scan"""
        for i, flag in enumerate(flags):
            if flag == '-p':
                if i + 1 < len(flags):
                    port_spec = flags[i + 1]
                    if port_spec == '-':
                        return 65535
                    elif ',' in port_spec:
                        return len(port_spec.split(','))
                    elif '-' in port_spec and port_spec != '-':
                        try:
                            start, end = port_spec.split('-')
                            return int(end) - int(start) + 1
                        except:
                            pass
            elif flag == '-F':
                return 100  # Fast scan
            elif '--top-ports' in flag:
                return int(flag.split('=')[1]) if '=' in flag else 1000
        
        return 1000  # Default top 1000 ports
    
    def _estimate_scan_time(self, scan_type: str, port_count: int) -> float:
        """Estimate scan duration"""
        base_time = 0.001  # Base time per port
        
        multipliers = {
            'SYN Scan': 1.0,
            'TCP Connect': 1.5,
            'UDP Scan': 3.0,
            'Version Detection': 2.0,
            'Default Scan': 1.0
        }
        
        multiplier = multipliers.get(scan_type, 1.0)
        return base_time * port_count * multiplier
    
    def _generate_simulated_output(self, command: str, scan_type: str, port_count: int) -> str:
        """Generate realistic Nmap output"""
        target = self._extract_target(command) or 'target'
        
        output = f"""Starting Nmap ( https://nmap.org )
Nmap scan report for {target}
Host is up (0.0012s latency).
Not shown: {port_count - 3} closed ports
PORT     STATE SERVICE
22/tcp   open  ssh
80/tcp   open  http
443/tcp  open  https

Nmap done: 1 IP address (1 host up) scanned in {self._estimate_scan_time(scan_type, port_count):.2f} seconds
"""
        return output
    
    def _docker_execution(self, command: str, timeout: int) -> Dict:
        """
        Execute command in Docker container
        
        Args:
            command: Nmap command
            timeout: Timeout in seconds
            
        Returns:
            Execution result
        """
        start_time = time.time()
        
        try:
            # Run Nmap in Docker container
            docker_command = [
                'docker', 'run', '--rm',
                '--network', 'host',
                'instrumentisto/nmap',
                *command.split()[1:]  # Remove 'nmap' prefix
            ]
            
            result = subprocess.run(
                docker_command,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            execution_time = time.time() - start_time
            
            return {
                'success': result.returncode == 0,
                'simulated': False,
                'output': result.stdout if result.returncode == 0 else result.stderr,
                'execution_time': execution_time,
                'return_code': result.returncode,
                'component': 'docker_sandbox'
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': f'Command timed out after {timeout} seconds',
                'output': '',
                'execution_time': timeout
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Execution failed: {str(e)}',
                'output': '',
                'execution_time': time.time() - start_time
            }
    
    def validate_execution(self, command: str) -> Dict:
        """
        Test if command would execute successfully
        
        Args:
            command: Nmap command
            
        Returns:
            Validation result
        """
        # Check syntax first
        if not command.strip().startswith('nmap'):
            return {
                'executable': False,
                'reason': 'Command must start with nmap'
            }
        
        # Check safety
        if not self._is_safe_command(command):
            return {
                'executable': False,
                'reason': 'Command contains unsafe elements'
            }
        
        # Try simulation
        result = self._simulate_execution(command)
        
        return {
            'executable': True,
            'estimated_time': result['execution_time'],
            'scan_type': result.get('scan_type', 'Unknown'),
            'port_count': result.get('estimated_ports', 0)
        }


# Test function
if __name__ == "__main__":
    print("="*70)
    print("DOCKER SANDBOX TEST")
    print("="*70 + "\n")
    
    sandbox = DockerSandbox(mode='simulate')
    
    test_commands = [
        "nmap -sS -p 80,443 scanme.nmap.org",
        "nmap -A -v -T4 192.168.1.1",
        "nmap -sU -p 53 localhost",
        "nmap --script exploit target.com",  # Should be blocked
    ]
    
    for cmd in test_commands:
        print(f"\nTesting: {cmd}")
        print("-" * 70)
        
        # Validate
        validation = sandbox.validate_execution(cmd)
        print(f"Executable: {validation.get('executable', False)}")
        
        if validation.get('executable'):
            print(f"Estimated time: {validation.get('estimated_time', 0):.3f}s")
            
            # Execute
            result = sandbox.execute(cmd)
            print(f"Success: {result['success']}")
            print(f"Simulated: {result.get('simulated', False)}")
            if result['success']:
                print(f"\nOutput:\n{result['output'][:200]}...")
        else:
            print(f"Blocked: {validation.get('reason', 'Unknown')}")