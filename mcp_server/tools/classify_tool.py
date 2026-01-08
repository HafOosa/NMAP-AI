#!/usr/bin/env python3
"""
✅ CORRECT classify_tool.py for MCP Server
- Uses joblib model (NO spaCy)
- Function name: classify_query (matches server.py import)
- Async compatible
"""

import sys
from pathlib import Path
import joblib
import re
from typing import Dict, Any
import json

# ============================================================================
# MODEL LOADING
# ============================================================================

classifier_model = None
label_encoder = None

def load_model():
    """Load classifier model once at startup"""
    global classifier_model, label_encoder
    
    # Try multiple paths
    paths_to_try = [
        Path(__file__).parent.parent / "models" / "hybrid_classifier_optimized.joblib",
        Path(__file__).parent / "models" / "hybrid_classifier_optimized.joblib",
        Path(__file__).parent / "hybrid_classifier_optimized.joblib",
        Path.home() / ".nmap_ai" / "models" / "hybrid_classifier_optimized.joblib",
    ]
    
    for model_path in paths_to_try:
        if model_path.exists():
            try:
                model_data = joblib.load(str(model_path))
                classifier_model = model_data.get('model')
                label_encoder = model_data.get('le_complexity')
                print(f"✅ Model loaded: {model_path}")
                return True
            except Exception as e:
                print(f"⚠️  Error loading {model_path}: {e}")
                continue
    
    print("⚠️  WARNING: No model found. Using fallback heuristics.")
    return False


# Load model at import time
load_model()


# ============================================================================
# FEATURE EXTRACTION (30 features)
# ============================================================================

def extract_simple_features(query: str) -> list:
    """
    Extract exactly 30 features without spaCy
    Compatible with joblib classifier model
    """
    query_lower = query.lower()
    words = query_lower.split()
    
    features = []
    
    # === STATISTICS (5 features) ===
    features.append(len(words))  # 0: num_tokens
    features.append(sum(1 for w in words if w in ['scan', 'check', 'test', 'probe']))  # 1: verbs
    features.append(sum(1 for w in words if w in ['port', 'host', 'network', 'service']))  # 2: nouns
    features.append(sum(1 for w in words if w in ['quick', 'fast', 'slow', 'aggressive']))  # 3: adjectives
    features.append(len(query))  # 4: query_length
    
    # === IP & NETWORK (3 features) ===
    has_ipv4 = 1 if re.search(r'\d+\.\d+\.\d+\.\d+', query) else 0
    has_range = 1 if '/' in query or '-' in query else 0
    num_ips = len(re.findall(r'\d+\.\d+\.\d+\.\d+', query))
    features.extend([has_ipv4, has_range, num_ips])  # 5-7
    
    # === KEYWORDS (4 features) ===
    EASY_KEYWORDS = {'sn', 'ping', 'simple', 'basic', 'quick', 'fast'}
    MEDIUM_KEYWORDS = {'sv', 'version', 'os', 'script', 'sc', 't4', 'udp'}
    HARD_KEYWORDS = {'ss', 'sf', 'sx', 'sn', 'sm', 'sa', 'sw', 'f', 'fragment', 
                     'spoof', 'decoy', 'evasion', 't0', 't1', 't2'}
    
    nb_easy = sum(1 for w in words if w in EASY_KEYWORDS)
    nb_medium = sum(1 for w in words if w in MEDIUM_KEYWORDS)
    nb_hard = sum(1 for w in words if w in HARD_KEYWORDS)
    ratio_hard = nb_hard / (len(words) + 1)
    
    features.extend([nb_easy, nb_medium, nb_hard, ratio_hard])  # 8-11
    
    # === OPTIONS (7 features) ===
    has_timing = 1 if any(t in query_lower for t in ['t0', 't1', 't2', 't3', 't4', 't5']) else 0
    has_script = 1 if 'script' in query_lower else 0
    has_udp = 1 if 'udp' in query_lower or '-su' in query_lower else 0
    has_os = 1 if ' -o' in query_lower or 'os ' in query_lower else 0
    has_version = 1 if '-sv' in query_lower or 'version' in query_lower else 0
    has_stealth = 1 if any(k in query_lower for k in HARD_KEYWORDS) else 0
    num_options = sum(1 for kw in list(HARD_KEYWORDS) + list(MEDIUM_KEYWORDS) if kw in query_lower)
    
    features.extend([has_timing, has_script, has_udp, has_os, has_version, has_stealth, num_options])  # 12-18
    
    # === ADVANCED (3 features) ===
    has_entities = 0  # No NER without spaCy
    has_proxy = 1 if 'proxy' in query_lower else 0
    has_decoy = 1 if 'decoy' in query_lower else 0
    features.extend([has_entities, has_proxy, has_decoy])  # 19-21
    
    # === SCRIPTS (1 feature) ===
    script_weight = 10 if 'script' in query_lower else 0
    features.append(script_weight)  # 22
    
    # === COMPLEXITY SCORE (1 feature) ===
    complexity_score = nb_hard * 5 + nb_medium * 2 + nb_easy
    features.append(complexity_score)  # 23
    
    # === KG FEATURES (5 features) ===
    features.extend([0, 0, 0.0, 0, 0])  # 24-28
    
    # === PADDING (1 feature) ===
    features.append(0)  # 29
    
    # Ensure exactly 30 features
    return features[:30]


# ============================================================================
# HEURISTIC FALLBACK
# ============================================================================

def fallback_classify(query: str) -> str:
    """
    Fallback classification using heuristics
    Used when model is not available
    """
    query_lower = query.lower()
    
    # HARD indicators
    hard_patterns = ['-ss', '-sf', '-sx', '-sn', '-sm', '-sa', '-sw', 
                     'fragment', 'spoof', 'decoy', 'evasion', '-t0', '-t1', '-t2']
    if any(pattern in query_lower for pattern in hard_patterns):
        return "HARD"
    
    # MEDIUM indicators
    medium_patterns = ['-sv', '-o ', 'version', 'os ', 'script', '-t4', '-t5', 'udp']
    if any(pattern in query_lower for pattern in medium_patterns):
        return "MEDIUM"
    
    # Default
    return "EASY"


# ============================================================================
# MAIN CLASSIFICATION FUNCTION (async)
# ============================================================================

async def classify_query(query: str) -> Dict[str, Any]:
    """
    Classify NMAP query complexity
    
    Args:
        query: NMAP command string
    
    Returns:
        {
            "complexity": "EASY|MEDIUM|HARD",
            "confidence": float (0.0-1.0),
            "all_probabilities": {label: prob, ...} or None,
            "explanation": str,
            "success": bool
        }
    """
    
    if not query or not isinstance(query, str):
        return {
            "complexity": "EASY",
            "confidence": 0.0,
            "all_probabilities": None,
            "explanation": "Invalid query",
            "success": False
        }
    
    # Try ML model first
    if classifier_model is not None and label_encoder is not None:
        try:
            features = extract_simple_features(query)
            
            # Predict
            prediction = classifier_model.predict([features])[0]
            probabilities = classifier_model.predict_proba([features])[0]
            
            labels = label_encoder.classes_.tolist()  # ['EASY', 'MEDIUM', 'HARD']
            complexity = labels[prediction]
            confidence = float(max(probabilities))
            
            return {
                "complexity": complexity,
                "confidence": confidence,
                "all_probabilities": {
                    label: float(prob) for label, prob in zip(labels, probabilities)
                },
                "explanation": f"ML-based classification (confidence: {confidence:.1%})",
                "success": True
            }
        
        except Exception as e:
            print(f"⚠️  ML classification error: {e}")
            # Fall through to heuristic
    
    # Fallback to heuristic
    try:
        prediction = fallback_classify(query)
        # Create default probabilities
        probs = {"EASY": 0.3, "MEDIUM": 0.3, "HARD": 0.4}
        probs[prediction] = 0.6  # Boost the predicted class
        # Normalize
        total = sum(probs.values())
        probs = {k: v/total for k, v in probs.items()}
        
        return {
            "complexity": prediction,
            "confidence": 0.6,
            "all_probabilities": probs,
            "explanation": "Heuristic classification (ML model unavailable)",
            "success": True
        }
    except Exception as e:
        return {
            "complexity": "EASY",
            "confidence": 0.5,
            "all_probabilities": {"EASY": 0.5, "MEDIUM": 0.3, "HARD": 0.2},
            "explanation": f"Error: {str(e)}",
            "success": False
        }


# ============================================================================
# SYNCHRONOUS WRAPPER (for compatibility)
# ============================================================================

def classify_query_sync(query: str) -> Dict[str, Any]:
    """
    Synchronous version of classify_query
    Use this if you can't use async/await
    """
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(classify_query(query))


# ============================================================================
# MCP TOOL DEFINITION
# ============================================================================

CLASSIFY_TOOL = {
    "name": "classify_nmap_command",
    "description": "Classify the complexity (EASY/MEDIUM/HARD) of a NMAP command using ML + heuristics",
    "input_schema": {
        "type": "object",
        "properties": {
            "nmap_command": {
                "type": "string",
                "description": "The NMAP command to classify (e.g., 'nmap -sV -O 192.168.1.1')"
            }
        },
        "required": ["nmap_command"]
    }
}


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    import asyncio
    
    print("=" * 70)
    print("✅ NMAP CLASSIFIER TOOL - TEST")
    print("=" * 70)
    
    test_commands = [
        "nmap -sn 192.168.1.0/24",
        "nmap -sV -O 192.168.1.1",
        "nmap -sS -p- -sV --script vuln -T5 192.168.0.0/16",
        "nmap -p 80,443 192.168.1.1",
        "nmap -f --decoy 192.168.1.1",
    ]
    
    async def test():
        for cmd in test_commands:
            result = await classify_query(cmd)
            print(f"\n📌 Command: {cmd}")
            print(f"   Complexity: {result['complexity']}")
            print(f"   Confidence: {result['confidence']:.1%}")
            print(f"   ✓ {result['explanation']}")
    
    asyncio.run(test())