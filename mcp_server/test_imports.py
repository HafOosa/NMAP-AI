"""Test simple des tools"""
import asyncio
from tools.classify_tool import classify_query
from tools.generate_easy_tool import generate_nmap_easy
from tools.generate_medium_tool import generate_nmap_medium
from tools.generate_hard_tool import generate_nmap_hard
from tools.validate_tool import validate_command

async def test():
    print("="*60)
    print("TEST MCP TOOLS")
    print("="*60)
    
    query = "Scan ports 80,443 on 192.168.1.1 with version detection"
    
    # Test 1: Classify
    print("\n1. Classification:")
    result = await classify_query(query)
    print(f"   {result}")
    
    # Test 2: Generate Medium
    print("\n2. Generate MEDIUM:")
    cmd = await generate_nmap_medium(query)
    print(f"   {cmd}")
    
    # Test 3: Validate
    print("\n3. Validate:")
    val = await validate_command(cmd)
    print(f"   Valid: {val['valid']}, Score: {val['score']}, Grade: {val['grade']}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    asyncio.run(test())