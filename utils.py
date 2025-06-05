import fitz  # PyMuPDF
import re
import requests
import json
import os
import sys
import traceback

# Add safe import handling
try:
    from prompts.claude_prompt_notes import claude_prompt_notes
    from prompts.claude_prompt_qna import claude_prompt_qna
    print("✅ Prompts imported successfully")
except ImportError as e:
    print(f"⚠️ Warning: Could not import prompts: {e}")
    # Fallback prompts
    claude_prompt_notes = "Extract the following content into 3-5 bullet-point notes for exam revision:\n\n{content}"
    claude_prompt_qna = "Generate 3-5 practice questions based on this content:\n\n{content}"

def extract_text_from_pdf(pdf_path):
    """Extract clean text from PDF using PyMuPDF"""
    try:
        print(f"📂 Opening PDF: {pdf_path}")
        
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        doc = fitz.open(pdf_path)
        text = ""
        
        print(f"📄 PDF has {len(doc)} pages")
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            page_text = page.get_text()
            text += page_text + "\n"
            print(f"📝 Processed page {page_num + 1}")
        
        doc.close()
        
        # Clean the text
        text = clean_text(text)
        print(f"✅ Text extraction completed. Length: {len(text)}")
        return text
        
    except Exception as e:
        print(f"❌ Error extracting text from PDF: {e}")
        traceback.print_exc()
        raise Exception(f"Error extracting text from PDF: {str(e)}")

def clean_text(text):
    """Clean and normalize extracted text"""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep punctuation
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\"\'\/]', '', text)
    
    # Remove very short lines (likely headers/footers)
    lines = text.split('\n')
    cleaned_lines = [line.strip() for line in lines if len(line.strip()) > 10]
    
    return '\n'.join(cleaned_lines)

def chunk_text(text, chunk_size=1000, overlap=200):
    """Split text into overlapping chunks"""
    if not text:
        return []
    
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    
    return chunks

def call_claude_api(prompt, content):
    """Call Claude API with the given prompt and content"""
    # For this hackathon version, we'll use a mock response
    # In production, you would integrate with actual Claude API
    
    # Mock responses for demonstration
    if "notes" in prompt.lower():
        return generate_mock_notes(content)
    else:
        return generate_mock_questions(content)

def generate_mock_notes(content):
    """Generate mock study notes (replace with actual API call)"""
    # This is a simplified version - in real implementation, use Claude API
    lines = content.split('. ')[:5]  # Take first 5 sentences
    notes = []
    
    for i, line in enumerate(lines):
        if len(line.strip()) > 20:
            notes.append(f"• {line.strip()}")
    
    if not notes:
        notes = ["• Key concepts from this section need review"]
    
    return '\n'.join(notes[:5])

def generate_mock_questions(content):
    """Generate mock practice questions (replace with actual API call)"""
    # This is a simplified version - in real implementation, use Claude API
    questions = [
        "1. What are the main concepts discussed in this section?",
        "2. How do these concepts relate to practical applications?",
        "3. What are the key differences between the mentioned approaches?",
        "4. Why is this topic important for the exam?",
        "5. Can you explain the underlying principles?"
    ]
    
    return '\n'.join(questions[:4])

def generate_notes(content):
    """Generate study notes from content"""
    try:
        prompt = claude_prompt_notes.format(content=content)
        notes = call_claude_api(prompt, content)
        return notes
    except Exception as e:
        return f"Error generating notes: {str(e)}"

def generate_questions(content):
    """Generate practice questions from content"""
    try:
        prompt = claude_prompt_qna.format(content=content)
        questions = call_claude_api(prompt, content)
        return questions
    except Exception as e:
        return f"Error generating questions: {str(e)}"

# Advanced API integration (for when you have actual API access)
def call_actual_claude_api(prompt, api_key=None):
    """
    Call actual Claude API - uncomment and modify when you have API access
    """
    # Example implementation:
    # headers = {
    #     'Authorization': f'Bearer {api_key}',
    #     'Content-Type': 'application/json'
    # }
    # 
    # data = {
    #     'prompt': prompt,
    #     'max_tokens': 500,
    #     'temperature': 0.7
    # }
    # 
    # response = requests.post('https://api.anthropic.com/v1/complete', 
    #                         headers=headers, json=data)
    # 
    # if response.status_code == 200:
    #     return response.json()['completion']
    # else:
    #     raise Exception(f"API call failed: {response.status_code}")
    
    pass