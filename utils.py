import fitz  # PyMuPDF
import re
import requests
import json
import os
import sys
import traceback
from typing import List, Optional

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

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract clean text from PDF using PyMuPDF"""
    try:
        print(f"📂 Opening PDF: {pdf_path}")
        
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        doc = fitz.open(pdf_path)
        text = ""
        
        print(f"📄 PDF has {len(doc)} pages")
        
        for page_num in range(len(doc)):
            try:
                page = doc.load_page(page_num)
                page_text = page.get_text()
                
                # Skip if page has very little text (likely image-only)
                if len(page_text.strip()) > 50:
                    text += page_text + "\n\n"
                    print(f"📝 Processed page {page_num + 1} ({len(page_text)} chars)")
                else:
                    print(f"⚠️ Skipped page {page_num + 1} (insufficient text)")
                    
            except Exception as e:
                print(f"⚠️ Error processing page {page_num + 1}: {e}")
                continue
        
        doc.close()
        
        if not text.strip():
            raise ValueError("No text could be extracted from the PDF")
        
        # Clean the text
        text = clean_text(text)
        print(f"✅ Text extraction completed. Length: {len(text)} characters")
        return text
        
    except Exception as e:
        print(f"❌ Error extracting text from PDF: {e}")
        traceback.print_exc()
        raise Exception(f"Failed to extract text from PDF: {str(e)}")

def clean_text(text: str) -> str:
    """Clean and normalize extracted text"""
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove page numbers and headers/footers (common patterns)
    text = re.sub(r'\n\s*\d+\s*\n', '\n', text)  # Page numbers
    text = re.sub(r'\n\s*Page\s+\d+.*?\n', '\n', text, flags=re.IGNORECASE)
    
    # Remove very short lines (likely headers/footers)
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        # Keep lines that are substantial or contain important punctuation
        if len(line) > 15 or any(char in line for char in ['.', ':', ';', '?', '!']):
            cleaned_lines.append(line)
    
    cleaned_text = '\n'.join(cleaned_lines)
    
    # Remove excessive line breaks
    cleaned_text = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned_text)
    
    return cleaned_text.strip()

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks for better processing"""
    if not text:
        return []
    
    # Split by sentences first for better chunk boundaries
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        # Fallback to word-based chunking
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        return chunks
    
    # Sentence-based chunking
    chunks = []
    current_chunk = ""
    current_size = 0
    
    for sentence in sentences:
        sentence_words = len(sentence.split())
        
        if current_size + sentence_words > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            # Start new chunk with overlap
            overlap_sentences = current_chunk.split('.')[-2:]  # Keep last 2 sentences for overlap
            current_chunk = '. '.join(overlap_sentences) + '. ' + sentence
            current_size = len(current_chunk.split())
        else:
            current_chunk += sentence + '. '
            current_size += sentence_words
    
    # Add the last chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return [chunk for chunk in chunks if len(chunk.strip()) > 100]  # Filter out tiny chunks

def generate_smart_notes(content: str) -> str:
    """Generate intelligent study notes from content"""
    try:
        # Extract key information patterns
        notes = []
        
        # Find definitions and key terms
        definitions = extract_definitions(content)
        if definitions:
            notes.extend([f"• **{term}**: {definition}" for term, definition in definitions])
        
        # Find important concepts
        concepts = extract_key_concepts(content)
        notes.extend([f"• {concept}" for concept in concepts])
        
        # Find numerical data, formulas, dates
        important_data = extract_important_data(content)
        notes.extend([f"• {data}" for data in important_data])
        
        if not notes:
            # Fallback: Create notes from sentences
            sentences = [s.strip() for s in content.split('.') if len(s.strip()) > 20]
            notes = [f"• {sent}" for sent in sentences[:5]]
        
        return '\n'.join(notes[:8])  # Limit to 8 key points
        
    except Exception as e:
        print(f"Error generating notes: {e}")
        return generate_fallback_notes(content)

def extract_definitions(text: str) -> List[tuple]:
    """Extract definitions from text"""
    definitions = []
    
    # Pattern for "X is/are/means/refers to Y"
    definition_patterns = [
        r'([A-Z][a-zA-Z\s]+?)\s+(?:is|are|means?|refers?\s+to)\s+(.+?)(?:\.|;|,\s+and)',
        r'([A-Z][a-zA-Z\s]+?):\s*(.+?)(?:\.|;|\n)',
        r'(?:Define|Definition of)\s+([a-zA-Z\s]+?):\s*(.+?)(?:\.|;|\n)'
    ]
    
    for pattern in definition_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            term = match.group(1).strip()
            definition = match.group(2).strip()
            if len(term) < 50 and len(definition) < 200:  # Reasonable limits
                definitions.append((term, definition))
    
    return definitions[:3]  # Top 3 definitions

def extract_key_concepts(text: str) -> List[str]:
    """Extract key concepts and important information"""
    concepts = []
    
    # Look for important sentence patterns
    important_patterns = [
        r'(?:Important|Key|Main|Primary|Essential|Critical|Fundamental)\s+(.+?)(?:\.|;|\n)',
        r'(?:Remember|Note that|It is important to)\s+(.+?)(?:\.|;|\n)',
        r'(?:The main|Primary|Key)\s+(?:advantage|benefit|feature|characteristic|principle)\s+(.+?)(?:\.|;|\n)'
    ]
    
    for pattern in important_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            concept = match.group(1).strip()
            if len(concept) > 20 and len(concept) < 150:
                concepts.append(concept)
    
    # Also extract sentences with certain keywords
    keywords = ['principle', 'theory', 'method', 'approach', 'technique', 'concept', 'framework']
    sentences = text.split('.')
    
    for sentence in sentences:
        if any(keyword in sentence.lower() for keyword in keywords):
            clean_sentence = sentence.strip()
            if 20 < len(clean_sentence) < 150:
                concepts.append(clean_sentence)
    
    return list(set(concepts))[:5]  # Remove duplicates, top 5

def extract_important_data(text: str) -> List[str]:
    """Extract numerical data, formulas, dates, and other important data"""
    data_points = []
    
    # Numbers with units or percentages
    number_patterns = [
        r'\d+(?:\.\d+)?%',  # Percentages
        r'\d+(?:\.\d+)?\s*(?:kg|g|m|cm|mm|km|s|min|hr|°C|°F)',  # Numbers with units
        r'(?:19|20)\d{2}',  # Years
    ]
    
    for pattern in number_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            data_points.append(f"Important value: {match}")
    
    # Look for formulas (simple pattern)
    formula_pattern = r'[A-Za-z]\s*=\s*[A-Za-z0-9\+\-\*/\(\)\s]+'
    formulas = re.findall(formula_pattern, text)
    for formula in formulas:
        data_points.append(f"Formula: {formula}")
    
    return data_points[:3]  # Top 3 data points

def generate_smart_questions(content: str) -> str:
    """Generate intelligent practice questions from content"""
    try:
        questions = []
        
        # Extract topics for question generation
        topics = extract_topics_for_questions(content)
        
        question_templates = [
            "What are the key principles of {}?",
            "How does {} work in practice?",
            "What are the advantages and disadvantages of {}?",
            "Explain the relationship between {} and related concepts.",
            "Why is {} important in this field of study?",
            "What are the practical applications of {}?",
            "Compare and contrast different approaches to {}."
        ]
        
        for i, topic in enumerate(topics[:5]):
            if i < len(question_templates):
                question = question_templates[i].format(topic)
                questions.append(f"{i+1}. {question}")
        
        # Add some general questions
        if len(questions) < 4:
            general_questions = [
                "What are the main concepts discussed in this material?",
                "How do these concepts apply to real-world scenarios?",
                "What are the most important points to remember for an exam?",
                "Explain the underlying principles in your own words."
            ]
            
            for i, q in enumerate(general_questions):
                if len(questions) < 5:
                    questions.append(f"{len(questions)+1}. {q}")
        
        return '\n\n'.join(questions)
        
    except Exception as e:
        print(f"Error generating questions: {e}")
        return generate_fallback_questions(content)

def extract_topics_for_questions(text: str) -> List[str]:
    """Extract key topics from text for question generation"""
    topics = []
    
    # Look for noun phrases that could be topics
    # This is a simplified approach - in production, you'd use NLP libraries
    
    # Find capitalized terms (likely important concepts)
    capitalized_terms = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
    
    # Filter and clean
    for term in capitalized_terms:
        if 3 < len(term) < 30 and term not in ['The', 'This', 'That', 'These', 'Those']:
            topics.append(term.lower())
    
    # Remove duplicates and return top topics
    return list(set(topics))[:7]

def generate_fallback_notes(content: str) -> str:
    """Generate basic notes when smart extraction fails"""
    sentences = [s.strip() for s in content.split('.') if 20 < len(s.strip()) < 150]
    notes = [f"• {sent}" for sent in sentences[:5]]
    
    if not notes:
        notes = ["• Key concepts extracted from the uploaded document"]
    
    return '\n'.join(notes)

def generate_fallback_questions(content: str) -> str:
    """Generate basic questions when smart generation fails"""
    questions = [
        "1. What are the main topics covered in this material?",
        "2. How do the concepts relate to each other?",
        "3. What are the practical applications discussed?",
        "4. What should you focus on for exam preparation?",
        "5. Can you explain the key principles in your own words?"
    ]
    
    return '\n\n'.join(questions)

# Main interface functions
def generate_notes(content: str) -> str:
    """Generate study notes from content"""
    try:
        if not content or len(content.strip()) < 50:
            return "⚠️ Insufficient content for note generation"
        
        return generate_smart_notes(content)
        
    except Exception as e:
        print(f"Error in generate_notes: {e}")
        return f"Error generating notes: {str(e)}"

def generate_questions(content: str) -> str:
    """Generate practice questions from content"""
    try:
        if not content or len(content.strip()) < 50:
            return "⚠️ Insufficient content for question generation"
        
        return generate_smart_questions(content)
        
    except Exception as e:
        print(f"Error in generate_questions: {e}")
        return f"Error generating questions: {str(e)}"

# For future API integration
def call_claude_api(prompt: str, content: str, api_key: Optional[str] = None) -> str:
    """
    Call Claude API - placeholder for when you have API access
    For now, falls back to local processing
    """
    if api_key:
        # Implement actual API call here
        pass
    
    # Fallback to local processing
    if "notes" in prompt.lower():
        return generate_smart_notes(content)
    else:
        return generate_smart_questions(content)
