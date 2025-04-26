import requests
from flask import request, jsonify
import google.generativeai as genai
from bs4 import BeautifulSoup
import fitz  # PyMuPDF
import os
import re
import base64
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
genai.configure(api_key="AIzaSyB7qBez2qP9KVbWUo7mOZaYmlDQ09hDPu0")
# model = genai.GenerativeModel("gemini-2.5-flash-preview-04-17")
model = genai.GenerativeModel("gemini-2.5-pro-exp-03-25")

def upload_file(file_path):
    # Determine content type based on file extension
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    if ext == '.html' or ext == '.htm':
        content_type = 'html'
    elif ext == '.pdf':
        content_type = 'pdf'
    else:
        raise ValueError("Unsupported file type")

    # Read content
    with open(file_path, 'rb') as f:
        raw_bytes = f.read()

    if content_type == 'html':
        content = raw_bytes.decode('utf-8', errors='ignore')
        text = extract_text_from_html(content)
    elif content_type == 'pdf':
        content = base64.b64encode(raw_bytes).decode('utf-8')
        pdf_bytes = base64.b64decode(content)
        text = extract_text_from_pdf(pdf_bytes)

    return text

# @app.route('/upload', methods=['POST'])
def handle_upload():
    data = request.json
    content = data['content']
    content_type = data['contentType']

    if content_type == 'html':
        text = extract_text_from_html(content)
    elif content_type == 'pdf':
        pdf_bytes = base64.b64decode(content)
        text = extract_text_from_pdf(pdf_bytes)
    else:
        return jsonify({f"error": "Unsupported content type: {content_type}. Needs to be HTML or PDF."}), 400

def extract_text_from_html(html_content):
    """Extract text from HTML using BeautifulSoup"""
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.get_text(separator=' ', strip=True)

def extract_text_from_pdf(pdf_bytes):
    """Extract text from PDF bytes using PyMuPDF"""
    text = ""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

def preprocess_text(text):
    """Clean and truncate text for Gemini"""
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:10000]  # Truncate to fit token limits

def generate_fixed_spelling(text, query):
    """Generate fixed spelling using Gemini"""
    prompt = f"""
    Given this content: {text}
    Check if the query has been misspelled and ONLY return the corrected spelling.
    If there are several possible corrections (like "color" vs "colour" or "twenty one" vs "21" vs "twenty-one"), return all possible corrections.
    Also return capitalization variations (like "Los Angeles" vs "los angeles" or "Los Angeles" vs "LOS ANGELES").
    Generate this for the query: "{query}". Return ONLY carrot (^) separated terms.
    """
    response = model.generate_content(prompt)
    if response is None:
        return []
    return [term.strip() for term in response.text.split('^') if term.strip()]

def generate_similar_terms(text, query):
    """Generate search terms using Gemini"""
    prompt = f"""
    Given this content: {text} and this query: {query}
    Generate 5-10 search terms that are directly relevant to the query (synonyms and very related concepts), based on the context of the text.
    Make sure the search terms exactly exist in the context text.
    Do not include any terms that are not directly relevant to the query.
    Do not include spelling variations or corrections.
    Return ONLY carrot (^) separated terms.
    """
    response = model.generate_content(prompt)
    if response is None:
        return []
    return [term.strip() for term in response.text.split('^') if term.strip()]

def semantic_find(file_path, query): 
    # Extract text
    raw_text = upload_file(file_path)
    
    if not raw_text:
        print("Failed to extract text")
        exit()
    
    # Preprocess and generate terms
    clean_text = preprocess_text(raw_text)
    # print(f"nCleaned text (truncated):\n{clean_text[:500]}...")
    # print(f"length of preprocessed text {len(clean_text)}")  # Show only the first 500 characters
    spelling_fix_terms = generate_fixed_spelling(clean_text, query)
    related_terms = generate_similar_terms(clean_text, query)

    return related_terms

def semantic_find_html(raw_text, query): 
    # Extract text
    # raw_text = upload_file(file_path)
    
    if not raw_text:
        print("Failed to extract text")
        exit()
    
    # Preprocess and generate terms
    clean_text = preprocess_text(raw_text)
    # print(f"nCleaned text (truncated):\n{clean_text[:500]}...")
    # print(f"length of preprocessed text {len(clean_text)}")  # Show only the first 500 characters
    spelling_fix_terms = generate_fixed_spelling(clean_text, query)
    related_terms = generate_similar_terms(clean_text, query)

    return related_terms

### DEBUG 

if __name__ == "__main__":
    print("\nGenerated fixed-spelling terms:")
    related_terms = semantic_find("ww2.html", "axis powers")
    # if spelling_fix_terms:
    #     for i, term in enumerate(spelling_fix_terms, 1):
    #         print(f"{i}. {term}")
    print("\nGenerated similar terms:")
    for i, term in enumerate(related_terms, 1):
        print(f"{i}. {term}")