import os
from pathlib import Path

# ============================
# PATHS
# ============================
PROJECT_ROOT = Path(__file__).parent.parent
AGENT_CLASSIFIER_PATH = PROJECT_ROOT / "AgentClassifieur"
AGENT_RAG_PATH = PROJECT_ROOT / "AgentRag"
AGENT_MODELS_PATH = PROJECT_ROOT / "AgentModels"
AGENT_VALIDATOR_PATH = PROJECT_ROOT / "AgentValidator"
RAG_NEO4J_PATH = PROJECT_ROOT / "Rag_neo4j"

# ============================
# NEO4J
# ============================
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "nmap_ai_2024")

# ============================
# MODELS
# ============================
MEDIUM_MODEL_PATH = AGENT_MODELS_PATH / "models" / "medium_models"
HARD_MODEL_PATH = AGENT_MODELS_PATH / "models" / "hard_models"

# ============================
# CLASSIFIER
# ============================
CLASSIFIER_MODEL_PATH = AGENT_CLASSIFIER_PATH / "models" / "complexity_classifier.pkl"

# ============================
# MCP SERVER
# ============================
MCP_SERVER_NAME = "nmap-ai"
MCP_SERVER_VERSION = "1.0.0"