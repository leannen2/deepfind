from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from sklearn.metrics.pairwise import cosine_similarity
from bs4 import BeautifulSoup
import fitz  # PyMuPDF
import numpy as np
import os
import base64
import re

app = Flask(__name__)
CORS(app)

# Load Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("models/embedding-001")

def extract_text_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.get_text(separator=' ', strip=True)

def extract_text_from_pdf(base64_pdf):
    pdf_bytes = base64.b64decode(base64_pdf)
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def preprocess_text(text):
    text = re.sub(r'\s+', ' ', text).strip()
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < 500:
            current_chunk += " " + sentence if current_chunk else sentence
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

def embed_text(texts):
    response = model.embed_content(
        contents=texts,
        task_type="RETRIEVAL_QUERY",  # or "RETRIEVAL_DOCUMENT" depending on your case
        title="User Query"
    )
    embeddings = [e.embedding for e in response.embeddings]
    return np.array(embeddings)

@app.route("/search", methods=["POST"])
def search():
    data = request.json
    query = data.get("query", "")
    content = data.get("content", "")
    content_type = data.get("contentType", "html")

    if not query or not content:
        return jsonify({"error": "Query and content are required"}), 400

    try:
        if content_type == "html":
            full_text = extract_text_from_html(content)
        elif content_type == "pdf":
            full_text = extract_text_from_pdf(content)
        else:
            return jsonify({"error": "Unsupported content type"}), 400

        chunks = preprocess_text(full_text)
        if not chunks:
            return jsonify({"results": []}), 200

        chunk_embeddings = embed_text(chunks)
        query_embedding = embed_text([query])[0]

        similarities = cosine_similarity([query_embedding], chunk_embeddings)[0]

        results = []
        for i, (chunk, score) in enumerate(zip(chunks, similarities)):
            if score > 0.5:
                results.append({
                    "text": chunk,
                    "score": float(score),
                    "index": i
                })

        results = sorted(results, key=lambda x: x["score"], reverse=True)
        return jsonify({"results": results[:10]}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)