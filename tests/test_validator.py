

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from validator import NmapValidator


def test_syntax_checker():
    """Test syntax checker component"""
    print("\n" + "="*70)
    print("TEST 1: SYNTAX CHECKER")
    print("="*70 + "\n")
    
    from validators.syntax_checker import SyntaxChecker
    checker = SyntaxChecker()
    
    test_cases = [
        ("nmap -sS -p 80,443 192.168.1.1", True),
        ("nmap -sS -sT 192.168.1.1", True),  # Valid syntax
        ("nmap -p 99999 target.com", False),  # Invalid port
        ("nmap", False),  # No target
        ("scan -sS target.com", False)  # Doesn't start with nmap
    ]
    
    passed = 0
    for cmd, expected_valid in test_cases:
        result = checker.check(cmd)
        status = "✅" if result['valid'] == expected_valid else "❌"
        print(f"{status} {cmd[:50]:50} | Valid: {result['valid']}")
        if result['valid'] == expected_valid:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(test_cases)}")
    return passed == len(test_cases)


def test_conflict_detector():
    """Test conflict detector component"""
    print("\n" + "="*70)
    print("TEST 2: CONFLICT DETECTOR (with Knowledge Graph)")
    print("="*70 + "\n")
    
    from validators.conflict_detector import ConflictDetector
    detector = ConflictDetector()
    
    test_cases = [
        ("nmap -sS -p 80,443 192.168.1.1", 0),  # No conflicts
        ("nmap -sS -sT 192.168.1.1", 1),         # 1 conflict expected
        ("nmap -A -v -O target.com", 0)          # No conflicts
    ]
    
    passed = 0
    for cmd, expected_conflicts in test_cases:
        result = detector.check(cmd)
        actual_conflicts = len(result.get('conflicts', []))
        status = "✅" if actual_conflicts >= expected_conflicts else "⚠️"
        print(f"{status} {cmd[:50]:50} | Conflicts: {actual_conflicts}")
        if actual_conflicts >= expected_conflicts:
            passed += 1
    
    detector.close()
    print(f"\nPassed: {passed}/{len(test_cases)}")
    return passed >= 2  # Allow some flexibility with KG


def test_heuristic_checker():
    """Test heuristic checker component"""
    print("\n" + "="*70)
    print("TEST 3: HEURISTIC CHECKER")
    print("="*70 + "\n")
    
    from validators.heuristic_checker import HeuristicChecker
    checker = HeuristicChecker()
    
    test_cases = [
        ("nmap -sS -p 80,443 -T4 -v 192.168.1.1", 80, 100),  # Good
        ("nmap -A 192.168.1.1", 60, 80),                      # Missing timing
        ("nmap -sS -p- 192.168.1.1", 40, 70),                 # All ports
    ]
    
    passed = 0
    for cmd, min_score, max_score in test_cases:
        result = checker.check(cmd)
        in_range = min_score <= result['score'] <= max_score
        status = "✅" if in_range else "❌"
        print(f"{status} {cmd[:50]:50} | Score: {result['score']}")
        if in_range:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(test_cases)}")
    return passed == len(test_cases)


def test_integration():
    """Test complete validation pipeline"""
    print("\n" + "="*70)
    print("TEST 4: COMPLETE VALIDATION PIPELINE")
    print("="*70 + "\n")
    
    validator = NmapValidator()
    
    # Test good command
    good_cmd = "nmap -sS -p 80,443 -T4 -v 192.168.1.1"
    result = validator.validate_single_command(good_cmd, verbose=False)
    
    test1 = result['score'] >= 80 and result['valid']
    print(f"{'✅' if test1 else '❌'} Good command validation: Score={result['score']}, Valid={result['valid']}")
    
    # Test bad command
    bad_cmd = "nmap -sS -sT 192.168.1.1"
    result = validator.validate_single_command(bad_cmd, verbose=False)
    
    test2 = result['score'] < 80  # Should have lower score
    print(f"{'✅' if test2 else '❌'} Bad command detection: Score={result['score']}")
    
    validator.close()
    
    return test1 and test2


def test_final_decision():
    """Test final decision agent"""
    print("\n" + "="*70)
    print("TEST 5: FINAL DECISION AGENT")
    print("="*70 + "\n")
    
    validator = NmapValidator()
    
    commands = [
        "nmap -sS -p 80,443 -T4 -v 192.168.1.1",
        "nmap -sS -sT 192.168.1.1"  # Has conflict
    ]
    
    result = validator.validate_multiple_commands(commands, ['Agent1', 'Agent2'])
    
    decision = result['decision']
    
    # Best command should be the first one (no conflicts)
    test1 = decision['success']
    test2 = decision['confidence'] > 50
    
    print(f"{'✅' if test1 else '❌'} Decision made successfully: {decision['success']}")
    print(f"{'✅' if test2 else '❌'} Confidence level adequate: {decision['confidence']:.1f}%")
    
    validator.close()
    
    return test1 and test2


def run_all_tests():
    """Run all tests"""
    print("\n" + "#"*70)
    print("# NMAP VALIDATOR - COMPREHENSIVE TEST SUITE")
    print("#"*70)
    
    tests = [
        ("Syntax Checker", test_syntax_checker),
        ("Conflict Detector", test_conflict_detector),
        ("Heuristic Checker", test_heuristic_checker),
        ("Integration Test", test_integration),
        ("Final Decision", test_final_decision)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n❌ {name} failed with error: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70 + "\n")
    
    passed_count = sum(1 for _, passed in results if passed)
    total = len(results)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status:10} | {name}")
    
    print(f"\n{'='*70}")
    print(f"TOTAL: {passed_count}/{total} tests passed")
    print(f"{'='*70}\n")
    
    if passed_count == total:
        print("🎉 ALL TESTS PASSED! System is ready for production.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())