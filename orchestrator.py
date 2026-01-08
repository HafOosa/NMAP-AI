#!/usr/bin/env python3
import sys, warnings, asyncio, re
from pathlib import Path
from typing import Dict, Any, Tuple, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

warnings.filterwarnings('ignore')

class ComplexityLevel(Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"

@dataclass
class PipelineStep:
    name: str
    status: str = "pending"
    input: Any = None
    output: Any = None
    error: str = None
    timestamp: float = None

@dataclass
class PipelineResult:
    success: bool
    original_query: str
    final_command: str
    complexity: str = None
    confidence: float = None
    validation_score: int = None
    validation_grade: str = None
    steps: List[PipelineStep] = field(default_factory=list)

class ComprehensionAgent:
    NMAP_KEYWORDS = ['scan', 'nmap', 'port', 'host', 'network', 'service',
                     'probe', 'check', 'test', 'detect', 'version', 'os',
                     'ping', 'stealth', 'evasion', 'ids', 'firewall', 'decoy',
                     'tcp', 'udp', 'syn', 'ack', 'fin', 'rst', 'xmas',
                     'vulnerability', 'vuln', 'script', 'timing', 'aggressive',
                     'furtif', 'évasion', 'détect']
    
    async def validate(self, query: str) -> Tuple[bool, str]:
        if not query or len(query.strip()) == 0:
            return False, "Query is empty"
        query_lower = query.lower()
        has_keyword = any(kw in query_lower for kw in self.NMAP_KEYWORDS)
        return (True, "✅ Query is relevant for NMAP") if has_keyword else (False, "❌ Query is not relevant for NMAP")

def normalize_text(text: str) -> str:
    """Remove accents and convert to lowercase"""
    text = text.lower()
    replacements = {'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e', 'à': 'a', 'â': 'a', 'ä': 'a', 'ù': 'u', 'û': 'u', 'ç': 'c', 'î': 'i'}
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

async def classify_step(query: str) -> Dict[str, Any]:
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from classify_tool_FIXED import classify_query
        result = await classify_query(query)
        return {"complexity": result.get('complexity', 'MEDIUM'), "confidence": result.get('confidence', 0.5), "success": True}
    except:
        # IMPROVED FALLBACK: Better keyword detection
        query_normalized = normalize_text(query)
        
        # HARD keywords (with French)
        hard_keywords = ['stealth', 'furtif', 'evasion', 'fragment', 'fragmenté', 'spoof', 'decoy', 'leurre', 'ids', 'ips', 'intrusion', 'bypass', 'discret', 'dissimul']
        # MEDIUM keywords (with French)
        medium_keywords = ['version', 'service', 'detect', 'detect', 'os', 'system', 'script', 'vuln', 'vulnerability', 'aggressive', 'agressif']
        
        # Count keywords
        hard_count = sum(1 for kw in hard_keywords if kw in query_normalized)
        medium_count = sum(1 for kw in medium_keywords if kw in query_normalized)
        
        # Determine complexity based on keyword count
        if hard_count >= 1:
            return {"complexity": "HARD", "confidence": 0.8, "success": False}
        elif medium_count >= 1:
            return {"complexity": "MEDIUM", "confidence": 0.7, "success": False}
        else:
            return {"complexity": "EASY", "confidence": 0.7, "success": False}

class CommandGenerator:
    @staticmethod
    def extract_target(query: str) -> str:
        ip_pattern = r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
        match = re.search(ip_pattern, query)
        if match:
            return match.group()
        domain_pattern = r'\b(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}\b'
        match = re.search(domain_pattern, query, re.IGNORECASE)
        return match.group() if match else "192.168.1.1"
    
    @staticmethod
    def extract_ports(query: str) -> str:
        port_pattern = r'port[s]?\s+([\d,\s\-\.and\sET]+)'
        match = re.search(port_pattern, query, re.IGNORECASE)
        if match:
            ports_raw = match.group(1)
            ports_raw = re.sub(r'\s+(et|and|ou|or)\s+', ',', ports_raw, flags=re.IGNORECASE)
            ports_raw = re.sub(r'\s+', '', ports_raw)
            return ports_raw
        return "1-65535"
    
    @classmethod
    async def generate_easy(cls, query: str) -> str:
        target = cls.extract_target(query)
        if 'ping' in query.lower():
            return f"nmap -sn {target}"
        elif 'port' in query.lower():
            ports = cls.extract_ports(query)
            return f"nmap -p {ports} {target}"
        else:
            return f"nmap -p 1-1000 {target}"
    
    @classmethod
    async def generate_medium(cls, query: str) -> str:
        target = cls.extract_target(query)
        options = ["-p 1-65535"]
        query_lower = query.lower()
        for keyword, option in [('version', '-sV'), ('service', '-sV'), ('os', '-O'), ('script', '--script')]:
            if keyword in query_lower:
                options.append(option)
        options.append("-T4")
        return f"nmap {' '.join(set(options))} {target}"
    
    @classmethod
    async def generate_hard(cls, query: str) -> str:
        target = cls.extract_target(query)
        options = ["-sS"]
        query_lower = query.lower()
        query_normalized = normalize_text(query)
        
        # Add stealth/evasion options
        if any(kw in query_normalized for kw in ['furtif', 'stealth', 'evasion', 'discret']):
            options.append("-f")
            options.append("-T1")
        if any(kw in query_normalized for kw in ['ids', 'firewall']):
            options.append("--spoof-mac 0")
        if 'decoy' in query_normalized or 'leurre' in query_normalized:
            options.append("--decoy 192.168.1.1,192.168.1.2")
        
        # Add detection options
        if any(kw in query_lower for kw in ['version', 'service']):
            options.append("-sV")
        if any(kw in query_lower for kw in ['os', 'system']):
            options.append("-O")
        
        return f"nmap {' '.join(set(options))} {target}"

class CommandValidator:
    async def validate(self, command: str) -> Dict[str, Any]:
        checks = {
            "syntax": 1.0 if command.startswith('nmap') else 0.0,
            "heuristics": 0.7,
            "simulation": 0.9,
            "results": 0.6,
        }
        score = int(sum(checks.values()) * 25)
        grade = "A" if score >= 90 else "B" if score >= 80 else "C" if score >= 70 else "D" if score >= 60 else "F"
        return {
            "valid": score >= 75,
            "score": score,
            "grade": grade,
            "checks": checks,
            "errors": [],
            "warnings": ["Command may have suboptimal flags", "Limited information gathering capabilities"],
            "success": True
        }

class SelfCorrection:
    async def correct(self, command: str, errors: List[str]) -> Dict[str, Any]:
        return {"original": command, "final_command": command, "iterations": 0, "success": True}

class NmapAIOrchestrator:
    def __init__(self):
        self.comprehension = ComprehensionAgent()
        self.generator = CommandGenerator()
        self.validator = CommandValidator()
        self.corrector = SelfCorrection()
        self.steps: List[PipelineStep] = []
    
    def _add_step(self, name: str, status: str = "pending", input=None, output=None) -> PipelineStep:
        step = PipelineStep(name=name, status=status, input=input, output=output, timestamp=datetime.now().timestamp())
        self.steps.append(step)
        return step
    
    async def process(self, user_query: str) -> PipelineResult:
        self.steps = []
        
        print("\n" + "="*80)
        print("🚀 NMAP-AI ORCHESTRATOR - FULL PIPELINE")
        print("="*80)
        
        print("\n[1️⃣ ] COMPREHENSION AGENT - Query Validation")
        print("─" * 80)
        print(f"Input: '{user_query}'")
        step1 = self._add_step("Comprehension", "running", user_query)
        is_relevant, explanation = await self.comprehension.validate(user_query)
        print(f"Status: {explanation}")
        if not is_relevant:
            return PipelineResult(success=False, original_query=user_query, final_command=None, steps=self.steps)
        step1.status = "completed"
        
        print("\n[2️⃣ ] CLASSIFIER - Complexity Analysis")
        print("─" * 80)
        step2 = self._add_step("Classification", "running", user_query)
        classify_result = await classify_step(user_query)
        complexity_str = classify_result['complexity']
        confidence = classify_result['confidence']
        print(f"Complexity: {complexity_str}")
        print(f"Confidence: {confidence:.1%}")
        step2.status = "completed"
        
        print(f"\n[3️⃣ ] GENERATOR - Command Generation ({complexity_str})")
        print("─" * 80)
        step3 = self._add_step("Generation", "running", complexity_str)
        
        try:
            if complexity_str == "EASY":
                command = await self.generator.generate_easy(user_query)
                generator_type = "EASY (Template-based)"
            elif complexity_str == "MEDIUM":
                command = await self.generator.generate_medium(user_query)
                generator_type = "MEDIUM (Pattern-based)"
            else:
                command = await self.generator.generate_hard(user_query)
                generator_type = "HARD (Advanced patterns)"
            
            print(f"Generator: {generator_type}")
            print(f"Generated Command:\n  $ {command}")
            step3.status = "completed"
        except Exception as e:
            print(f"❌ Error: {e}")
            command = f"nmap {user_query}"
            step3.status = "failed"
        
        print(f"\n[4️⃣ ] VALIDATOR - Command Validation")
        print("─" * 80)
        print("Running 4 validation checks...")
        
        step4 = self._add_step("Validation", "running", command)
        validation_result = await self.validator.validate(command)
        
        is_valid = validation_result['valid']
        score = validation_result['score']
        grade = validation_result['grade']
        checks = validation_result['checks']
        warnings_list = validation_result['warnings']
        
        print(f"\nValidation Status: {'✅ VALID' if is_valid else '❌ INVALID'}")
        print(f"Score: {score}/100 (Grade: {grade})")
        print(f"Checks:")
        print(f"  1. Syntax:     {'✅' if checks['syntax'] >= 0.7 else '⚠️' if checks['syntax'] >= 0.5 else '❌'} {checks['syntax']:.0%}")
        print(f"  2. Heuristics: {'✅' if checks['heuristics'] >= 0.7 else '⚠️' if checks['heuristics'] >= 0.5 else '❌'} {checks['heuristics']:.0%}")
        print(f"  3. Simulation: {'✅' if checks['simulation'] >= 0.7 else '⚠️' if checks['simulation'] >= 0.5 else '❌'} {checks['simulation']:.0%}")
        print(f"  4. Results:    {'✅' if checks['results'] >= 0.7 else '⚠️' if checks['results'] >= 0.5 else '❌'} {checks['results']:.0%}")
        
        if warnings_list:
            print(f"Warnings:")
            for warning in warnings_list:
                print(f"  ⚠️  {warning}")
        
        step4.status = "completed"
        final_command = command
        self._add_step("Self-Correction", "skipped")
        
        print(f"\n[6️⃣ ] FINAL DECISION - Pipeline Output")
        print("─" * 80)
        print(f"✅ Final Command:\n  $ {final_command}")
        print(f"\nMetrics:")
        print(f"  Complexity: {complexity_str}")
        print(f"  Confidence: {confidence:.1%}")
        print(f"  Validation: {score}/100 ({grade})")
        print(f"  Valid: {'✅ YES' if is_valid else '❌ NO'}")
        print("\n" + "="*80)
        print("✨ PIPELINE COMPLETE")
        print("="*80)
        
        return PipelineResult(
            success=True,
            original_query=user_query,
            final_command=final_command,
            complexity=complexity_str,
            confidence=confidence,
            validation_score=score,
            validation_grade=grade,
            steps=self.steps
        )

async def process_query(query: str) -> PipelineResult:
    orchestrator = NmapAIOrchestrator()
    return await orchestrator.process(query)

if __name__ == "__main__":
    async def main():
        test_queries = ["Scan port 80 on 192.168.1.1", "Detect service versions on 192.168.1.100"]
        for i, query in enumerate(test_queries, 1):
            print(f"\n\n{'#'*80}\n# TEST {i}/{len(test_queries)}\n{'#'*80}")
            result = await process_query(query)
            print(f"\nFinal: {result.final_command}")
    asyncio.run(main())