#!/usr/bin/env python3
"""
🔥 HYBRID NMAP CLASSIFIER - Neo4j + Machine Learning
Combines Neo4j Knowledge Graph with ML for EASY/MEDIUM/HARD classification
"""

import pandas as pd
import numpy as np
from neo4j import GraphDatabase
import logging
from typing import Dict, List, Tuple
import json
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import pickle
import re

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Neo4jConnector:
    """Connect and manage Neo4j operations"""
    
    def __init__(self, uri: str = "bolt://localhost:7687", user: str = "neo4j", password: str = "password"):
        """Initialize Neo4j connection"""
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            self.session = self.driver.session()
            logger.info("✅ Neo4j connected successfully!")
        except Exception as e:
            logger.warning(f"⚠️ Neo4j not available: {e}. Using offline mode.")
            self.driver = None
            self.session = None
    
    def query(self, query_str: str) -> List[Dict]:
        """Execute Cypher query"""
        if not self.session:
            return []
        try:
            result = self.session.run(query_str)
            return [dict(record) for record in result]
        except Exception as e:
            logger.error(f"Query error: {e}")
            return []
    
    def get_complexity_nodes(self) -> Dict:
        """Fetch complexity data from Neo4j"""
        query = """
        MATCH (cmd:Command)-[r:HAS_COMPLEXITY]->(comp:Complexity)
        RETURN cmd.name as command, comp.level as level, r.score as score
        LIMIT 1000
        """
        results = self.query(query)
        logger.info(f"📊 Fetched {len(results)} complexity nodes from Neo4j")
        return results
    
    def get_nmap_features(self) -> Dict:
        """Fetch NMAP features from knowledge graph"""
        query = """
        MATCH (opt:NmapOption)-[r:AFFECTS]->(complexity:Complexity)
        RETURN 
            opt.name as option, 
            opt.short_form as short,
            complexity.level as complexity,
            r.severity as severity
        """
        results = self.query(query)
        features = {}
        for r in results:
            if r['option']:
                features[r['option']] = {
                    'short': r['short'],
                    'complexity': r['complexity'],
                    'severity': r['severity']
                }
        logger.info(f"📚 Loaded {len(features)} NMAP features from Neo4j")
        return features
    
    def close(self):
        """Close connection"""
        if self.session:
            self.session.close()
        if self.driver:
            self.driver.close()


class NmapFeatureExtractor:
    """Extract features from NMAP commands"""
    
    # Complexity keywords
    EASY_KEYWORDS = {
        'sn': 'ping_scan',
        'list': 'list_scan',
        'simple': 'simple',
        'basic': 'basic'
    }
    
    MEDIUM_KEYWORDS = {
        'sV': 'service_detection',
        'version': 'version_detection',
        'O': 'os_detection',
        'script': 'script_scan',
        'sC': 'default_scripts',
        'timing': 'timing_control',
        'T0': 'paranoid',
        'T1': 'sneaky',
        'T2': 'polite',
        'T3': 'normal',
        'T4': 'aggressive',
        'T5': 'insane'
    }
    
    HARD_KEYWORDS = {
        'sS': 'syn_stealth',
        'sF': 'fin_stealth',
        'sX': 'xmas_stealth',
        'sN': 'null_stealth',
        'sM': 'maimon_stealth',
        'sA': 'ack_scan',
        'sW': 'window_scan',
        'sU': 'udp_scan',
        'Pn': 'no_ping',
        'f': 'fragmentation',
        'spoof': 'spoof_mac',
        'decoy': 'decoy',
        'zombie': 'idle_scan',
        'badsum': 'badsum',
        'randomize': 'randomize_hosts',
        'source-port': 'source_port_manipulation'
    }
    
    @staticmethod
    def count_ports(command: str) -> int:
        """Count number of ports in command"""
        port_match = re.search(r'-p\s+([\d,\-\*]+)', command)
        if not port_match:
            return 0
        
        ports_str = port_match.group(1)
        if ports_str == '-' or ports_str == '*':
            return 65535
        
        ports = set()
        for part in ports_str.split(','):
            if '-' in part:
                start, end = part.split('-')
                ports.update(range(int(start), int(end) + 1))
            else:
                ports.add(int(part))
        return len(ports)
    
    @staticmethod
    def extract_features(command: str) -> Dict:
        """Extract all features from command"""
        features = {
            'has_service_detection': 0,
            'has_os_detection': 0,
            'has_scripts': 0,
            'has_timing': 0,
            'has_stealth': 0,
            'ports_count': NmapFeatureExtractor.count_ports(command),
            'is_ipv6': 1 if '-6' in command else 0,
            'scan_type_count': 0,
            'has_traceroute': 1 if '--traceroute' in command else 0,
            'has_output_file': 1 if '-oN' in command or '-oX' in command else 0,
            'has_version_detection': 1 if '-sV' in command else 0,
            'has_os_detection': 1 if '-O' in command else 0,
            'has_scripts': 1 if '--script' in command else 0,
            'is_syn_scan': 1 if '-sS' in command else 0,
            'is_udp_scan': 1 if '-sU' in command else 0,
            'is_tcp_connect': 1 if '-sT' in command else 0,
            'is_ping_scan': 1 if '-sn' in command else 0,
        }
        
        # Count scan types
        scan_types = sum([
            1 if '-sS' in command else 0,
            1 if '-sT' in command else 0,
            1 if '-sU' in command else 0,
            1 if '-sn' in command else 0,
            1 if '-sA' in command else 0,
            1 if '-sM' in command else 0,
        ])
        features['scan_type_count'] = scan_types
        
        # Timing values
        timing_values = ['T0', 'T1', 'T2', 'T3', 'T4', 'T5']
        for timing in timing_values:
            if f'-{timing}' in command:
                features['has_timing'] = 1
                features['timing_value'] = int(timing[1])
                break
        
        # Count complexity indicators
        complexity_score = 0
        
        # Easy features
        if '-sn' in command:
            features['has_stealth'] = 0
            complexity_score += 1
        
        # Medium features
        if '-sV' in command:
            features['has_service_detection'] = 1
            complexity_score += 2
        if '-O' in command:
            features['has_os_detection'] = 1
            complexity_score += 2
        if '--script' in command:
            features['has_scripts'] = 1
            complexity_score += 2
        
        # Hard features
        if '-sS' in command:
            features['has_stealth'] = 1
            complexity_score += 3
        if '-sU' in command:
            complexity_score += 2
        if '--traceroute' in command:
            complexity_score += 1
        if '-f' in command or 'fragment' in command:
            features['has_stealth'] = 1
            complexity_score += 3
        if 'decoy' in command or 'spoof' in command:
            features['has_stealth'] = 1
            complexity_score += 4
        
        features['complexity_score'] = complexity_score
        
        return features


class HybridNmapClassifier:
    """
    Hybrid classifier combining:
    ✅ Neo4j Knowledge Graph
    ✅ Machine Learning (Random Forest)
    ✅ Expert Rules
    """
    
    def __init__(self, neo4j_uri: str = None):
        """Initialize classifier"""
        self.neo4j = Neo4jConnector(neo4j_uri) if neo4j_uri else None
        self.feature_extractor = NmapFeatureExtractor()
        self.model = None
        self.le_complexity = LabelEncoder()
        self.feature_names = []
        logger.info("🚀 Hybrid Classifier initialized!")
    
    def train(self, dataset_path: str) -> Dict:
        """Train classifier from CSV dataset"""
        logger.info(f"📚 Loading dataset from {dataset_path}")
        
        df = pd.read_csv(dataset_path)
        logger.info(f"✅ Loaded {len(df)} samples")
        
        # Extract features for all commands
        feature_list = []
        for cmd in df['command']:
            features = self.feature_extractor.extract_features(cmd)
            feature_list.append(features)
        
        feature_df = pd.DataFrame(feature_list)
        self.feature_names = feature_df.columns.tolist()
        
        X = feature_df.values
        y = self.le_complexity.fit_transform(df['complexity'])
        
        # Train Random Forest
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42
        )
        self.model.fit(X, y)
        
        # Calculate accuracy
        train_score = self.model.score(X, y)
        logger.info(f"🎯 Training accuracy: {train_score:.2%}")
        
        # Feature importance
        importances = self.model.feature_importances_
        top_features = sorted(
            zip(self.feature_names, importances),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        logger.info(f"⭐ Top features: {top_features}")
        
        return {
            'accuracy': train_score,
            'model': self.model,
            'feature_names': self.feature_names,
            'classes': self.le_complexity.classes_.tolist(),
            'top_features': top_features
        }
    
    def predict(self, command: str) -> Dict:
        """Predict complexity of a command"""
        if not self.model:
            logger.error("❌ Model not trained!")
            return None
        
        features = self.feature_extractor.extract_features(command)
        feature_values = [features.get(name, 0) for name in self.feature_names]
        
        # ML Prediction
        ml_pred_idx = self.model.predict([feature_values])[0]
        ml_complexity = self.le_complexity.classes_[ml_pred_idx]
        ml_confidence = self.model.predict_proba([feature_values])[0][ml_pred_idx]
        
        # Rule-based prediction
        rule_complexity = self._rule_based_predict(command, features)
        
        # Ensemble prediction
        final_complexity = self._ensemble_predict(
            ml_complexity,
            rule_complexity,
            ml_confidence
        )
        
        return {
            'command': command,
            'ml_prediction': ml_complexity,
            'ml_confidence': ml_confidence,
            'rule_prediction': rule_complexity,
            'final_prediction': final_complexity,
            'features': features,
            'complexity_score': features.get('complexity_score', 0)
        }
    
    def _rule_based_predict(self, command: str, features: Dict) -> str:
        """Rule-based prediction"""
        complexity_score = features.get('complexity_score', 0)
        
        if '-sn' in command and '-sV' not in command and '-O' not in command:
            return 'EASY'
        
        if complexity_score >= 8:
            return 'HARD'
        elif complexity_score >= 4:
            return 'MEDIUM'
        else:
            return 'EASY'
    
    def _ensemble_predict(self, ml_pred: str, rule_pred: str, confidence: float) -> str:
        """Combine ML and rule-based predictions"""
        if ml_pred == rule_pred:
            return ml_pred
        
        # If ML confidence is high, trust it
        if confidence > 0.85:
            return ml_pred
        
        # Otherwise, trust rule-based
        return rule_pred
    
    def batch_predict(self, commands: List[str]) -> pd.DataFrame:
        """Predict multiple commands"""
        results = []
        for cmd in commands:
            pred = self.predict(cmd)
            if pred:
                results.append(pred)
        
        return pd.DataFrame(results)
    
    def save_model(self, path: str):
        """Save trained model"""
        with open(path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'le_complexity': self.le_complexity,
                'feature_names': self.feature_names
            }, f)
        logger.info(f"💾 Model saved to {path}")
    
    def load_model(self, path: str):
        """Load trained model"""
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.model = data['model']
            self.le_complexity = data['le_complexity']
            self.feature_names = data['feature_names']
        logger.info(f"✅ Model loaded from {path}")


def main():
    """Main execution"""
    logger.info("=" * 60)
    logger.info("🔥 HYBRID NMAP CLASSIFIER - Neo4j + ML")
    logger.info("=" * 60)
    
    # Initialize classifier
    classifier = HybridNmapClassifier()
    
    # Train from CSV
    logger.info("\n📚 TRAINING PHASE")
    dataset_path = "/home/claude/nmap_dataset_hybrid.csv"
    train_results = classifier.train(dataset_path)
    
    logger.info("\n🎯 PREDICTION EXAMPLES")
    
    # Test cases
    test_commands = [
        "nmap -sn 192.168.1.0/24",  # EASY - ping scan
        "nmap -sV -O 192.168.1.1",  # MEDIUM - service + OS detection
        "nmap -sS -p- -sV --script vuln -T5 192.168.1.0/24",  # HARD - stealth + scripts
        "nmap -p 80,443 192.168.1.1",  # EASY - simple port scan
        "nmap -p- --script default,vuln -T5 192.168.0.0/16",  # HARD - all ports + scripts + timing
    ]
    
    for cmd in test_commands:
        result = classifier.predict(cmd)
        logger.info(f"\n📌 Command: {cmd}")
        logger.info(f"   ML: {result['ml_prediction']} ({result['ml_confidence']:.1%})")
        logger.info(f"   Rules: {result['rule_prediction']}")
        logger.info(f"   Final: ⚡ {result['final_prediction']}")
        logger.info(f"   Score: {result['complexity_score']}")
    
    # Save model
    logger.info("\n💾 SAVING MODEL")
    classifier.save_model("/home/claude/hybrid_classifier.pkl")
    
    logger.info("\n✅ Classification complete!")


if __name__ == "__main__":
    main()