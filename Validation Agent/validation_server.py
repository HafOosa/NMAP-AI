#!/usr/bin/env python3
from flask import Flask, request, jsonify, send_from_directory
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from validator import NmapValidator
    HAS_VALIDATOR = True
    print("✅ Validator imported successfully")
except ImportError as e:
    print(f"❌ Cannot import validator: {e}")
    HAS_VALIDATOR = False

app = Flask(__name__, static_folder='.', static_url_path='')

# Global validator instance
validator = None

def get_validator():
    """Get or create validator instance"""
    global validator
    if validator is None and HAS_VALIDATOR:
        validator = NmapValidator()
    return validator

# Servir index.html à la racine
@app.route('/')
def index():
    return send_from_directory('.', 'templates/validator.html')

# Servir les fichiers statiques (CSS, JS, etc)
@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        val = get_validator()
        return jsonify({
            'status': 'ok',
            'validator': 'available' if HAS_VALIDATOR else 'missing',
            'neo4j': 'connected' if val else 'disconnected'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 503

@app.route('/api/validate', methods=['POST'])
def validate_command():
    """
    Validate a single NMAP command
    
    Request Body:
    {
        "command": "nmap -sS -p 80,443 192.168.1.1",
        "verbose": false
    }
    
    Response:
    {
        "command": "...",
        "valid": true,
        "score": 95,
        "grade": "A",
        "components": {...},
        "issues": {...}
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data'}), 400
        
        command = data.get('command', '')
        if not command:
            return jsonify({'error': 'Command required'}), 400
        
        if not HAS_VALIDATOR:
            return jsonify({'error': 'Validator not available', 'success': False}), 503
        
        verbose = data.get('verbose', False)
        
        # Get validator instance
        val = get_validator()
        if not val:
            return jsonify({'error': 'Validator initialization failed'}), 500
        
        # Validate command
        result = val.validate_single_command(command, verbose=False)
        
        # Structure response for frontend
        response = {
            'command': command,
            'valid': result['valid'],
            'score': result['score'],
            'grade': result['grade'],
            'components': result['breakdown'],  # breakdown contains syntax/conflicts/heuristics
            'issues': {
                'errors': result.get('errors', []),
                'warnings': result.get('warnings', []),
                'suggestions': result.get('suggestions', [])
            },
            'summary': result.get('summary', '')
        }
        
        if verbose:
            response['details'] = result
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"Error validating command: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/validate/multiple', methods=['POST'])
def validate_multiple():
    """
    Validate multiple commands and choose best
    
    Request Body:
    {
        "commands": ["nmap -sS ...", "nmap -A ..."],
        "source_agents": ["RAG", "Phi4"]
    }
    
    Response:
    {
        "decision": {
            "success": true,
            "chosen_command": "...",
            "score": 95,
            "grade": "A",
            ...
        },
        "all_results": [...]
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data'}), 400
        
        commands = data.get('commands', [])
        if not commands or not isinstance(commands, list):
            return jsonify({'error': 'Commands array required'}), 400
        
        if not HAS_VALIDATOR:
            return jsonify({'error': 'Validator not available'}), 503
        
        source_agents = data.get('source_agents', None)
        
        # Get validator
        val = get_validator()
        if not val:
            return jsonify({'error': 'Validator initialization failed'}), 500
        
        # Validate multiple commands
        result = val.validate_multiple_commands(commands, source_agents)
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get validator statistics"""
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
            'status': 'operational',
            'validator': 'available' if HAS_VALIDATOR else 'missing'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': {
            'GET /': 'Validator interface',
            'GET /health': 'Health check',
            'POST /api/validate': 'Validate single command',
            'POST /api/validate/multiple': 'Validate multiple commands',
            'GET /api/stats': 'Get statistics'
        }
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal server error',
        'message': str(error)
    }), 500

if __name__ == '__main__':
    print("\n" + "="*80)
    print("🚀 NMAP VALIDATOR Flask Server")
    print("="*80)
    print(f"Validator: {'✅ Available' if HAS_VALIDATOR else '❌ Missing'}")
    print(f"Working directory: {os.getcwd()}")
    print("\n📁 Serving validator.html from templates/")
    print("🌐 Open: http://127.0.0.1:5001")
    print("\nEndpoints:")
    print("  GET  /              - Validator Interface")
    print("  GET  /health        - Health Check")
    print("  POST /api/validate  - Validate Single Command")
    print("  POST /api/validate/multiple - Validate Multiple Commands")
    print("  GET  /api/stats     - Statistics")
    print("="*80 + "\n")
    
    # Initialize validator on startup
    if HAS_VALIDATOR:
        print("Initializing validator...")
        get_validator()
        print("✅ Validator ready!\n")
    
    app.run(debug=True, host='127.0.0.1', port=5001)