from flask import Flask, jsonify
from flask_cors import CORS
from semantic import * 
from google.oauth2 import id_token
from google.auth.transport import requests
import requests as pyrequests  # to avoid conflict with Flask's requests
from datetime import datetime
import os
from dotenv import load_dotenv
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)  # this allows all origins by default

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# Connect to MongoDB Atlas
client = MongoClient(os.environ["MONGODB_URI"])
db = client["ctrl++"]
users_collection = db["users"]

@app.route('/auth/google', methods=['POST'])
def google_auth():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing token"}), 400

    token = auth_header.split(" ")[1]

    try:
        # Use token to query Google's userinfo endpoint
        response = pyrequests.get(
            'https://www.googleapis.com/oauth2/v1/userinfo',
            headers={'Authorization': f'Bearer {token}'}
        )

        if response.status_code != 200:
            return jsonify({"error": "Invalid token"}), 401

        user_info = response.json()
        google_id = user_info.get('id')
        # Upsert user into MongoDB
        users_collection.update_one(
            { "_id": google_id },
            {
                "$set": {
                    "email": user_info.get('email'),
                    "name": user_info.get('name')
                },
                "$setOnInsert": {
                    "topics": {}
                }
            },
            upsert=True
        )

        return jsonify({
            "googleId": user_info.get('id'),
            "email": user_info.get('email'),
            "name": user_info.get('name'),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/user/add_link', methods=['POST'])
def add_link():
    data = request.json
    user_id = data.get('userId')  # this should be Google ID
    topic = data.get('topic')
    link = data.get('link')  # dict with title, url

    if not all([user_id, topic, link]):
        return jsonify({"error": "Missing userId, topic, or link"}), 400

    if not isinstance(link, dict) or not all(k in link for k in ['title', 'url']):
        return jsonify({"error": "Link must contain 'title' and 'url'"}), 400

    link['date_added'] = datetime.utcnow().isoformat()

    result = users_collection.update_one(
        { "_id": user_id },
        { "$push": { f"topics.{topic}": link } }
    )

    if result.matched_count == 0:
        return jsonify({"error": "User not found"}), 404

    return jsonify({ "status": "success" })


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
    app.run(host="0.0.0.0", port=5000, debug=True)
