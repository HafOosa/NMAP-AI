"""
QUICK START GUIDE - Person 5
Get your validation system running in 5 minutes!
"""

# ============================================================================
# STEP 1: SETUP (One-time)
# ============================================================================

# 1.1 Make sure Neo4j is running
"""
Check in Docker Desktop or run:
    docker ps

You should see: nmap-ai-neo4j container
"""

# 1.2 Install Python dependencies
"""
    pip install neo4j
"""

# ============================================================================
# STEP 2: COPY FILES
# ============================================================================
"""
Copy these 8 files to your project folder:
1. config.py
2. syntax_checker.py
3. conflict_detector.py
4. heuristic_checker.py
5. scoring_system.py
6. final_decision.py
7. validator.py
8. test_validator.py
"""

# ============================================================================
# STEP 3: TEST YOUR SYSTEM
# ============================================================================

# Run the test suite:
"""
    python test_validator.py
"""
# Expected: ✅ 5/5 tests passed

# ============================================================================
# STEP 4: USE IN YOUR CODE
# ============================================================================

from validator import NmapValidator

# Initialize
validator = NmapValidator()

# Validate a command
result = validator.validate_single_command(
    "nmap -sS -p 80,443 -T4 -v 192.168.1.1"
)

print(f"Score: {result['score']}/100")
print(f"Grade: {result['grade']}")
print(f"Valid: {result['valid']}")

# Close when done
validator.close()

# ============================================================================
# STEP 5: INTEGRATE WITH YOUR TEAM
# ============================================================================

# When Person 2, 3, 4 send you commands:

# From Person 4 (RAG Agent)
rag_command = "nmap -sS -p 80,443 192.168.1.1"

# From Person 2 (Phi4 Model)  
phi4_command = "nmap -sS -p 80,443,22 -A 192.168.1.1"

# From Person 2 (Diffusion Model)
diffusion_command = "nmap -sS -p 1-1000 192.168.1.1"

# Validate all and choose best
result = validator.validate_multiple_commands(
    [rag_command, phi4_command, diffusion_command],
    ['RAG_Agent', 'Phi4_Model', 'Diffusion_Model']
)

# Get the best command
best = result['decision']['chosen_command']
confidence = result['decision']['confidence']

print(f"Best command: {best}")
print(f"Confidence: {confidence}%")

validator.close()

# ============================================================================
# DONE! 🎉
# ============================================================================

"""
You now have:
✅ Complete validation system (~1,330 lines)
✅ Neo4j integration for conflict detection
✅ Scoring system with A-F grades
✅ Final decision agent
✅ Full test suite

Your teammates can now send you commands and you'll validate them!
"""