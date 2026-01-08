# Docker Sandbox Integration Guide

## 📦 What You Just Got

A **Docker Sandbox** module for safely testing Nmap commands!

**File:** `docker_sandbox.py` (~200 lines)

---

## 🎯 Features

1. ✅ **Simulate Mode** - Safe testing without real scanning
2. ✅ **Docker Mode** - Real execution in isolated container
3. ✅ **Safety Checks** - Blocks dangerous commands
4. ✅ **Execution Validation** - Tests if commands would work
5. ✅ **Realistic Output** - Generates Nmap-like results

---

## 📥 Installation

### Step 1: Copy File

Copy `docker_sandbox.py` to your `validators/` folder:

```
validators/
├── __init__.py
├── syntax_checker.py
├── conflict_detector.py
├── heuristic_checker.py
├── scoring_system.py
├── final_decision.py
└── docker_sandbox.py  ← NEW FILE
```

### Step 2: Test It

```powershell
python test_sandbox.py
```

Expected: All tests pass ✅

---

## 💻 Usage Examples

### Example 1: Basic Usage

```python
from validators.docker_sandbox import DockerSandbox

# Initialize (simulate mode - safe, no real scanning)
sandbox = DockerSandbox(mode='simulate')

# Test a command
result = sandbox.execute("nmap -sS -p 80,443 192.168.1.1")

print(f"Success: {result['success']}")
print(f"Output: {result['output']}")
print(f"Time: {result['execution_time']:.3f}s")
```

### Example 2: Validate Before Execution

```python
sandbox = DockerSandbox()

# Check if command is safe and executable
validation = sandbox.validate_execution("nmap -sS -p 80 target.com")

if validation['executable']:
    print(f"✅ Command is safe")
    print(f"Estimated time: {validation['estimated_time']:.2f}s")
    print(f"Scan type: {validation['scan_type']}")
else:
    print(f"❌ Command blocked: {validation['reason']}")
```

### Example 3: Use Docker Mode (Real Execution)

```python
# Only use with safe targets like scanme.nmap.org
sandbox = DockerSandbox(mode='docker')

result = sandbox.execute("nmap -sV scanme.nmap.org", timeout=60)

if result['success']:
    print("Real scan completed!")
    print(result['output'])
```

---

## 🔗 Integration with Your Validator

### Option A: Add as Validation Step

Update your `validator.py`:

```python
from validators.docker_sandbox import DockerSandbox

class NmapValidator:
    def __init__(self):
        # ... existing code ...
        self.sandbox = DockerSandbox(mode='simulate')
        print("  - Docker Sandbox loaded")
    
    def validate_single_command(self, command: str, test_execution: bool = False):
        # ... existing validation ...
        
        # Optional: Test execution
        if test_execution:
            print("\nStep 5: Testing execution...")
            exec_result = self.sandbox.execute(command, timeout=5)
            print(f"  Executable: {exec_result['success']}")
```

### Option B: Separate Execution Validator

```python
from validators.docker_sandbox import DockerSandbox

def validate_with_execution(command: str):
    """Complete validation including execution test"""
    
    # Standard validation
    validator = NmapValidator()
    validation_result = validator.validate_single_command(command)
    
    # Execution test
    sandbox = DockerSandbox(mode='simulate')
    execution_result = sandbox.execute(command)
    
    # Combine results
    return {
        'validation': validation_result,
        'execution': execution_result,
        'fully_valid': validation_result['valid'] and execution_result['success']
    }
```

---

## 🛡️ Safety Features

### Blocked Commands:
- ❌ Exploit scripts (`--script exploit`)
- ❌ DoS scripts (`--script dos`)
- ❌ Command injection (`;`, `|`, `&`, etc.)
- ❌ Unsafe targets (in docker mode)

### Allowed Commands:
- ✅ Standard scans (`-sS`, `-sT`, `-sU`)
- ✅ Version detection (`-sV`)
- ✅ OS detection (`-O`)
- ✅ Safe NSE scripts
- ✅ Any scan against safe targets

---

## 🎮 Two Modes

### Simulate Mode (Default)
```python
sandbox = DockerSandbox(mode='simulate')
```
- ✅ No real network activity
- ✅ Instant results
- ✅ Safe for testing
- ✅ Generates realistic output
- ✅ Good for development/testing

### Docker Mode
```python
sandbox = DockerSandbox(mode='docker')
```
- ⚠️ Runs real Nmap in container
- ⚠️ Requires Docker installed
- ⚠️ Only allows safe targets
- ✅ Real validation results
- ✅ Use for production validation

---

## 📊 Output Format

```python
{
    'success': True/False,           # Execution succeeded
    'simulated': True/False,         # Was it simulated or real
    'output': 'Nmap output...',      # Nmap output text
    'execution_time': 1.234,         # Time in seconds
    'scan_type': 'SYN Scan',         # Detected scan type
    'estimated_ports': 1000,         # Number of ports
    'component': 'docker_sandbox'
}
```

---

## 🧪 Testing

```powershell
# Run sandbox tests
python test_sandbox.py

# Test in your code
python -c "from validators.docker_sandbox import DockerSandbox; s = DockerSandbox(); r = s.execute('nmap -sS -p 80 localhost'); print(r)"
```

---

## ✅ Deliverables Checklist

Now you have:

- [x] Syntax Checker (~200 lines)
- [x] Conflict Detector (~250 lines)
- [x] Heuristic Checker (~150 lines)
- [x] Scoring System (~200 lines)
- [x] Final Decision Agent (~200 lines)
- [x] **Docker Sandbox (~200 lines)** ← NEW! ✅
- [x] Complete Integration
- [x] Test Suite

**Total: ~1,530 lines of code**

---

## 🎯 Next Steps

1. Copy `docker_sandbox.py` to `validators/` folder
2. Run `python test_sandbox.py` to test
3. Decide if you want to integrate it into your main validator
4. Optional: Add MCP Server (REST API) next

**Your validation system is now even more complete!** 🚀