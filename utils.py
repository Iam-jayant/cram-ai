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
    
    # Fix common PDF extraction issues
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # Remove non-ASCII characters
    text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
    
    # Remove page numbers and headers/footers
    text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
    text = re.sub(r'\n\s*Page\s+\d+.*?\n', '\n', text, flags=re.IGNORECASE)
    
    # Split into lines and clean
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        # Keep substantial lines
        if len(line) > 10:
            cleaned_lines.append(line)
    
    # Rejoin and clean up spacing
    cleaned_text = ' '.join(cleaned_lines)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    
    return cleaned_text.strip()

def chunk_text(text: str, chunk_size: int = 2000, overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks for better processing"""
    if not text:
        return []
    
    words = text.split()
    if len(words) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk_words = words[start:end]
        chunk_text = ' '.join(chunk_words)
        
        if chunk_text.strip():
            chunks.append(chunk_text)
        
        if end >= len(words):
            break
            
        start += chunk_size - overlap
    
    return chunks

def extract_main_topics(text: str) -> List[str]:
    """Extract main topics and sections from the text"""
    topics = []
    
    # Look for numbered sections and headers
    section_patterns = [
        r'(\d+\.?\s*[A-Z][^.!?]*?)(?=\s|\n|$)',  # Numbered sections
        r'([A-Z][A-Z\s]{10,50}?)(?=\s*\n|\s*[a-z])',  # ALL CAPS headers
        r'((?:Introduction|Overview|Applications?|Benefits?|Challenges?|Future|Conclusion)[^.!?]*?)(?=\s|\n|$)',  # Common section types
    ]
    
    for pattern in section_patterns:
        matches = re.findall(pattern, text, re.MULTILINE)
        for match in matches:
            topic = match.strip()
            if 10 < len(topic) < 100:
                topics.append(topic)
    
    return list(set(topics))[:8]  # Remove duplicates, top 8

def extract_key_points(text: str) -> List[str]:
    """Extract key points and important information"""
    key_points = []
    
    # Look for bullet points and important statements
    bullet_patterns = [
        r'[•▪▫◦]\s*([^.!?\n]{20,200})',  # Bullet points
        r'✅\s*([^.!?\n]{20,200})',  # Checkmark bullets
        r'🔹\s*([^.!?\n]{20,200})',  # Diamond bullets
        r'(?:Key|Important|Main|Primary|Essential|Critical):\s*([^.!?\n]{20,200})',  # Key statements
    ]
    
    for pattern in bullet_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            point = match.strip()
            if point and len(point) > 15:
                key_points.append(point)
    
    # Also extract sentences with important keywords
    important_keywords = ['improve', 'enhance', 'reduce', 'increase', 'optimize', 'enable', 'provide', 'ensure']
    sentences = re.split(r'[.!?]+', text)
    
    for sentence in sentences:
        sentence = sentence.strip()
        if any(keyword in sentence.lower() for keyword in important_keywords):
            if 20 < len(sentence) < 200:
                key_points.append(sentence)
    
    return list(set(key_points))[:10]  # Remove duplicates, top 10

def extract_examples_and_applications(text: str) -> List[str]:
    """Extract examples and real-world applications"""
    examples = []
    
    # Look for example patterns
    example_patterns = [
        r'(?:Example|For example|Instance|Case study):\s*([^.!?\n]{20,150})',
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+uses?\s+([^.!?\n]{20,150})',  # Company uses X
        r'(?:Companies? like|Such as|Including)\s+([^.!?\n]{20,150})',
    ]
    
    for pattern in example_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                example = ' '.join(match)
            else:
                example = match
            
            example = example.strip()
            if len(example) > 20:
                examples.append(example)
    
    return list(set(examples))[:5]  # Top 5 examples

def generate_structured_notes(content: str) -> str:
    """Generate well-structured study notes"""
    try:
        # Extract different types of information
        topics = extract_main_topics(content)
        key_points = extract_key_points(content)
        examples = extract_examples_and_applications(content)
        
        notes = []
        
        # Add main topics
        if topics:
            notes.append("**📚 Main Topics:**")
            for i, topic in enumerate(topics[:4], 1):
                notes.append(f"  {i}. {topic}")
            notes.append("")
        
        # Add key points
        if key_points:
            notes.append("**🔑 Key Points:**")
            for point in key_points[:6]:
                # Clean up the point
                point = re.sub(r'^[•▪▫◦🔹✅]\s*', '', point)
                point = point.strip()
                if point:
                    notes.append(f"  • {point}")
            notes.append("")
        
        # Add examples
        if examples:
            notes.append("**💡 Examples & Applications:**")
            for example in examples[:3]:
                notes.append(f"  • {example}")
        
        # If no structured content found, extract from sentences
        if len(notes) < 3:
            notes = generate_fallback_notes(content).split('\n')
        
        return '\n'.join(notes)
        
    except Exception as e:
        print(f"Error generating structured notes: {e}")
        return generate_fallback_notes(content)

def generate_comprehensive_questions(content: str) -> str:
    """Generate comprehensive practice questions"""
    try:
        topics = extract_main_topics(content)
        key_points = extract_key_points(content)
        
        questions = []
        
        # Question templates based on Bloom's taxonomy
        question_templates = [
            ("Understanding", [
                "What is the main purpose of {}?",
                "How would you explain {} in simple terms?",
                "What are the key characteristics of {}?"
            ]),
            ("Application", [
                "How is {} used in real-world scenarios?",
                "What are the practical applications of {}?",
                "When would you implement {}?"
            ]),
            ("Analysis", [
                "What are the advantages and disadvantages of {}?",
                "How does {} compare to alternative approaches?",
                "What factors influence the effectiveness of {}?"
            ]),
            ("Evaluation", [
                "Why is {} important in this field?",
                "What makes {} an effective solution?",
                "How would you assess the impact of {}?"
            ])
        ]
        
        # Generate questions from topics
        question_count = 1
        for category, templates in question_templates:
            if question_count > 8:  # Limit to 8 questions
                break
                
            for template in templates[:2]:  # Max 2 questions per category
                if topics and question_count <= 8:
                    # Use a relevant topic
                    topic_index = (question_count - 1) % len(topics)
                    topic = topics[topic_index].lower()
                    # Clean up topic
                    topic = re.sub(r'^\d+\.?\s*', '', topic)  # Remove numbering
                    topic = topic.strip()
                    
                    if topic:
                        question = template.format(topic)
                        questions.append(f"{question_count}. {question}")
                        question_count += 1
        
        # Add some general questions if we don't have enough
        if len(questions) < 5:
            general_questions = [
                "What are the main concepts covered in this material?",
                "How do these technologies improve current processes?",
                "What challenges need to be addressed for successful implementation?",
                "How might these concepts evolve in the future?",
                "What skills would be needed to work with these technologies?"
            ]
            
            for q in general_questions:
                if len(questions) < 8:
                    questions.append(f"{len(questions) + 1}. {q}")
        
        return '\n\n'.join(questions)
        
    except Exception as e:
        print(f"Error generating questions: {e}")
        return generate_fallback_questions(content)

def generate_fallback_notes(content: str) -> str:
    """Generate basic notes when structured extraction fails"""
    # Split into sentences and find the most informative ones
    sentences = re.split(r'[.!?]+', content)
    good_sentences = []
    
    # Score sentences based on informativeness
    for sentence in sentences:
        sentence = sentence.strip()
        if 30 < len(sentence) < 150:  # Good length
            score = 0
            # Add points for important keywords
            important_words = ['AI', 'improve', 'enhance', 'system', 'process', 'technology', 'method', 'application']
            for word in important_words:
                if word.lower() in sentence.lower():
                    score += 1
            
            good_sentences.append((score, sentence))
    
    # Sort by score and take top sentences
    good_sentences.sort(key=lambda x: x[0], reverse=True)
    notes = [f"• {sentence}" for score, sentence in good_sentences[:6]]
    
    if not notes:
        notes = ["• Key information extracted from the document"]
    
    return '\n'.join(notes)

def generate_fallback_questions(content: str) -> str:
    """Generate basic questions when comprehensive generation fails"""
    questions = [
        "1. What are the main topics discussed in this material?",
        "2. How do the technologies mentioned improve existing processes?",
        "3. What are the practical applications of these concepts?",
        "4. What benefits and challenges are associated with implementation?",
        "5. How might these technologies impact the future of the field?"
    ]
    
    return '\n\n'.join(questions)

# Main interface functions
def generate_notes(content: str) -> str:
    """Generate study notes from content"""
    try:
        if not content or len(content.strip()) < 100:
            return "⚠️ Insufficient content for note generation"
        
        return generate_structured_notes(content)
        
    except Exception as e:
        print(f"Error in generate_notes: {e}")
        traceback.print_exc()
        return f"Error generating notes: {str(e)}"

def generate_questions(content: str) -> str:
    """Generate practice questions from content"""
    try:
        if not content or len(content.strip()) < 100:
            return "⚠️ Insufficient content for question generation"
        
        return generate_comprehensive_questions(content)
        
    except Exception as e:
        print(f"Error in generate_questions: {e}")
        traceback.print_exc()
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
        return generate_structured_notes(content)
    else:
        return generate_comprehensive_questions(content)
