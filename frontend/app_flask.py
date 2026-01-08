#!/usr/bin/env python3
from flask import Flask, request, jsonify, send_from_directory
import asyncio
import sys
from pathlib import Path

# orchestrator.py est dans Nmap_Agents (parent de frontend/)
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

try:
    from orchestrator import NmapAIOrchestrator
    HAS_ORCHESTRATOR = True
    print(f"✅ Orchestrator imported from {parent_dir}")
except ImportError as e:
    print(f"❌ Cannot import orchestrator: {e}")
    HAS_ORCHESTRATOR = False

app = Flask(__name__, static_folder='.', static_url_path='')

# Servir index.html à la racine
@app.route('/')
def index():
    return send_from_directory('.', 'templates/index.html')

# Servir les fichiers statiques (CSS, JS, etc)
@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'orchestrator': 'available' if HAS_ORCHESTRATOR else 'missing'})

@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data'}), 400
        
        query = data.get('query', '')
        if not query:
            return jsonify({'error': 'Query required'}), 400
        
        if not HAS_ORCHESTRATOR:
            return jsonify({'error': 'Orchestrator not available', 'success': False}), 503
        
        orchestrator = NmapAIOrchestrator()
        result = asyncio.run(orchestrator.process(query))
        
        return jsonify({
            'success': result.success,
            'original_query': result.original_query,
            'command': result.final_command,
            'complexity': result.complexity,
            'confidence': result.confidence,
            'validation_score': result.validation_score,
            'validation_grade': result.validation_grade,
            'steps': [{'name': s.name, 'status': s.status} for s in result.steps]
        }), 200
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/classify', methods=['POST'])
def classify():
    try:
        data = request.get_json()
        command = data.get('command', '')
        if not command:
            return jsonify({'error': 'Command required'}), 400
        
        try:
            from tools.classify_tool import classify_query
            result = asyncio.run(classify_query(command))
            return jsonify({
                'success': True,
                'command': command,
                'complexity': result.get('complexity'),
                'confidence': result.get('confidence')
            }), 200
        except:
            return jsonify({'error': 'Classifier not available'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*80)
    print("🚀 NMAP-AI Flask Server")
    print("="*80)
    print(f"Orchestrator: {'✅ Available' if HAS_ORCHESTRATOR else '❌ Missing'}")
    print(f"Looking for orchestrator.py in: {parent_dir}")
    print("\n📁 Serving index.html from current directory")
    print("🌐 Open: http://127.0.0.1:5000")
    print("="*80 + "\n")
    app.run(debug=True, host='127.0.0.1', port=5000)