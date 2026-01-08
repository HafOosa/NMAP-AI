"""
FastMCP Server pour NMAP-AI
Compatible MCP Inspector & mcp dev
"""
import sys
from pathlib import Path
import logging

# Add project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.server.fastmcp import FastMCP

# Import tools
from tools.classify_tool import classify_query
from tools.generate_easy_tool import generate_nmap_easy
from tools.generate_medium_tool import generate_nmap_medium
from tools.generate_hard_tool import generate_nmap_hard
from tools.validate_tool import validate_command

# Logging minimal
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nmap-ai")

# Create FastMCP server (ATTENTION : plus de description ici)
mcp = FastMCP(name="nmap-ai")

# ================= TOOLS =================

@mcp.tool(
    name="classify_query",
    description="Classify Nmap query complexity (EASY / MEDIUM / HARD)"
)
async def classify(query: str) -> str:
    result = await classify_query(query)
    return (
        f"Complexity: {result['complexity']}\n"
        f"Confidence: {result['confidence']:.2f}\n"
        f"Explanation: {result['explanation']}"
    )

@mcp.tool(
    name="generate_nmap_easy",
    description="Generate EASY Nmap command"
)
async def gen_easy(query: str) -> str:
    return await generate_nmap_easy(query)

@mcp.tool(
    name="generate_nmap_medium",
    description="Generate MEDIUM Nmap command"
)
async def gen_medium(query: str) -> str:
    return await generate_nmap_medium(query)

@mcp.tool(
    name="generate_nmap_hard",
    description="Generate HARD Nmap command"
)
async def gen_hard(query: str) -> str:
    return await generate_nmap_hard(query)

@mcp.tool(
    name="validate_command",
    description="Validate Nmap command (syntax, security, best practices)"
)
async def validate(command: str) -> str:
    result = await validate_command(command)
    return (
        f"Valid: {result['valid']}\n"
        f"Score: {result['score']}/100\n"
        f"Grade: {result['grade']}\n"
        f"Errors: {', '.join(result.get('errors', []))}\n"
        f"Warnings: {', '.join(result.get('warnings', []))}\n"
        f"Suggestions: {', '.join(result.get('suggestions', []))}"
    )

if __name__ == "__main__":
    logger.info("🚀 NMAP-AI FastMCP Server starting...")
    mcp.run()
