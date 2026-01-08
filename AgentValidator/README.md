# NMAP Validator - Person 5
## Infrastructure & Validation System

Complete validation system for NMAP-AI project with Neo4j Knowledge Graph integration.

---

## 📋 Components Overview

### ✅ **What You Built:**

1. **Syntax Checker** (~200 lines)
   - Validates Nmap command syntax
   - Checks flags, ports, targets
   - Returns errors and warnings

2. **Conflict Detector** (~250 lines)
   - Uses Neo4j Knowledge Graph from Person 1
   - Detects conflicting options (CONFLICTS_WITH)
   - Provides recommendations (COMMONLY_USED_WITH)

3. **Heuristic Checker** (~150 lines)
   - Best practices validation
   - Performance warnings
   - Security recommendations

4. **Scoring System** (~200 lines)
   - Combines all checker results
   - Weighted scoring (Syntax: 30%, Conflicts: 40%, Heuristics: 30%)
   - Grades A-F

5. **Final Decision Agent** (~200 lines)
   - Chooses best command from multiple options
   - Confidence calculation
   - Explanation generation

---

## 🚀 Installation

### Prerequisites:
- ✅ Docker Desktop (running)
- ✅ Neo4j container (from Person 1)
- ✅ Python 3.8+

### Step 1: Copy Files to Your Project

Copy all these files to your project folder:
```
your_project/
├── config.py
├── syntax_checker.py
├── conflict_detector.py
├── heuristic_checker.py
├── scoring_system.py
├── final_decision.py
├── validator.py
├── test_validator.py
└── requirements.txt
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install neo4j
```

### Step 3: Verify Neo4j is Running

Make sure Neo4j is running:
```bash
docker ps
```

You should see `nmap-ai-neo4j` container.

---

## 🧪 Testing

### Run Complete Test Suite:
```bash
python test_validator.py
```

Expected output:
```
✅ PASS | Syntax Checker
✅ PASS | Conflict Detector
✅ PASS | Heuristic Checker
✅ PASS | Integration Test
✅ PASS | Final Decision

TOTAL: 5/5 tests passed
🎉 ALL TESTS PASSED!
```

### Run Main Validator Demo:
```bash
python validator.py
```

This will:
1. Validate a single command
2. Compare multiple commands
3. Generate full reports

---

## 📖 Usage Examples

### Example 1: Validate Single Command

```python
from validator import NmapValidator

validator = NmapValidator()

# Validate a command
result = validator.validate_single_command(
    "nmap -sS -p 80,443 -T4 -v 192.168.1.1"
)

print(f"Score: {result['score']}/100")
print(f"Grade: {result['grade']}")
print(f"Valid: {result['valid']}")

validator.close()
```

### Example 2: Get Full Report

```python
from validator import NmapValidator

validator = NmapValidator()

# Get detailed report
report = validator.get_full_report(
    "nmap -sS -p 80,443 -T4 -v 192.168.1.1"
)

print(report)
validator.close()
```

### Example 3: Compare Multiple Commands (Final Decision)

```python
from validator import NmapValidator

validator = NmapValidator()

# Commands from different agents
commands = [
    "nmap -sS -p 80,443 -T4 -v 192.168.1.1",     # RAG Agent
    "nmap -sS -p 80,443,22 -A -T4 192.168.1.1",  # Phi4 Model
    "nmap -sS -sT -p- 192.168.1.1"                # Diffusion Model
]

agents = ['RAG_Agent', 'Phi4_Model', 'Diffusion_Model']

result = validator.validate_multiple_commands(commands, agents)

# Get final decision
decision = result['decision']
print(f"Best command: {decision['chosen_command']}")
print(f"Confidence: {decision['confidence']}%")

validator.close()
```

---

## 🔗 Integration with Other Team Members

### How Person 2, 3, 4 Will Use Your System:

```python
from validator import NmapValidator

# Initialize validator
validator = NmapValidator()

# Person 3's classifier routes to different agents
# Person 2's models and Person 4's RAG generate commands

# Example: Validate command from RAG Agent (Person 4)
rag_command = "nmap -sS -p 80,443 192.168.1.1"
result = validator.validate_single_command(rag_command)

if result['valid']:
    print(f"✅ RAG command approved: {result['score']}/100")
else:
    print(f"❌ RAG command rejected")
    print(f"Issues: {result['errors']}")

# Example: Choose best from all agents
all_commands = [
    rag_command,           # From Person 4's RAG
    phi4_command,          # From Person 2's Phi4
    diffusion_command      # From Person 2's Diffusion
]

final = validator.validate_multiple_commands(
    all_commands,
    ['RAG', 'Phi4', 'Diffusion']
)

print(f"Best: {final['decision']['chosen_command']}")

validator.close()
```

---

## 🗂️ File Descriptions

| File | Lines | Purpose |
|------|-------|---------|
| `config.py` | ~30 | Configuration (Neo4j, weights, grades) |
| `syntax_checker.py` | ~200 | Validates Nmap syntax |
| `conflict_detector.py` | ~250 | Neo4j conflict detection |
| `heuristic_checker.py` | ~150 | Best practices validation |
| `scoring_system.py` | ~200 | Combines scores, assigns grades |
| `final_decision.py` | ~200 | Chooses best command |
| `validator.py` | ~150 | Main integration |
| `test_validator.py` | ~150 | Test suite |

**TOTAL: ~1,330 lines of production code**

---

## 📊 Scoring System

### Weights:
- **Syntax**: 30% - Must have valid syntax
- **Conflicts**: 40% - No conflicting options (most important!)
- **Heuristics**: 30% - Best practices

### Grades:
- **A (90-100)**: Excellent command
- **B (80-89)**: Good command
- **C (70-79)**: Acceptable
- **D (60-69)**: Poor quality
- **F (0-59)**: Failing

---

## 🔍 Knowledge Graph Queries

Your system uses these Neo4j relationships:

### CONFLICTS_WITH (used by Conflict Detector):
```cypher
MATCH (n)-[r:CONFLICTS_WITH]->(m)
WHERE n.name = '-sS' AND m.name = '-sT'
RETURN r.reason
```

### COMMONLY_USED_WITH (for recommendations):
```cypher
MATCH (n {name: '-sS'})-[r:COMMONLY_USED_WITH]->(m)
RETURN m.name, r.frequency
ORDER BY r.frequency DESC
```

---

## ✅ Deliverables Checklist

- [x] Syntax Checker (~200 lines)
- [x] Conflict Detector (~250 lines) with Neo4j
- [x] Heuristic Checker (~150 lines)
- [x] Scoring System (~200 lines)
- [x] Final Decision Agent (~200 lines)
- [x] Main Integration (validator.py)
- [x] Comprehensive Test Suite
- [x] Documentation (this README)

**Total: ~1,330 lines of production code**

---

## 🐛 Troubleshooting

### "Neo4j connection not available"
```bash
# Check if container is running
docker ps

# Restart Neo4j
docker start nmap-ai-neo4j

# Test connection
python test_kg.py
```

### "Import 'neo4j' could not be resolved"
```bash
pip install neo4j
```

### Tests failing
```bash
# Run individual component tests
python syntax_checker.py
python conflict_detector.py
python heuristic_checker.py
```

---

## 👥 Credits

**Person 5 (You)**: Infrastructure & Validation
**Person 1**: Knowledge Graph (147 nodes, 604 relationships)

---

## 📞 Support

If you have issues, check:
1. Neo4j is running (`docker ps`)
2. Python dependencies installed (`pip install neo4j`)
3. Connection settings in `config.py`

---

🎉 **Your validation system is complete and ready to integrate with the team!**