

from validators.syntax_checker import SyntaxChecker
from validators.conflict_detector import ConflictDetector
from validators.heuristic_checker import HeuristicChecker
from validators.scoring_system import ScoringSystem
from validators.final_decision import FinalDecisionAgent
from typing import Dict, List


class NmapValidator:
    """Complete NMAP command validation system"""
    
    def __init__(self):
        """Initialize all validation components"""
        print("Starting NMAP Validator...")
        
        self.syntax_checker = SyntaxChecker()
        print("  - Syntax Checker loaded")
        
        self.conflict_detector = ConflictDetector()
        print("  - Conflict Detector loaded (with Neo4j KG)")
        
        self.heuristic_checker = HeuristicChecker()
        print("  - Heuristic Checker loaded")
        
        self.scoring_system = ScoringSystem()
        print("  - Scoring System loaded")
        
        self.final_decision = FinalDecisionAgent()
        print("  - Final Decision Agent loaded")
        
        print("\nNMAP Validator ready!\n")
    
    def validate_single_command(self, command: str, verbose: bool = True) -> Dict:
        """
        Validate a single Nmap command
        
        Args:
            command: Nmap command string
            verbose: Print detailed output
            
        Returns:
            Complete validation result
        """
        if verbose:
            print(f"{'='*70}")
            print(f"Validating: {command}")
            print(f"{'='*70}\n")
        
        # Step 1: Syntax check
        if verbose:
            print("Step 1: Checking syntax...")
        syntax_result = self.syntax_checker.check(command)
        if verbose:
            print(f"  Score: {syntax_result['score']}/100")
            if syntax_result['errors']:
                print(f"  Errors: {len(syntax_result['errors'])}")
        
        # Step 2: Conflict detection
        if verbose:
            print("\nStep 2: Checking conflicts (using Knowledge Graph)...")
        conflict_result = self.conflict_detector.check(command)
        if verbose:
            print(f"  Score: {conflict_result['score']}/100")
            if conflict_result.get('conflicts'):
                print(f"  Conflicts found: {len(conflict_result['conflicts'])}")
        
        # Step 3: Heuristic check
        if verbose:
            print("\nStep 3: Checking best practices...")
        heuristic_result = self.heuristic_checker.check(command)
        if verbose:
            print(f"  Score: {heuristic_result['score']}/100")
            if heuristic_result['warnings']:
                print(f"  Warnings: {len(heuristic_result['warnings'])}")
        
        # Step 4: Calculate overall score
        if verbose:
            print("\nStep 4: Calculating overall score...")
        scoring_result = self.scoring_system.calculate_score(
            syntax_result,
            conflict_result,
            heuristic_result
        )
        
        if verbose:
            print(f"  Overall Score: {scoring_result['score']}/100")
            print(f"  Grade: {scoring_result['grade']}")
            print(f"  Status: {'VALID' if scoring_result['valid'] else 'INVALID'}")
        
        # Combine all results
        result = {
            'command': command,
            'valid': scoring_result['valid'],
            'score': scoring_result['score'],
            'grade': scoring_result['grade'],
            'breakdown': scoring_result['breakdown'],
            'errors': scoring_result['errors'],
            'warnings': scoring_result['warnings'],
            'suggestions': scoring_result['suggestions'],
            'summary': scoring_result['summary'],
            'source_agent': 'User'
        }
        
        if verbose:
            print(f"\n{scoring_result['summary']}")
            print(f"{'='*70}\n")
        
        return result
    
    def validate_multiple_commands(self, 
                                   commands: List[str], 
                                   source_agents: List[str] = None) -> Dict:
        """
        Validate multiple commands and choose the best one
        
        Args:
            commands: List of command strings
            source_agents: List of agent names that generated each command
            
        Returns:
            Final decision with best command
        """
        if not commands:
            return {'success': False, 'reason': 'No commands provided'}
        
        if source_agents is None:
            source_agents = [f'Agent_{i+1}' for i in range(len(commands))]
        
        print(f"{'='*70}")
        print(f"VALIDATING {len(commands)} COMMANDS")
        print(f"{'='*70}\n")
        
        # Validate each command
        results = []
        for i, (cmd, agent) in enumerate(zip(commands, source_agents), 1):
            print(f"\n[{i}/{len(commands)}] Validating command from {agent}...")
            print(f"Command: {cmd}\n")
            
            result = self.validate_single_command(cmd, verbose=False)
            result['source_agent'] = agent
            results.append(result)
            
            print(f"  Score: {result['score']}/100 | Grade: {result['grade']} | "
                  f"Valid: {'YES' if result['valid'] else 'NO'}")
        
        # Make final decision
        print(f"\n{'='*70}")
        print("MAKING FINAL DECISION...")
        print(f"{'='*70}\n")
        
        decision = self.final_decision.decide(results)
        
        return {
            'decision': decision,
            'all_results': results
        }
    
    def get_full_report(self, command: str) -> str:
        """
        Get complete validation report for a command
        
        Args:
            command: Nmap command string
            
        Returns:
            Formatted report string
        """
        result = self.validate_single_command(command, verbose=False)
        return self.scoring_system.generate_report(command, result)
    
    def close(self):
        """Clean up resources"""
        self.conflict_detector.close()
        print("Validator closed")


def main():
    """Main function for testing"""
    # Initialize validator
    validator = NmapValidator()
    
    print("\n" + "="*70)
    print("DEMO: SINGLE COMMAND VALIDATION")
    print("="*70 + "\n")
    
    # Test single command
    test_command = "nmap -sS -p 80,443 -T4 -v 192.168.1.1"
    result = validator.validate_single_command(test_command)
    
    # Get full report
    print("\n" + validator.get_full_report(test_command))
    
    print("\n" + "="*70)
    print("DEMO: MULTIPLE COMMAND VALIDATION")
    print("="*70 + "\n")
    
    # Test multiple commands
    test_commands = [
        "nmap -sS -p 80,443 -T4 -v 192.168.1.1",
        "nmap -sS -p 80,443,22,21,25 -A -T4 192.168.1.1",
        "nmap -sS -sT -p- 192.168.1.1"
    ]
    
    agents = ['RAG_Agent', 'Phi4_Model', 'Diffusion_Model']
    
    result = validator.validate_multiple_commands(test_commands, agents)
    
    # Print final decision
    print("\n" + validator.final_decision.generate_decision_report(result['decision']))
    
    # Close validator
    validator.close()


if __name__ == "__main__":
    main()