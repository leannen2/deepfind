import requests
from flask import request, jsonify
from bs4 import BeautifulSoup
import fitz  # PyMuPDF
import os
import re
import base64
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# Configure Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
model = "deepseek-r1-distill-llama-70b"
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
    print(f"spelling_fix_terms: {spelling_fix_terms}")
    related_terms = generate_similar_terms(clean_text, query)
    print(f"related_terms: {related_terms}")
    terms = spelling_fix_terms + related_terms
    # print(f"terms: {terms}")
    return terms

def process_response(response):
    # Split by '^' and process all cases
    split_response = response.split('^')
    
    # Get all non-empty terms after first caret
    terms = [
        term.strip() 
        for term in split_response[1:-1]  # Skip everything before first ^
        if term.strip()
    ]
    # print(f"gemini_response: {response} \n terms: {terms}")
    return terms

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
    print(f"spelling_fix_terms: {spelling_fix_terms}")
    related_terms = generate_similar_terms(clean_text, query)
    print(f"related_terms: {related_terms}")

    return spelling_fix_terms.append(related_terms)


def generate_fixed_spelling(text, query):
    """Generate fixed spelling using Groq"""
    prompt = f"""
    Given this content: {text}
    Check if the query has been misspelled and ONLY return the corrected spelling.
    If there are several possible corrections (like "color" vs "colour" or "twenty one" vs "21" vs "twenty-one"), return all possible corrections.
    Also return all capitalization variations (like "Los Angeles" vs "los angeles" or "Los Angeles" vs "LOS ANGELES").
    Return maximum 5 terms and ensure that each term appears in the context text.
    Generate this for the query: "{query}". Return list of terms separated by a carat (^) like so: "^term1^term2^term3^".
    """

    # prompt = f"""
    # **Task**: Find EXACT variations of "{query}" that appear VERBATIM in the text below.
    # **Text Content**: {text}  # Truncate to focus on key content

    # **Strict Rules**:
    # 1. Return MAX 3 variations separated by ^
    # 2. Format: ^variation1^variation2^variation3^
    # 3. Only include variations that:
    # - Are exact matches from the text
    # - Match spelling/case/number patterns in text
    # 4. Never invent variations that don't exist
    # 5. If no variations exist, return empty

    # **Bad Example** (invented variations):
    # Query: "germany partner world war 2"
    # Response: ^Germany Partner^Germany partner^  # Not in text

    # **Good Example**:
    # Query: "germany partner world war 2"
    # Text Contains: "Germany allied with Italy in WWII"
    # Response: ^Germany allied^allied with Italy^WWII^"""
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": prompt
            }],
            model=model,  # Fastest model
            temperature=0.15,
            max_tokens=1000
        )
        
        response = chat_completion.choices[0].message.content
        # print(f"response in spelling: {response}")
        # return [term.strip() for term in response.split('^') if term.strip()]
        return process_response(response)
    
    except Exception as e:
        print(f"Groq API Error: {str(e)}")
        return []

def generate_similar_terms(text, query):
    """Generate search terms using Groq"""
    prompt = f"""

    Given this content: {text} and this query: {query}
    Generate 5-10 search terms that are directly relevant to the query (synonyms and very related concepts), based on the context of the text.
    Ensure that every term/phrase exactly exists in the context text.
    Do not include any terms that are not directly relevant to the query.
    Do not include spelling variations or corrections.
    Return list of terms separated by a carat (^) like so: "^term1^term2^term3^".
    
    **Task**: Find EXACT phrases from the text that answer: "{query}"""


    
    try:
        chat_completion = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": prompt
            }],
            model=model,
            temperature=0.15,
            max_tokens=1000
        )
        
        response = chat_completion.choices[0].message.content
        # return [term.strip() for term in response.split('^') if term.strip()]
        return process_response(response)
    
    except Exception as e:
        print(f"Groq API Error: {str(e)}")
        return []

# Rest of the original functions remain unchanged (upload_file, handle_upload, extract_text_from_html, etc.)

if __name__ == "__main__":
    print("\nGenerated terms to search:")
    related_terms = semantic_find("ww2.html", "germany partner")
    for i, term in enumerate(related_terms, 1):
        print(f"{i}. {term}")