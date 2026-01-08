from typing import Dict, List
import config


class ScoringSystem:
    """Combines validation results and assigns overall score"""
    
    def __init__(self):
        self.weights = config.WEIGHTS
        self.grade_thresholds = config.GRADE_THRESHOLDS
    
    def calculate_score(self, 
                       syntax_result: Dict, 
                       conflict_result: Dict, 
                       heuristic_result: Dict) -> Dict:
        """
        Calculate overall score from all validation results
        
        Args:
            syntax_result: Result from SyntaxChecker
            conflict_result: Result from ConflictDetector
            heuristic_result: Result from HeuristicChecker
            
        Returns:
            Combined scoring result
        """
        # Extract individual scores
        syntax_score = syntax_result.get('score', 0)
        conflict_score = conflict_result.get('score', 0)
        heuristic_score = heuristic_result.get('score', 0)
        
        # Calculate weighted score
        overall_score = (
            syntax_score * self.weights['syntax'] +
            conflict_score * self.weights['conflicts'] +
            heuristic_score * self.weights['heuristics']
        )
        
        # Round to integer
        overall_score = int(round(overall_score))
        
        # Determine grade
        grade = self._get_grade(overall_score)
        
        # Collect all issues
        all_errors = []
        all_warnings = []
        all_suggestions = []
        
        # Syntax errors
        all_errors.extend(syntax_result.get('errors', []))
        all_warnings.extend(syntax_result.get('warnings', []))
        
        # Conflict errors
        all_errors.extend(conflict_result.get('errors', []))
        all_warnings.extend(conflict_result.get('warnings', []))
        
        # Heuristic warnings
        all_warnings.extend(heuristic_result.get('warnings', []))
        all_suggestions.extend(heuristic_result.get('suggestions', []))
        
        # Determine overall validity
        is_valid = (
            syntax_result.get('valid', False) and
            conflict_result.get('valid', False) and
            len(all_errors) == 0
        )
        
        # Build detailed breakdown
        breakdown = {
            'syntax': {
                'score': syntax_score,
                'weight': self.weights['syntax'],
                'contribution': syntax_score * self.weights['syntax']
            },
            'conflicts': {
                'score': conflict_score,
                'weight': self.weights['conflicts'],
                'contribution': conflict_score * self.weights['conflicts']
            },
            'heuristics': {
                'score': heuristic_score,
                'weight': self.weights['heuristics'],
                'contribution': heuristic_score * self.weights['heuristics']
            }
        }
        
        return {
            'valid': is_valid,
            'score': overall_score,
            'grade': grade,
            'breakdown': breakdown,
            'errors': all_errors,
            'warnings': all_warnings,
            'suggestions': all_suggestions,
            'summary': self._generate_summary(overall_score, grade, is_valid),
            'component': 'scoring_system'
        }
    
    def _get_grade(self, score: int) -> str:
        """
        Convert score to letter grade
        
        Args:
            score: Overall score (0-100)
            
        Returns:
            Letter grade (A-F)
        """
        for grade, threshold in sorted(self.grade_thresholds.items(), 
                                      key=lambda x: x[1], 
                                      reverse=True):
            if score >= threshold:
                return grade
        return 'F'
    
    def _generate_summary(self, score: int, grade: str, is_valid: bool) -> str:
        """
        Generate human-readable summary
        
        Args:
            score: Overall score
            grade: Letter grade
            is_valid: Whether command is valid
            
        Returns:
            Summary string
        """
        if not is_valid:
            return "❌ Command is INVALID and cannot be executed"
        
        if grade == 'A':
            return "✅ Excellent! Command follows best practices"
        elif grade == 'B':
            return "✅ Good command with minor improvements possible"
        elif grade == 'C':
            return "⚠️  Acceptable but several issues detected"
        elif grade == 'D':
            return "⚠️  Poor command quality - significant issues"
        else:
            return "❌ Failing grade - major problems detected"
    
    def compare_commands(self, results: List[Dict]) -> Dict:
        """
        Compare multiple command validation results
        
        Args:
            results: List of validation results
            
        Returns:
            Comparison result with best command
        """
        if not results:
            return {'best': None, 'ranking': []}
        
        # Sort by score
        ranked = sorted(results, key=lambda x: x.get('score', 0), reverse=True)
        
        # Find best valid command
        best = next((r for r in ranked if r.get('valid', False)), None)
        
        return {
            'best': best,
            'ranking': ranked,
            'comparison': [
                {
                    'command': r.get('command', 'Unknown'),
                    'score': r.get('score', 0),
                    'grade': r.get('grade', 'F'),
                    'valid': r.get('valid', False)
                }
                for r in ranked
            ]
        }
    
    def generate_report(self, command: str, result: Dict) -> str:
        """
        Generate detailed text report
        
        Args:
            command: Original command
            result: Validation result
            
        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 70)
        report.append("NMAP COMMAND VALIDATION REPORT")
        report.append("=" * 70)
        report.append(f"\nCommand: {command}")
        report.append(f"\nOverall Score: {result['score']}/100 (Grade: {result['grade']})")
        report.append(f"Status: {'✅ VALID' if result['valid'] else '❌ INVALID'}")
        report.append(f"\n{result['summary']}")
        
        # Breakdown
        report.append("\n" + "-" * 70)
        report.append("SCORE BREAKDOWN:")
        report.append("-" * 70)
        
        breakdown = result['breakdown']
        for component, data in breakdown.items():
            report.append(
                f"{component.capitalize():15} | "
                f"Score: {data['score']:3d}/100 | "
                f"Weight: {data['weight']:.0%} | "
                f"Contribution: {data['contribution']:.1f}"
            )
        
        # Errors
        if result['errors']:
            report.append("\n" + "-" * 70)
            report.append("❌ ERRORS:")
            report.append("-" * 70)
            for i, error in enumerate(result['errors'], 1):
                report.append(f"{i}. {error}")
        
        # Warnings
        if result['warnings']:
            report.append("\n" + "-" * 70)
            report.append("⚠️  WARNINGS:")
            report.append("-" * 70)
            for i, warning in enumerate(result['warnings'], 1):
                report.append(f"{i}. {warning}")
        
        # Suggestions
        if result['suggestions']:
            report.append("\n" + "-" * 70)
            report.append("💡 SUGGESTIONS:")
            report.append("-" * 70)
            for i, suggestion in enumerate(result['suggestions'], 1):
                report.append(f"{i}. {suggestion}")
        
        report.append("\n" + "=" * 70)
        
        return "\n".join(report)


# Test function
if __name__ == "__main__":
    scorer = ScoringSystem()
    
    # Simulate results from checkers
    test_cases = [
        {
            'command': 'nmap -sS -p 80,443 -T4 -v 192.168.1.1',
            'syntax': {'valid': True, 'score': 100, 'errors': [], 'warnings': []},
            'conflicts': {'valid': True, 'score': 100, 'errors': [], 'warnings': []},
            'heuristics': {'valid': True, 'score': 90, 'warnings': [], 'suggestions': ['Add output format']}
        },
        {
            'command': 'nmap -sS -sT 192.168.1.1',
            'syntax': {'valid': True, 'score': 100, 'errors': [], 'warnings': []},
            'conflicts': {'valid': False, 'score': 40, 'errors': ['Conflict: -sS and -sT'], 'warnings': []},
            'heuristics': {'valid': True, 'score': 70, 'warnings': ['No timing'], 'suggestions': []}
        }
    ]
    
    for test in test_cases:
        result = scorer.calculate_score(
            test['syntax'],
            test['conflicts'],
            test['heuristics']
        )
        
        report = scorer.generate_report(test['command'], result)
        print(report)
        print("\n")