

from neo4j import GraphDatabase
from typing import Dict, List, Set
import config


class ConflictDetector:
    """Detects conflicts using Neo4j Knowledge Graph"""
    
    def __init__(self, uri=config.NEO4J_URI, user=config.NEO4J_USER, password=config.NEO4J_PASSWORD):
        """Initialize connection to Neo4j"""
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            self._test_connection()
            print("✅ Connected to Neo4j Knowledge Graph")
        except Exception as e:
            print(f"❌ Failed to connect to Neo4j: {e}")
            self.driver = None
    
    def _test_connection(self):
        """Test Neo4j connection"""
        with self.driver.session() as session:
            result = session.run("MATCH (n) RETURN count(n) as count")
            count = result.single()["count"]
            print(f"✅ Knowledge Graph loaded: {count} nodes")
    
    def check(self, command: str) -> Dict:
        """
        Check for conflicts in the command
        
        Args:
            command: Nmap command string
            
        Returns:
            Dictionary with conflict detection results
        """
        if not self.driver:
            return {
                'valid': False,
                'score': 0,
                'errors': ['Neo4j connection not available'],
                'warnings': [],
                'conflicts': [],
                'component': 'conflict_detector'
            }
        
        # Parse command to extract flags
        flags = self._extract_flags(command)
        
        if not flags:
            return {
                'valid': True,
                'score': 100,
                'errors': [],
                'warnings': [],
                'conflicts': [],
                'component': 'conflict_detector'
            }
        
        # Query Neo4j for conflicts
        conflicts = self._check_conflicts_in_kg(flags)
        
        # Calculate score
        errors = []
        warnings = []
        
        if conflicts:
            for conflict in conflicts:
                errors.append(
                    f"Conflict: {conflict['option1']} conflicts with {conflict['option2']} - "
                    f"Reason: {conflict['reason']}"
                )
        
        # Additional heuristic checks
        self._check_common_conflicts(flags, warnings)
        
        valid = len(conflicts) == 0
        score = 100 if valid else max(0, 100 - (len(conflicts) * 30))
        
        return {
            'valid': valid,
            'score': score,
            'errors': errors,
            'warnings': warnings,
            'conflicts': conflicts,
            'component': 'conflict_detector'
        }
    
    def _extract_flags(self, command: str) -> List[str]:
        """Extract flags from command"""
        parts = command.split()
        flags = []
        
        for part in parts[1:]:  # Skip 'nmap'
            if part.startswith('-'):
                # Handle combined flags like -sS or separate like -p 80
                if len(part) > 2 and part[1] != '-':
                    # Could be -sS, -sT, etc.
                    flags.append(part[:3] if len(part) >= 3 else part)
                else:
                    flags.append(part)
        
        return list(set(flags))  # Remove duplicates
    
    def _check_conflicts_in_kg(self, flags: List[str]) -> List[Dict]:
        """
        Query Knowledge Graph for CONFLICTS_WITH relationships
        
        Args:
            flags: List of flags to check
            
        Returns:
            List of conflict dictionaries
        """
        conflicts = []
        
        with self.driver.session() as session:
            # Check each pair of flags
            for i, flag1 in enumerate(flags):
                for flag2 in flags[i+1:]:
                    # Query: Does flag1 conflict with flag2?
                    query = """
                    MATCH (n)-[r:CONFLICTS_WITH]->(m)
                    WHERE (n.name = $flag1 AND m.name = $flag2) OR
                          (n.name = $flag2 AND m.name = $flag1)
                    RETURN n.name as option1, m.name as option2, r.reason as reason
                    """
                    
                    result = session.run(query, flag1=flag1, flag2=flag2)
                    
                    for record in result:
                        conflicts.append({
                            'option1': record['option1'],
                            'option2': record['option2'],
                            'reason': record['reason']
                        })
        
        return conflicts
    
    def _check_common_conflicts(self, flags: List[str], warnings: List[str]):
        """
        Check for common conflicts not in KG
        (Backup heuristic checks)
        """
        # Check for multiple TCP scan types
        tcp_scans = [f for f in flags if f in ['-sS', '-sT', '-sA', '-sW', '-sM']]
        if len(tcp_scans) > 1:
            warnings.append(f"Multiple TCP scan types detected: {', '.join(tcp_scans)}")
        
        # Check UDP with TCP scans
        if '-sU' in flags and any(s in flags for s in ['-sS', '-sT']):
            warnings.append("UDP scan combined with TCP scan (this is valid but may be slow)")
        
        # Check for -F (fast) with -p- (all ports)
        if '-F' in flags and '-p' in flags:
            warnings.append("Fast scan (-F) with custom port specification may conflict")
    
    def get_recommendations(self, flags: List[str]) -> List[str]:
        """
        Get recommendations from Knowledge Graph
        Uses COMMONLY_USED_WITH relationships
        
        Args:
            flags: Current flags in command
            
        Returns:
            List of recommended flags
        """
        if not self.driver:
            return []
        
        recommendations = []
        
        with self.driver.session() as session:
            for flag in flags:
                query = """
                MATCH (n {name: $flag})-[r:COMMONLY_USED_WITH]->(m)
                RETURN m.name as recommendation, r.frequency as frequency
                ORDER BY frequency DESC
                LIMIT 3
                """
                
                result = session.run(query, flag=flag)
                
                for record in result:
                    rec = record['recommendation']
                    if rec not in flags:
                        recommendations.append(rec)
        
        return recommendations
    
    def get_conflict_graph(self) -> Dict:
        """
        Get full conflict graph for visualization
        
        Returns:
            Dictionary with nodes and edges
        """
        if not self.driver:
            return {'nodes': [], 'edges': []}
        
        nodes = []
        edges = []
        
        with self.driver.session() as session:
            # Get all nodes involved in conflicts
            query = """
            MATCH (n)-[r:CONFLICTS_WITH]->(m)
            RETURN DISTINCT n.name as node1, m.name as node2, r.reason as reason
            """
            
            result = session.run(query)
            
            seen_nodes = set()
            for record in result:
                node1 = record['node1']
                node2 = record['node2']
                
                if node1 not in seen_nodes:
                    nodes.append({'id': node1, 'label': node1})
                    seen_nodes.add(node1)
                
                if node2 not in seen_nodes:
                    nodes.append({'id': node2, 'label': node2})
                    seen_nodes.add(node2)
                
                edges.append({
                    'from': node1,
                    'to': node2,
                    'label': record['reason']
                })
        
        return {'nodes': nodes, 'edges': edges}
    
    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()
            print("✅ Neo4j connection closed")
    
    def __del__(self):
        """Destructor to ensure connection is closed"""
        self.close()


# Test function
if __name__ == "__main__":
    detector = ConflictDetector()
    
    test_commands = [
        "nmap -sS -p 80,443 192.168.1.1",          # Valid
        "nmap -sS -sT 192.168.1.1",                 # Conflict: two scan types
        "nmap -A -v -O target.com",                 # Valid
        "nmap -sU -sS -p 1-1000 192.168.1.1"       # Valid (UDP + TCP is ok)
    ]
    
    for cmd in test_commands:
        print(f"\n{'='*60}")
        print(f"Testing: {cmd}")
        print(f"{'='*60}")
        result = detector.check(cmd)
        print(f"Valid: {result['valid']}")
        print(f"Score: {result['score']}")
        
        if result['errors']:
            print(f"\n❌ Errors:")
            for error in result['errors']:
                print(f"  - {error}")
        
        if result['warnings']:
            print(f"\n⚠️  Warnings:")
            for warning in result['warnings']:
                print(f"  - {warning}")
        
        if result['conflicts']:
            print(f"\n🔥 Conflicts Found: {len(result['conflicts'])}")
            for conflict in result['conflicts']:
                print(f"  - {conflict}")
        
        # Get recommendations
        flags = detector._extract_flags(cmd)
        recommendations = detector.get_recommendations(flags)
        if recommendations:
            print(f"\n💡 Recommendations:")
            for rec in recommendations:
                print(f"  - Consider adding: {rec}")
    
    detector.close()