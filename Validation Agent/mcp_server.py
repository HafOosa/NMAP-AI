

from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import Dict, List
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from validator import NmapValidator


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize validator (singleton)
validator = None


def get_validator():
    """Get or create validator instance"""
    global validator
    if validator is None:
        validator = NmapValidator()
    return validator


@app.route('/', methods=['GET'])
def home():
    """API home page"""
    return jsonify({
        'service': 'NMAP Validator MCP Server',
        'version': '1.0',
        'person': 'Person 5',
        'endpoints': {
            'GET /': 'This help page',
            'GET /health': 'Health check',
            'POST /validate': 'Validate single command',
            'POST /validate/multiple': 'Validate multiple commands',
            'POST /validate/report': 'Get full validation report',
            'GET /stats': 'Get validator statistics'
        },
        'status': 'running'
    })


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        val = get_validator()
        return jsonify({
            'status': 'healthy',
            'validator': 'ready',
            'neo4j': 'connected'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503


@app.route('/validate', methods=['POST'])
def validate_command():
    """
    Validate a single Nmap command
    
    Request Body:
    {
        "command": "nmap -sS -p 80,443 192.168.1.1",
        "verbose": false  // optional
    }
    
    Response:
    {
        "command": "...",
        "valid": true/false,
        "score": 95,
        "grade": "A",
        "errors": [],
        "warnings": [],
        "suggestions": []
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'command' not in data:
            return jsonify({
                'error': 'Missing required field: command'
            }), 400
        
        command = data['command']
        verbose = data.get('verbose', False)
        
        # Validate command
        val = get_validator()
        result = val.validate_single_command(command, verbose=verbose)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'command': data.get('command', 'unknown')
        }), 500


@app.route('/validate/multiple', methods=['POST'])
def validate_multiple():
    """
    Validate multiple commands and choose best
    
    Request Body:
    {
        "commands": [
            "nmap -sS -p 80,443 192.168.1.1",
            "nmap -A -T4 192.168.1.1"
        ],
        "source_agents": ["RAG", "Phi4"]  // optional
    }
    
    Response:
    {
        "decision": {
            "success": true,
            "chosen_command": "...",
            "source_agent": "RAG",
            "score": 95,
            "confidence": 92.5,
            "explanation": "..."
        },
        "all_results": [...]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'commands' not in data:
            return jsonify({
                'error': 'Missing required field: commands'
            }), 400
        
        commands = data['commands']
        source_agents = data.get('source_agents', None)
        
        if not isinstance(commands, list) or len(commands) == 0:
            return jsonify({
                'error': 'commands must be a non-empty list'
            }), 400
        
        # Validate multiple commands
        val = get_validator()
        result = val.validate_multiple_commands(commands, source_agents)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/validate/report', methods=['POST'])
def get_report():
    """
    Get detailed validation report
    
    Request Body:
    {
        "command": "nmap -sS -p 80,443 192.168.1.1"
    }
    
    Response:
    {
        "report": "Formatted text report..."
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'command' not in data:
            return jsonify({
                'error': 'Missing required field: command'
            }), 400
        
        command = data['command']
        
        # Get full report
        val = get_validator()
        report = val.get_full_report(command)
        
        return jsonify({
            'report': report,
            'command': command
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/stats', methods=['GET'])
def get_stats():
    """
    Get validator statistics
    
    Response:
    {
        "total_requests": 42,
        "components": {
            "syntax_checker": "ready",
            "conflict_detector": "ready",
            "heuristic_checker": "ready",
            "scoring_system": "ready",
            "final_decision": "ready"
        }
    }
    """
    try:
        return jsonify({
            'components': {
                'syntax_checker': 'ready',
                'conflict_detector': 'ready',
                'heuristic_checker': 'ready',
                'scoring_system': 'ready',
                'final_decision': 'ready',
                'docker_sandbox': 'ready'
            },
            'status': 'operational'
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': {
            'GET /': 'API documentation',
            'GET /health': 'Health check',
            'POST /validate': 'Validate single command',
            'POST /validate/multiple': 'Validate multiple commands',
            'POST /validate/report': 'Get validation report'
        }
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal server error',
        'message': str(error)
    }), 500


def main():
    """Run the MCP server"""
    print("="*70)
    print("NMAP VALIDATOR MCP SERVER")
    print("="*70)
    print("\nInitializing validator...")
    
    # Initialize validator
    global validator
    validator = NmapValidator()
    
    print("\n✅ Validator ready!")
    print("\nStarting MCP Server...")
    print("API available at: http://localhost:5000")
    print("\nEndpoints:")
    print("  GET  /              - API documentation")
    print("  GET  /health        - Health check")
    print("  POST /validate      - Validate single command")
    print("  POST /validate/multiple - Validate multiple commands")
    print("  POST /validate/report   - Get validation report")
    print("  GET  /stats         - Statistics")
    print("\nPress Ctrl+C to stop\n")
    print("="*70 + "\n")
    
    # Run server
    app.run(host='0.0.0.0', port=5000, debug=False)


if __name__ == '__main__':
    main()