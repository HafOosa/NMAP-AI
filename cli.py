

import argparse
import sys
import json
from validator import NmapValidator


def print_banner():
    """Print CLI banner"""
    print("="*70)
    print("NMAP VALIDATOR CLI - Person 5")
    print("="*70)
    print()


def validate_command(args):
    """Validate a single command"""
    print_banner()
    
    validator = NmapValidator()
    
    print(f"Validating command: {args.command}\n")
    
    result = validator.validate_single_command(args.command, verbose=args.verbose)
    
    if not args.verbose:
        # Compact output
        print(f"\n{'='*70}")
        print(f"RESULT")
        print(f"{'='*70}")
        print(f"Score:  {result['score']}/100")
        print(f"Grade:  {result['grade']}")
        print(f"Valid:  {'✅ YES' if result['valid'] else '❌ NO'}")
        
        if result['errors']:
            print(f"\n❌ Errors ({len(result['errors'])}):")
            for error in result['errors']:
                print(f"  - {error}")
        
        if result['warnings']:
            print(f"\n⚠️  Warnings ({len(result['warnings'])}):")
            for warning in result['warnings']:
                print(f"  - {warning}")
        
        if result['suggestions']:
            print(f"\n💡 Suggestions ({len(result['suggestions'])}):")
            for suggestion in result['suggestions']:
                print(f"  - {suggestion}")
        
        print(f"\n{result['summary']}")
        print(f"{'='*70}\n")
    
    if args.json:
        print("\nJSON Output:")
        print(json.dumps(result, indent=2))
    
    validator.close()
    
    # Exit code
    sys.exit(0 if result['valid'] else 1)


def validate_multiple(args):
    """Validate multiple commands"""
    print_banner()
    
    validator = NmapValidator()
    
    commands = args.commands
    agents = args.agents if args.agents else [f'Command_{i+1}' for i in range(len(commands))]
    
    result = validator.validate_multiple_commands(commands, agents)
    
    # Print decision
    print("\n" + "="*70)
    print("FINAL DECISION")
    print("="*70)
    
    decision = result['decision']
    
    if decision['success']:
        print(f"\n✅ Best Command: {decision['chosen_command']}")
        print(f"Source:      {decision['source_agent']}")
        print(f"Score:       {decision['score']}/100")
        print(f"Grade:       {decision['grade']}")
        print(f"Confidence:  {decision['confidence']:.1f}%")
        print(f"\nExplanation:\n{decision['explanation']}")
    else:
        print(f"\n❌ No valid command found")
        print(f"Reason: {decision['reason']}")
    
    print("="*70 + "\n")
    
    if args.json:
        print("\nJSON Output:")
        print(json.dumps(result, indent=2))
    
    validator.close()
    
    sys.exit(0 if decision['success'] else 1)


def get_report(args):
    """Get full validation report"""
    print_banner()
    
    validator = NmapValidator()
    
    report = validator.get_full_report(args.command)
    
    print(report)
    
    validator.close()


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description='NMAP Validator CLI - Person 5',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "nmap -sS -p 80,443 192.168.1.1"
  %(prog)s "nmap -A -T4 target.com" --verbose
  %(prog)s "nmap -sS -p 80 192.168.1.1" --json
  %(prog)s --multiple "nmap -sS -p 80 target" "nmap -A target"
  %(prog)s --report "nmap -sS -p 80,443 192.168.1.1"
        """
    )
    
    # Main command argument
    parser.add_argument(
        'command',
        nargs='?',
        help='Nmap command to validate'
    )
    
    # Options
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output (show all validation steps)'
    )
    
    parser.add_argument(
        '-j', '--json',
        action='store_true',
        help='Output results in JSON format'
    )
    
    parser.add_argument(
        '-m', '--multiple',
        nargs='+',
        dest='commands',
        help='Validate multiple commands and choose best'
    )
    
    parser.add_argument(
        '-a', '--agents',
        nargs='+',
        help='Agent names for multiple commands'
    )
    
    parser.add_argument(
        '-r', '--report',
        metavar='COMMAND',
        help='Get full validation report for command'
    )
    
    args = parser.parse_args()
    
    # Route to appropriate function
    try:
        if args.report:
            args.command = args.report
            get_report(args)
        elif args.commands:
            validate_multiple(args)
        elif args.command:
            validate_command(args)
        else:
            parser.print_help()
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nValidation cancelled by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()