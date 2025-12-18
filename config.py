
# Neo4j Connection Settings
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "nmap_ai_2024"

# Validation Weights (for scoring)
WEIGHTS = {
    'syntax': 0.30,      # 30% - Must be valid syntax
    'conflicts': 0.40,   # 40% - No conflicts (most important)
    'heuristics': 0.30   # 30% - Best practices
}

# Score Grades
GRADE_THRESHOLDS = {
    'A': 90,
    'B': 80,
    'C': 70,
    'D': 60,
    'F': 0
}