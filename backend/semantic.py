import requests
from flask import request, jsonify
import google.generativeai as genai
from bs4 import BeautifulSoup
import fitz  # PyMuPDF
import os
import re
import base64
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel("gemini-2.5-flash-preview-04-17")
# model = genai.GenerativeModel("gemini-2.5-pro-exp-03-25")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
groq_model = "mistral-saba-24b"

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
    return text[:80000]  # Truncate to fit token limits

# def generate_fixed_spelling(text, query):
#     """Generate fixed spelling using Gemini"""
#     prompt = f"""
#     Given this content: {text}
#     Check if the query has been misspelled and ONLY return the corrected spelling.
#     If there are several possible corrections (like "color" vs "colour" or "twenty one" vs "21" vs "twenty-one"), return all possible corrections.
#     Also return capitalization variations (like "Los Angeles" vs "los angeles" or "Los Angeles" vs "LOS ANGELES").
#     Generate this for the query: "{query}". Return ONLY carrot (^) separated terms.
#     """
#     response = gemini_model.generate_content(prompt)
#     if response is None:
#         return []
#     return [term.strip() for term in response.text.split('^') if term.strip()]
def generate_fixed_spelling(text, query):
    """Generate fixed spelling using Groq"""
    #     Also return all capitalization variations (like "Los Angeles" vs "los angeles" or "Los Angeles" vs "LOS ANGELES").
    prompt = f"""
    Given this content: {text}
    Check if the query has been misspelled and ONLY return the corrected spelling.
    If there are several possible corrections (like "color" vs "colour" or "twenty one" vs "21" vs "twenty-one"), return all possible corrections.
    Return maximum 5 terms and ensure that each term appears in the context text.
    Generate this for the query: "{query}". Return list of terms separated by a caret (^) like so: "^term1^term2^term3^".
    """
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": prompt
            }],
            model=groq_model,  # Fastest model
            temperature=0.1,
            max_tokens=1000
        )
        
        response = chat_completion.choices[0].message.content
        # print(f"response in spelling: {response}")
        # return [term.strip() for term in response.split('^') if term.strip()]
        return process_response(response)
    
    except Exception as e:
        print(f"Groq API Error: {str(e)}")
        return []
    
# def generate_similar_terms(text, query):
#     """Generate search terms using Gemini"""
#     prompt = f"""
#     Given this content: {text} and this query: {query}
#     Generate 5-10 search terms that are directly relevant to the query (synonyms and very related concepts), based on the context of the text.
#     Make sure the search terms exactly exist in the context text.
#     Do not include any terms that are not directly relevant to the query.
#     Do not include spelling variations or corrections.
#     Return ONLY carrot (^) separated terms.
#     """
#     response = gemini_model.generate_content(prompt)
#     if response is None:
#         return []
#     return [term.strip() for term in response.text.split('^') if term.strip()]

def generate_similar_terms(text, query, spelling_fix_terms):
    """Generate search terms using Groq"""
    prompt = f"""
    Given this content: {text} and this query: {query}. The query may be misspelled, it may be: {spelling_fix_terms}.
    If there are any phrases or terms that are synonyms or very related concepts to the query, return them.
    Make sure the search terms exactly exist in the context text.
    If there are no terms that are synonyms or very related concepts to the query, do not return anything. 
    If the query is not relevant to the text, do not return anything.
    Do not include any terms that are not directly relevant to the query.
    Do not include any explanation.
    Return only a maximum of 10 such terms.
    Return ONLY caret (^) separated terms like this: "^term1^term2^term3^".
    """

    try:
        chat_completion = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": prompt
            }],
            model=groq_model,
            temperature=0.1,
            max_tokens=1000
        )
        
        response = chat_completion.choices[0].message.content
        # print(f"response in similar terms: {response}")
        # return [term.strip() for term in response.split('^') if term.strip()]
        return process_response(response)
    
    except Exception as e:
        print(f"Groq API Error: {str(e)}")
        return []
    
def process_response(response):
    # Split by '^' and process all cases
    print(f"********* response: {response}")
    split_response = response.split('^')
    
    # Get all non-empty terms after first caret
    terms = [
        term.strip() for term in split_response[1:]  if term.strip() and len(term.strip()) < 50
    ]
    # print(f"* gemini_response: * {response} \n terms: {terms}")
    return terms

def ensure_phrase_appears_in_text(phrase, text):
    """Check if a phrase appears in the text"""
    # Normalize both text and phrase to lowercase for case-insensitive comparison
    lower_text = text.lower()
    lower_phrase = phrase.lower()
    # Check if the phrase is in the text
    return lower_phrase in lower_text

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
    related_terms = generate_similar_terms(clean_text, query, spelling_fix_terms)

    return related_terms

def find_relevant_Images(raw_text, related_terms):
    soup = BeautifulSoup(raw_text, 'html.parser')
    images = soup.find_all('img')
    relevant_images = []

    for img in images:
        alt_text = img.get('alt', '').lower()
        title_text = img.get('title', '').lower()
        src = img.get('src', '').lower()
        # orig_src = img.get('src', '')

    # Check nearby text (e.g., parent or sibling tags)
        surrounding_text = ''
        parent = img.find_parent()
        if parent:
            surrounding_text = parent.get_text(separator=' ', strip=True).lower()

        # Combine everything to one string to match against
        combined_text = f"{alt_text} {title_text} {src} {surrounding_text}"

        for term in related_terms:
            if term.lower() in combined_text:
                relevant_images.append({

                    'src': src,
                    'alt': alt_text,
                    'title': title_text,
                    'matched_term': term
                })
                break  # Once matched, no need to check other terms for this image

    return relevant_images

def semantic_find_html(raw_text, orig_raw, query): 
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
    related_terms = generate_similar_terms(clean_text, query, spelling_fix_terms)
    # print(f"initial spelling fix terms: {spelling_fix_terms}")
    # print(f"initial related terms: {related_terms}")
    spelling_fix_terms = [elem for elem in spelling_fix_terms if ensure_phrase_appears_in_text(elem, clean_text)]
    # print(ensure_phrase_appears_in_text("assam", clean_text))
    # print(f"last 30 chars of clean text: {clean_text[-30:]}")
    related_terms = [elem for elem in related_terms if ensure_phrase_appears_in_text(elem, clean_text)]

    # check overlap between lists and within lists
    
    overlap = set(spelling_fix_terms) & set(related_terms)
    # print(f"overlap: {overlap} \n spelling_fix_terms: {spelling_fix_terms} \n related_terms: {related_terms}")
    spelling_fix_terms = list(set(spelling_fix_terms))
    related_terms = list(set(related_terms) - overlap)
    # print(f"spelling_fix_terms: {spelling_fix_terms} \n related_terms: {related_terms}")

    relevant_images = find_relevant_Images(orig_raw, related_terms)

    return {
        "related_terms": related_terms,
        "spelling_fix_terms": spelling_fix_terms,
        "relevant_images": relevant_images
    }

### DEBUG 

if __name__ == "__main__":
    print("\nGenerating")

    file_path = "splitgeek.html"
    related_terms = semantic_find(file_path, "int")
    raw_text = upload_file(file_path)
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content_orig = f.read()
    query = "int"
    # images = find_relevant_Images(html_content_orig, related_terms)
    related_terms = semantic_find("ww2.html", "axis powers")
    raw_text = upload_file("ww2.html")
    with open('ww2.html', 'r', encoding='utf-8') as f:
        html_content_orig = f.read()
    query = "axis powers"
    images = find_relevant_Images(html_content_orig, related_terms)
    results = semantic_find_html(raw_text, html_content_orig, query)
    
    # if spelling_fix_terms:
    #     for i, term in enumerate(spelling_fix_terms, 1):
    #         print(f"{i}. {term}")
    # print("\nGenerated similar terms:")
    # for i, term in enumerate(related_terms, 1):
    #     print(f"{i}. {term}")
    if results:
        print("\n=== Related Terms ===")
        for term in results["related_terms"]:
            print(f"- {term}")

        print("\n=== Spelling Fix Terms ===")
        for term in results["spelling_fix_terms"]:
            print(f"- {term}")

        print("\n=== Relevant Images ===")
        for img_info in results["relevant_images"]:
            print(f"Matched Term: {img_info['matched_term']}")
            print(f"Src: {img_info['src']}")
            print(f"Alt: {img_info['alt']}")
            print(f"Title: {img_info['title']}")
            print("-" * 40)