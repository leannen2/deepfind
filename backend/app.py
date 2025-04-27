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

@app.route('/user/get_topics', methods=['POST'])
def get_topics():
    data = request.json
    user_id = data.get('userId')
    if not user_id:
        return jsonify({"error": "Missing userId"}), 400
    user = users_collection.find_one({ "_id": user_id })
    if not user:
        return jsonify({"error": "User not found"}), 404
    topics = list(user.get("topics", {}).keys())
    return jsonify({
        "status": "success",
        "topics": topics
    })
    
@app.route('/user/get_links', methods=['POST'])
def get_links():
    try:
        data = request.get_json(force=True)
        user_id = data.get('userId')
        topic = data.get('topic')

        if not user_id or not topic:
            return jsonify({"error": "Missing userId or topic"}), 400

        user = users_collection.find_one({ "_id": user_id })
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Ensure topic exists and is a list
        topics = user.get("topics", {})
        links = topics.get(topic)
        if not links or not isinstance(links, list):
            return jsonify({"error": "No links found for this topic"}), 404

        return jsonify({
            "status": "success",
            "links": links
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/user/add_topic', methods=['POST'])
def add_topic():
    data = request.json
    user_id = data.get('userId')
    topic = data.get('topic')
    if not user_id or not topic:
        return jsonify({"error": "Missing userId or topic"}), 400
    # Check if user exists
    user = users_collection.find_one({ "_id": user_id })
    if not user:
        return jsonify({"error": "User not found"}), 404
    # Check if topic already exists
    if topic in user.get("topics", {}):
        return jsonify({"error": "Topic already exists"}), 400
    # Add topic to user
    result = users_collection.update_one(
        { "_id": user_id },
        { "$set": { f"topics.{topic}": [] } }
    )
    if result.matched_count == 0:
        return jsonify({"error": "User not found"}), 404
    if result.modified_count == 0:
        return jsonify({"error": "Topic already exists"}), 400
    return jsonify({
        "status": "success",
        "message": f"Topic '{topic}' added successfully."
    })

@app.route('/user/add_text_chunk', methods=['POST'])
def add_text_chunk():
    data = request.json
    user_id = data.get('userId')
    topic = data.get('topic')
    link_url = data.get('linkUrl')  # target link
    text_chunk = data.get('textChunk')

    if not all([user_id, topic, link_url, text_chunk]):
        return jsonify({"error": "Missing userId, topic, linkUrl, or textChunk"}), 400

    # Check if user exists
    user = users_collection.find_one({ "_id": user_id })
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Check if topic exists
    links = user.get("topics", {}).get(topic)
    if links is None:
        return jsonify({"error": "Topic does not exist"}), 400

    # Find the index of the link to update
    link_index = next((i for i, link in enumerate(links) if link.get("url") == link_url), None)
    if link_index is None:
        return jsonify({"error": "Link not found in topic"}), 404

    # Use the positional operator to push to textChunks of the matching link
    result = users_collection.update_one(
        {
            "_id": user_id,
            f"topics.{topic}.{link_index}.url": link_url
        },
        {
            "$push": { f"topics.{topic}.{link_index}.textChunks": text_chunk }
        }
    )

    if result.modified_count == 0:
        return jsonify({"error": "Failed to add text chunk"}), 500

    return jsonify({
        "status": "success",
        "message": f"Text chunk added to link '{link_url}' in topic '{topic}' successfully."
    })


@app.route('/user/delete_text_chunk', methods=['POST'])
def delete_text_chunk():
    data = request.json
    user_id = data.get('userId')
    topic = data.get('topic')
    text_chunk = data.get('textChunk')

    if not all([user_id, topic, text_chunk]):
        return jsonify({"error": "Missing userId, topic, or textChunk"}), 400

    # Check if user exists
    user = users_collection.find_one({ "_id": user_id })
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Check if topic exists
    if topic not in user.get("topics", {}):
        return jsonify({"error": "Topic does not exist"}), 400

    # Delete text chunk from the topic
    result = users_collection.update_one(
        { "_id": user_id },
        { "$pull": { f"topics.{topic}": text_chunk } }
    )

    if result.matched_count == 0:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "status": "success",
        "message": f"Text chunk deleted from topic '{topic}' successfully."
    })

@app.route('/user/delete_topic', methods=['POST'])
def delete_topic():
    data = request.json
    user_id = data.get('userId')
    topic = data.get('topic')
    if not user_id or not topic:
        return jsonify({"error": "Missing userId or topic"}), 400
    # Check if user exists
    user = users_collection.find_one({ "_id": user_id })
    if not user:
        return jsonify({"error": "User not found"}), 404
    # Check if topic exists
    if topic not in user.get("topics", {}):
        return jsonify({"error": "Topic does not exist"}), 400
    # Delete topic from user
    result = users_collection.update_one(
        { "_id": user_id },
        { "$unset": { f"topics.{topic}": "" } }
    )
    if result.matched_count == 0:
        return jsonify({"error": "User not found"}), 404
    if result.modified_count == 0:
        return jsonify({"error": "Topic does not exist"}), 400
    return jsonify({
        "status": "success",
        "message": f"Topic '{topic}' deleted successfully."
    })

@app.route('/user/add_link', methods=['POST'])
def add_link():
    data = request.json
    user_id = data.get('userId')  # Google ID
    topic = data.get('topic')
    link = data.get('link')  # dict with title, url

    if not all([user_id, topic, link]):
        return jsonify({"error": "Missing userId, topic, or link"}), 400

    if not isinstance(link, dict) or not all(k in link for k in ['title', 'url']):
        return jsonify({"error": "Link must contain 'title' and 'url'"}), 400

    # Check if user exists and topic contains the same link (by URL)
    user = users_collection.find_one({ "_id": user_id })
    if not user:
        return jsonify({"error": "User not found"}), 404

    existing_links = user.get("topics", {}).get(topic, [])
    if any(existing['url'] == link['url'] for existing in existing_links):
        return jsonify({ "status": "duplicate", "message": "Link already exists under this topic." })

    link['date_added'] = datetime.utcnow().isoformat()

    result = users_collection.update_one(
        { "_id": user_id },
        { "$push": { f"topics.{topic}": link } }
    )

    return jsonify({ "status": "success" })

@app.route('/user/delete_link', methods=['POST'])
def delete_link():
    data = request.json
    user_id = data.get('userId')  # Google ID
    topic = data.get('topic')
    url = data.get('url')  # We delete by URL

    if not all([user_id, topic, url]):
        return jsonify({"error": "Missing userId, topic, or url"}), 400

    result = users_collection.update_one(
        { "_id": user_id },
        { "$pull": { f"topics.{topic}": { "url": url } } }
    )

    if result.matched_count == 0:
        return jsonify({"error": "User not found"}), 404

    if result.modified_count == 0:
        return jsonify({"status": "not_found", "message": "Link not found in topic."})

    return jsonify({"status": "success", "message": "Link deleted."})


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
        result = semantic_find_html(text, content, query)
        related_terms = result["related_terms"]
        spelling_fix_terms = result["spelling_fix_terms"]
        relevant_images = result["relevant_images"]

        return jsonify({
            'message': 'Search terms generated successfully',
            'similar_terms': related_terms,
            'spelling_fix_terms': spelling_fix_terms,
            'relevant_images': relevant_images,
            'status': 'success'
        })

    except Exception as e:
        return jsonify({'error': f'Exception: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)
