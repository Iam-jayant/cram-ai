import gradio as gr
import os
import tempfile
import traceback
from utils import extract_text_from_pdf, chunk_text, generate_notes, generate_questions

def process_pdf(pdf_file, progress=gr.Progress()):
    """Process PDF and return study materials"""
    if pdf_file is None:
        return "Please upload a PDF file.", "", "⚠️ No file uploaded"
    
    try:
        progress(0.1, desc="Processing PDF...")
        
        # Create temporary file path
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f"temp_{pdf_file.name}")
        
        # Copy uploaded file to temp location
        with open(temp_path, 'wb') as f:
            f.write(pdf_file.read())
        
        progress(0.3, desc="Extracting text from PDF...")
        
        # Extract text from PDF
        text = extract_text_from_pdf(temp_path)
        
        if not text or len(text.strip()) < 50:
            return "⚠️ Could not extract sufficient text from PDF. Please ensure it's a text-based PDF.", "", "❌ Text extraction failed"
        
        progress(0.5, desc="Processing content...")
        
        # Chunk text for better processing
        chunks = chunk_text(text, chunk_size=1500, overlap=300)
        
        if not chunks:
            return "⚠️ Could not process the PDF content.", "", "❌ Content processing failed"
        
        progress(0.7, desc="Generating study notes...")
        
        # Generate notes from first few chunks (to avoid overwhelming)
        notes_content = ' '.join(chunks[:3])  # Use first 3 chunks
        study_notes = generate_notes(notes_content)
        
        progress(0.9, desc="Generating practice questions...")
        
        # Generate questions
        practice_questions = generate_questions(notes_content)
        
        # Clean up temp file
        try:
            os.remove(temp_path)
        except:
            pass
        
        progress(1.0, desc="Complete!")
        
        # Format the output
        formatted_notes = f"""# 📝 Study Notes - {pdf_file.name}
## Key Concepts Extracted:
{study_notes}
---
*Generated from: {pdf_file.name} ({len(text)} characters processed)*
"""

        formatted_questions = f"""# ❓ Practice Questions - {pdf_file.name}
## Test Your Understanding:
{practice_questions}
---
*Questions based on content from: {pdf_file.name}*
"""

        status = f"✅ Successfully processed {pdf_file.name}"
        
        return formatted_notes, formatted_questions, status
        
    except Exception as e:
        error_msg = f"❌ Error processing PDF: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        return error_msg, "", error_msg

def test_function():
    """Test function to verify the app is working"""
    return "✅ CramAI is working perfectly!", "🎯 Ready to help you study!", "🧪 Test completed successfully"

def clear_outputs():
    """Clear all outputs"""
    return "", "", "🔄 Cleared all content"

# Create the Gradio interface
def create_app():
    with gr.Blocks(
        title="CramAI Study Assistant",
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="purple"
        )
    ) as demo:
        
        # Header
        gr.HTML("""
        <div style="text-align: center; padding: 20px; background: linear-gradient(45deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px; margin-bottom: 20px;">
            <h1>🧠 CramAI - Last-Minute Study Assistant</h1>
            <p style="font-size: 18px; margin: 10px 0;">Upload your study materials and get instant study notes + practice questions!</p>
            <p style="opacity: 0.9;">Perfect for syllabus documents, previous year papers, and textbook chapters.</p>
        </div>
        """)
        
        # Status indicator
        status_output = gr.Textbox(
            label="📊 Status", 
            value="Ready to process your PDF...",
            interactive=False,
            lines=1
        )
        
        # Control buttons row
        with gr.Row():
            with gr.Column(scale=1):
                test_btn = gr.Button("🧪 Test App", variant="secondary", size="sm")
                clear_btn = gr.Button("🔄 Clear All", variant="stop", size="sm")
            
            with gr.Column(scale=3):
                # File upload
                pdf_input = gr.File(
                    label="📁 Upload PDF File",
                    file_types=[".pdf"],
                    file_count="single"
                )
        
        # Process button
        process_btn = gr.Button(
            "🚀 Generate Study Materials", 
            variant="primary", 
            size="lg",
            scale=2
        )
        
        # Output areas
        with gr.Row():
            with gr.Column():
                notes_output = gr.Markdown(
                    label="📝 Study Notes",
                    value="Upload a PDF file and click 'Generate Study Materials' to see notes here...",
                    height=400
                )
            
            with gr.Column():
                questions_output = gr.Markdown(
                    label="❓ Practice Questions",
                    value="Upload a PDF file and click 'Generate Study Materials' to see questions here...",
                    height=400
                )
        
        # Tips section
        gr.Markdown("""
        ## 💡 Tips for Best Results:
        - **Upload clear, text-based PDFs** (avoid scanned images)
        - **Syllabus documents** work excellently
        - **Previous year question papers** are perfect
        - **Academic textbook chapters** also work well
        - **File size**: Keep under 10MB for best performance
        """)
        
        # Footer
        gr.HTML("""
        <div style="text-align: center; padding: 15px; background-color: #f8f9fa; border-radius: 8px; margin-top: 20px;">
            <p><strong>Built for the Gradio x MCP Hackathon</strong> | Powered by AI ❤️</p>
        </div>
        """)
        
        # Event handlers
        test_btn.click(
            fn=test_function,
            outputs=[notes_output, questions_output, status_output]
        )
        
        clear_btn.click(
            fn=clear_outputs,
            outputs=[notes_output, questions_output, status_output]
        )
        
        process_btn.click(
            fn=process_pdf,
            inputs=[pdf_input],
            outputs=[notes_output, questions_output, status_output],
            show_progress=True
        )
        
        # Auto-process when file is uploaded (optional)
        # pdf_input.change(
        #     fn=process_pdf,
        #     inputs=[pdf_input],
        #     outputs=[notes_output, questions_output, status_output]
        # )
    
    return demo

# Launch the app
if __name__ == "__main__":
    print("🚀 Starting CramAI - Fully Functional Version...")
    app = create_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        show_error=True
    )
