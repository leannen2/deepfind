import requests
import google.generativeai as genai
from bs4 import BeautifulSoup
import fitz  # PyMuPDF
import os
import re
import base64
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
# model = genai.GenerativeModel('gemini-pro')
model = genai.GenerativeModel("gemini-2.5-flash-preview-04-17")


def extract_text(input_source):
    """Extract text from URL (HTML/PDF) or local PDF file"""
    try:
        # Handle URLs
        if input_source.startswith(('http://', 'https://')):
            response = requests.get(input_source)
            response.raise_for_status()
            
            if input_source.lower().endswith('.pdf'):
                # PDF URL
                return extract_text_from_pdf(response.content)
            else:
                # HTML URL
                return extract_text_from_html(response.text)
        
        # # Handle local PDF files
        # elif input_source.lower().endswith('.pdf'):
        #     with open(input_source, 'rb') as f:
        #         return extract_text_from_pdf(f.read())
        
        else:
            raise ValueError("Unsupported file type. Please provide a webpage URL or PDF.")
            
    except Exception as e:
        print(f"Error processing input: {e}")
        return ""

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

def generate_search_terms(text, query):
    """Generate search terms using Gemini"""
    prompt = f"""
    Given this content: {text}
    Generate 5-10 search terms (synonyms, spelling corrections, related concepts)
    for the query: "{query}". Return ONLY comma-separated terms.
    """
    response = model.generate_content(prompt)
    return [term.strip() for term in response.text.split(',') if term.strip()]

if __name__ == "__main__":
    # Get user input
    source = input("Enter URL or PDF file path: ").strip()
    query = input("Enter search query: ").strip()
    
    # Extract text
    raw_text = extract_text(source)
    if not raw_text:
        print("Failed to extract text")
        exit()
    
    # Preprocess and generate terms
    clean_text = preprocess_text(raw_text)
    search_terms = generate_search_terms(clean_text, query)
    
    print("\nGenerated search terms:")
    for i, term in enumerate(search_terms, 1):
        print(f"{i}. {term}")