from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from backend.legal_simplifier import LegalDocumentSimplifier
import traceback

app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static')
CORS(app)

app.config['UPLOAD_FOLDER'] = 'frontend/static/uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx', 'txt'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

simplifier = LegalDocumentSimplifier()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_document():
    """Handle document upload"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        doc_name = request.form.get('doc_name', '')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Use PDF, DOCX, or TXT'}), 400
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        document_text = simplifier.load_document(filepath, doc_name if doc_name else filename)
        
        if "Error" in document_text:
            return jsonify({'error': document_text}), 500
        
        return jsonify({
            'success': True,
            'doc_name': doc_name if doc_name else filename,
            'length': len(document_text),
            'message': 'Document loaded successfully'
        })
    
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/documents', methods=['GET'])
def list_documents():
    """List all loaded documents"""
    try:
        docs = []
        for name, info in simplifier.loaded_documents.items():
            docs.append({
                'name': name,
                'loaded_at': info['loaded_at'],
                'length': len(info['text'])
            })
        return jsonify({'documents': docs})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_document():
    """Analyze a document"""
    try:
        data = request.json
        doc_name = data.get('doc_name')
        
        if not doc_name or doc_name not in simplifier.loaded_documents:
            return jsonify({'error': 'Document not found'}), 404
        
        document_text = simplifier.loaded_documents[doc_name]['text']
        analysis = simplifier.simplify_legal_text(document_text)
        simplifier.current_analysis = analysis
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
    
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/concerns', methods=['POST'])
def get_concerns():
    """Get concerning clauses"""
    try:
        data = request.json
        doc_name = data.get('doc_name')
        
        if not doc_name or doc_name not in simplifier.loaded_documents:
            return jsonify({'error': 'Document not found'}), 404
        
        document_text = simplifier.loaded_documents[doc_name]['text']
        concerns = simplifier.highlight_concerning_clauses(document_text)
        
        simplifier.current_analysis = f"CONCERNING CLAUSES ANALYSIS\n\n" + "\n".join([
            f"[{c['severity']}] {c['clause']}\nConcern: {c['concern']}\nRecommendation: {c['recommendation']}\n"
            for c in concerns
        ])
        
        return jsonify({
            'success': True,
            'concerns': concerns
        })
    
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/compare', methods=['POST'])
def compare_documents():
    """Compare two documents"""
    try:
        data = request.json
        doc1 = data.get('doc1')
        doc2 = data.get('doc2')
        
        if not doc1 or not doc2:
            return jsonify({'error': 'Two documents required'}), 400
        
        comparison = simplifier.compare_documents(doc1, doc2)
        simplifier.current_analysis = comparison
        
        return jsonify({
            'success': True,
            'comparison': comparison
        })
    
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat with the bot about documents"""
    try:
        data = request.json
        message = data.get('message')
        doc_name = data.get('doc_name')
        
        document_context = None
        if doc_name and doc_name in simplifier.loaded_documents:
            document_context = simplifier.loaded_documents[doc_name]['text']
        
        response = simplifier.chat(message, document_context)
        
        return jsonify({
            'success': True,
            'response': response
        })
    
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/save-pdf', methods=['POST'])
def save_pdf():
    """Save current analysis to PDF"""
    try:
        if not simplifier.current_analysis:
            return jsonify({'error': 'No analysis to save'}), 400
        
        data = request.json
        filename = data.get('filename', None)
        
        if filename and not filename.endswith('.pdf'):
            filename += '.pdf'
        
        filepath = simplifier.save_to_pdf(simplifier.current_analysis, filename)
        
        if filepath.startswith("Error"):
            return jsonify({'error': filepath}), 500
        
        return jsonify({
            'success': True,
            'filename': os.path.basename(filepath),
            'message': 'PDF saved successfully'
        })
    
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<filename>', methods=['GET'])
def download_pdf(filename):
    """Download generated PDF"""
    try:
        filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if not os.path.exists(filepath):
            filepath = filename  
        
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear', methods=['POST'])
def clear_conversation():
    """Clear conversation history"""
    try:
        simplifier.conversation_history = []
        return jsonify({'success': True, 'message': 'Conversation cleared'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)