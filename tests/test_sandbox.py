import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from validators.docker_sandbox import DockerSandbox


def test_sandbox():
    """Test Docker Sandbox functionality"""
    print("\n" + "="*70)
    print("DOCKER SANDBOX TEST")
    print("="*70 + "\n")
    
    sandbox = DockerSandbox(mode='simulate')
    
    test_commands = [
        ("nmap -sS -p 80,443 scanme.nmap.org", True, "Valid scan"),
        ("nmap -A -v -T4 192.168.1.1", True, "Aggressive scan"),
        ("nmap -sU -p 53 localhost", True, "UDP scan"),
        ("nmap --script exploit target.com", False, "Dangerous script"),
        ("nmap -p- target.com", True, "All ports scan"),
    ]
    
    passed = 0
    total = len(test_commands)
    
    for cmd, should_pass, description in test_commands:
        print(f"\nTest: {description}")
        print(f"Command: {cmd}")
        print("-" * 70)
        
        # Validate
        validation = sandbox.validate_execution(cmd)
        executable = validation.get('executable', False)
        
        if executable == should_pass:
            status = "✅ PASS"
            passed += 1
        else:
            status = "❌ FAIL"
        
        print(f"{status} | Executable: {executable} (expected: {should_pass})")
        
        if executable:
            print(f"  Estimated time: {validation.get('estimated_time', 0):.3f}s")
            print(f"  Scan type: {validation.get('scan_type', 'Unknown')}")
            print(f"  Port count: {validation.get('port_count', 0)}")
            
            # Execute
            result = sandbox.execute(cmd, timeout=5)
            print(f"  Execution success: {result['success']}")
            if result['success']:
                output_preview = result['output'][:150].replace('\n', ' ')
                print(f"  Output preview: {output_preview}...")
        else:
            print(f"  Reason: {validation.get('reason', 'Unknown')}")
    
    print("\n" + "="*70)
    print(f"RESULT: {passed}/{total} tests passed")
    print("="*70 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = test_sandbox()
    sys.exit(0 if success else 1)


