from typing import Dict, List, Optional
import json


class FinalDecisionAgent:
    """Makes final decision on which command to execute"""
    
    def __init__(self):
        self.decision_criteria = {
            'validity': 0.40,      # 40% - Must be valid
            'score': 0.30,         # 30% - Overall score
            'conflicts': 0.20,     # 20% - No conflicts
            'complexity': 0.10     # 10% - Simpler is better
        }
    
    def decide(self, candidates: List[Dict]) -> Dict:
        """
        Choose the best command from multiple candidates
        
        Args:
            candidates: List of command validation results
                       Each must have: command, valid, score, source_agent
            
        Returns:
            Decision dictionary with chosen command and explanation
        """
        if not candidates:
            return {
                'success': False,
                'chosen_command': None,
                'reason': 'No candidates provided',
                'confidence': 0
            }
        
        # Filter valid candidates
        valid_candidates = [c for c in candidates if c.get('valid', False)]
        
        if not valid_candidates:
            # No valid candidates - choose least bad
            return self._choose_least_bad(candidates)
        
        # Score each valid candidate
        scored_candidates = []
        for candidate in valid_candidates:
            decision_score = self._calculate_decision_score(candidate)
            scored_candidates.append({
                **candidate,
                'decision_score': decision_score
            })
        
        # Sort by decision score
        scored_candidates.sort(key=lambda x: x['decision_score'], reverse=True)
        
        best = scored_candidates[0]
        
        # Calculate confidence
        confidence = self._calculate_confidence(scored_candidates)
        
        # Generate explanation
        explanation = self._generate_explanation(best, scored_candidates)
        
        return {
            'success': True,
            'chosen_command': best['command'],
            'source_agent': best.get('source_agent', 'Unknown'),
            'score': best['score'],
            'grade': best.get('grade', 'N/A'),
            'decision_score': best['decision_score'],
            'confidence': confidence,
            'explanation': explanation,
            'alternatives': [
                {
                    'command': c['command'],
                    'score': c['score'],
                    'decision_score': c['decision_score'],
                    'source': c.get('source_agent', 'Unknown')
                }
                for c in scored_candidates[1:3]  # Top 3 alternatives
            ]
        }
    
    def _calculate_decision_score(self, candidate: Dict) -> float:
        """
        Calculate decision score based on multiple criteria
        
        Args:
            candidate: Candidate command with validation results
            
        Returns:
            Decision score (0-100)
        """
        score = 0
        
        # Validity (40%)
        if candidate.get('valid', False):
            score += 40
        
        # Overall score (30%)
        overall_score = candidate.get('score', 0)
        score += (overall_score / 100) * 30
        
        # No conflicts (20%)
        has_conflicts = len(candidate.get('errors', [])) > 0
        if not has_conflicts:
            score += 20
        
        # Simplicity (10%) - fewer flags is better
        command = candidate.get('command', '')
        complexity = len([p for p in command.split() if p.startswith('-')])
        simplicity_score = max(0, 10 - complexity)
        score += simplicity_score
        
        return min(100, score)
    
    def _calculate_confidence(self, candidates: List[Dict]) -> float:
        """
        Calculate confidence in the decision
        
        Args:
            candidates: Scored candidates
            
        Returns:
            Confidence percentage (0-100)
        """
        if len(candidates) == 1:
            # Only one option
            return 70 + (candidates[0]['decision_score'] * 0.3)
        
        best_score = candidates[0]['decision_score']
        second_best_score = candidates[1]['decision_score'] if len(candidates) > 1 else 0
        
        # Higher confidence if clear winner
        gap = best_score - second_best_score
        
        if gap > 20:
            confidence = 90 + (gap * 0.2)
        elif gap > 10:
            confidence = 80 + (gap * 0.5)
        else:
            confidence = 70 + (gap * 0.5)
        
        return min(100, confidence)
    
    def _generate_explanation(self, best: Dict, all_candidates: List[Dict]) -> str:
        """
        Generate human-readable explanation
        
        Args:
            best: Best candidate
            all_candidates: All candidates
            
        Returns:
            Explanation string
        """
        lines = []
        
        # Why this command was chosen
        lines.append(f"Selected command from {best.get('source_agent', 'Unknown')} agent")
        lines.append(f"Validation score: {best['score']}/100 (Grade: {best.get('grade', 'N/A')})")
        lines.append(f"Decision score: {best['decision_score']:.1f}/100")
        
        # Reasons
        reasons = []
        if best.get('valid', False):
            reasons.append("✅ Passes all validation checks")
        if best['score'] >= 80:
            reasons.append("✅ High quality command")
        if len(best.get('errors', [])) == 0:
            reasons.append("✅ No conflicts detected")
        if len([p for p in best['command'].split() if p.startswith('-')]) <= 5:
            reasons.append("✅ Simple and focused")
        
        if reasons:
            lines.append("\nStrengths:")
            lines.extend([f"  {r}" for r in reasons])
        
        # Weaknesses
        warnings = best.get('warnings', [])
        if warnings:
            lines.append("\nWarnings:")
            lines.extend([f"  ⚠️  {w}" for w in warnings[:3]])
        
        # Comparison with alternatives
        if len(all_candidates) > 1:
            lines.append(f"\nConsidered {len(all_candidates)} alternatives")
            lines.append(f"Best alternative scored: {all_candidates[1]['decision_score']:.1f}/100")
        
        return "\n".join(lines)
    
    def _choose_least_bad(self, candidates: List[Dict]) -> Dict:
        """
        When no valid candidates exist, choose least problematic
        
        Args:
            candidates: List of invalid candidates
            
        Returns:
            Decision with warning
        """
        # Sort by score anyway
        sorted_candidates = sorted(candidates, 
                                  key=lambda x: x.get('score', 0), 
                                  reverse=True)
        
        least_bad = sorted_candidates[0]
        
        return {
            'success': False,
            'chosen_command': None,
            'reason': 'No valid commands available',
            'least_bad_option': least_bad['command'],
            'issues': least_bad.get('errors', []),
            'confidence': 0,
            'explanation': (
                f"All commands failed validation. "
                f"The least problematic was: {least_bad['command']} "
                f"(score: {least_bad.get('score', 0)}/100)"
            )
        }
    
    def generate_decision_report(self, decision: Dict) -> str:
        """
        Generate formatted decision report
        
        Args:
            decision: Decision result
            
        Returns:
            Formatted report
        """
        report = []
        report.append("=" * 70)
        report.append("FINAL DECISION REPORT")
        report.append("=" * 70)
        
        if decision['success']:
            report.append(f"\n✅ DECISION: APPROVE")
            report.append(f"\nChosen Command: {decision['chosen_command']}")
            report.append(f"Source: {decision['source_agent']}")
            report.append(f"Confidence: {decision['confidence']:.1f}%")
            report.append(f"\n{decision['explanation']}")
            
            if decision.get('alternatives'):
                report.append("\n" + "-" * 70)
                report.append("ALTERNATIVES CONSIDERED:")
                report.append("-" * 70)
                for i, alt in enumerate(decision['alternatives'], 1):
                    report.append(
                        f"{i}. {alt['command']} "
                        f"(score: {alt['decision_score']:.1f}, source: {alt['source']})"
                    )
        else:
            report.append(f"\n❌ DECISION: REJECT")
            report.append(f"\nReason: {decision['reason']}")
            if decision.get('least_bad_option'):
                report.append(f"\nLeast bad option: {decision['least_bad_option']}")
                report.append("\nIssues:")
                for issue in decision.get('issues', []):
                    report.append(f"  - {issue}")
        
        report.append("\n" + "=" * 70)
        
        return "\n".join(report)


# Test function
if __name__ == "__main__":
    agent = FinalDecisionAgent()
    
    # Simulate candidates from different agents
    candidates = [
        {
            'command': 'nmap -sS -p 80,443 -T4 -v 192.168.1.1',
            'source_agent': 'RAG_Agent',
            'valid': True,
            'score': 95,
            'grade': 'A',
            'errors': [],
            'warnings': []
        },
        {
            'command': 'nmap -sS -p 80,443,22,21,25 -A -T4 192.168.1.1',
            'source_agent': 'Phi4_Model',
            'valid': True,
            'score': 88,
            'grade': 'B',
            'errors': [],
            'warnings': ['Aggressive scan may be slow']
        },
        {
            'command': 'nmap -sS -sT -p- 192.168.1.1',
            'source_agent': 'Diffusion_Model',
            'valid': False,
            'score': 45,
            'grade': 'F',
            'errors': ['Conflict: -sS and -sT'],
            'warnings': ['Scanning all ports is slow']
        }
    ]
    
    decision = agent.decide(candidates)
    report = agent.generate_decision_report(decision)
    print(report)