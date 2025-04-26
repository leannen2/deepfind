from flask import Flask, jsonify
from flask_cors import CORS
from semantic import * 
app = Flask(__name__)
CORS(app)  # this allows all origins by default

@app.route('/api/dummy', methods=['GET'])
def dummy_endpoint():
    return jsonify({
        'message': 'This is a dummy API response!',
        'status': 'success'
    })

@app.route('/api/find', methods=['POST'])
def find():
    try:
        data = request.json
        content = data.get('content')
        content_type = data.get('contentType')
        query = data.get('query')

        if not content or not content_type or not query:
            return jsonify({'error': 'Missing content, contentType, or query'}), 400

        # Use the same logic as handle_upload
        if content_type == 'html':
            text = extract_text_from_html(content)
        elif content_type == 'pdf':
            pdf_bytes = base64.b64decode(content)
            text = extract_text_from_pdf(pdf_bytes)
        else:
            return jsonify({'error': f"Unsupported content type: {content_type}"}), 400

        if not text:
            return jsonify({'error': 'Text extraction failed'}), 500

        # Now perform semantic search
        related_terms = semantic_find_html(text, query)

        return jsonify({
            'message': 'Search terms generated successfully',
            'similar_terms': related_terms,
            'status': 'success'
        })

    except Exception as e:
        return jsonify({'error': f'Exception: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)
