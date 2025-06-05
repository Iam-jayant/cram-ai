import gradio as gr
import os
import tempfile
import traceback
import shutil
from utils import extract_text_from_pdf, chunk_text, generate_notes, generate_questions

def process_pdf(pdf_file, progress=gr.Progress()):
    """Process PDF and return study materials"""
    if pdf_file is None:
        return "Please upload a PDF file.", "", "⚠️ No file uploaded"
    
    try:
        progress(0.1, desc="Processing PDF...")
        
        # Get the file path directly from Gradio
        pdf_path = pdf_file.name if hasattr(pdf_file, 'name') else pdf_file
        
        progress(0.2, desc="Extracting text from PDF...")
        
        # Extract text directly from the uploaded file path
        text = extract_text_from_pdf(pdf_path)
        
        if not text or len(text.strip()) < 100:
            return "⚠️ Could not extract sufficient text from PDF. Please ensure it's a text-based PDF.", "", "❌ Text extraction failed"
        
        progress(0.4, desc="Processing and cleaning content...")
        
        # Use a larger portion of the text for better results
        max_chars = 8000  # Increased from 1500*3
        content_for_processing = text[:max_chars] if len(text) > max_chars else text
        
        progress(0.6, desc="Generating comprehensive study notes...")
        
        # Generate notes from the content
        study_notes = generate_notes(content_for_processing)
        
        progress(0.8, desc="Creating practice questions...")
        
        # Generate questions from the same content
        practice_questions = generate_questions(content_for_processing)
        
        progress(1.0, desc="Complete!")
        
        # Get filename for display
        filename = os.path.basename(pdf_path)
        if len(filename) > 50:  # Truncate very long filenames
            filename = filename[:47] + "..."
        
        # Format the output with better structure
        formatted_notes = f"""# 📝 Study Notes - {filename}

{study_notes}

---
*Generated from: {filename} | Content processed: {len(content_for_processing):,} characters*
"""

        formatted_questions = f"""# ❓ Practice Questions - {filename}

{practice_questions}

---
*Questions based on content from: {filename}*
"""

        status = f"✅ Successfully processed {filename} ({len(text):,} characters extracted)"
        
        return formatted_notes, formatted_questions, status
        
    except Exception as e:
        error_msg = f"❌ Error processing PDF: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        return error_msg, "", error_msg

def test_function():
    """Test function to verify the app is working"""
    sample_notes = """# 📝 Sample Study Notes

**📚 Main Topics:**
  1. Artificial Intelligence Applications
  2. Machine Learning in Industry
  3. Automation and Robotics

**🔑 Key Points:**
  • AI improves efficiency and reduces costs in manufacturing
  • Predictive maintenance prevents unexpected machine failures
  • Computer vision enables automated quality control
  • Machine learning optimizes supply chain management

**💡 Examples & Applications:**
  • Tesla uses AI-driven robots for car assembly
  • General Electric employs AI for jet engine maintenance
  • Siemens utilizes AI cameras for defect detection
"""
    
    sample_questions = """# ❓ Sample Practice Questions

1. What is the main purpose of AI in manufacturing industries?

2. How would you explain predictive maintenance in simple terms?

3. What are the practical applications of computer vision in quality control?

4. What are the advantages and disadvantages of AI-driven automation?

5. How does AI improve supply chain management processes?

6. Why is predictive maintenance important in industrial settings?

7. What makes AI an effective solution for manufacturing challenges?

8. How would you assess the impact of AI on workplace safety?
"""
    
    return sample_notes, sample_questions, "🧪 Test completed - CramAI is working perfectly!"

def clear_outputs():
    """Clear all outputs"""
    return "", "", "🔄 Cleared all content - Ready for new PDF"

# Create the Gradio interface
def create_app():
    with gr.Blocks(
        title="CramAI Study Assistant",
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="purple"
        ),
        css="""
        .gradio-container {
            max-width: 1200px !important;
        }
        .panel {
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
        }
        """
    ) as demo:
        
        # Header
        gr.HTML("""
        <div style="text-align: center; padding: 25px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 12px; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
            <h1 style="margin: 0 0 10px 0; font-size: 2.5em;">🧠 CramAI</h1>
            <h2 style="margin: 0 0 15px 0; font-weight: 300; font-size: 1.3em;">Last-Minute Study Assistant</h2>
            <p style="font-size: 18px; margin: 10px 0; opacity: 0.95;">Transform your study materials into organized notes and practice questions instantly!</p>
            <p style="opacity: 0.8; font-size: 16px;">Perfect for syllabus documents, academic papers, and textbook chapters.</p>
        </div>
        """)
        
        # Status indicator with better styling
        status_output = gr.Textbox(
            label="📊 Processing Status", 
            value="🚀 Ready to process your PDF - Upload a file to get started!",
            interactive=False,
            lines=1,
            show_label=True
        )
        
        # Control section
        with gr.Row():
            with gr.Column(scale=1):
                with gr.Row():
                    test_btn = gr.Button("🧪 Test App", variant="secondary", size="sm")
                    clear_btn = gr.Button("🔄 Clear All", variant="stop", size="sm")
            
            with gr.Column(scale=2):
                # File upload with better description
                pdf_input = gr.File(
                    label="📁 Upload Your Study Material (PDF)",
                    file_types=[".pdf"],
                    file_count="single",
                    height=120
                )
        
        # Process button with better styling
        process_btn = gr.Button(
            "🚀 Generate Study Materials", 
            variant="primary", 
            size="lg",
            scale=2
        )
        
        # Output areas with improved layout
        gr.HTML("<div style='margin: 20px 0;'><h2 style='text-align: center; color: #444;'>📚 Generated Study Materials</h2></div>")
        
        with gr.Row(equal_height=True):
            with gr.Column():
                notes_output = gr.Markdown(
                    label="📝 Study Notes",
                    value="""### Ready to Generate Notes! 📝

Upload a PDF file and click **'Generate Study Materials'** to see comprehensive study notes here.

**What you'll get:**
- 📚 Main topics and sections
- 🔑 Key points and concepts  
- 💡 Examples and applications
- ✨ Organized, exam-focused content

*Perfect for quick revision and understanding core concepts.*""",
                    height=500,
                    show_label=True
                )
            
            with gr.Column():
                questions_output = gr.Markdown(
                    label="❓ Practice Questions",
                    value="""### Ready to Generate Questions! ❓

Upload a PDF file and click **'Generate Study Materials'** to see practice questions here.

**What you'll get:**
- 🎯 Conceptual understanding questions
- 🧠 Application-based problems
- 📊 Analysis and evaluation questions
- 🎓 Exam-style practice problems

*Test your knowledge and identify areas for improvement.*""",
                    height=500,
                    show_label=True
                )
        
        # Enhanced tips section
        with gr.Accordion("💡 Tips for Best Results", open=False):
            gr.Markdown("""
            ### 📋 How to Get the Best Results:
            
            **✅ Ideal File Types:**
            - **Syllabus documents** - Perfect for comprehensive topic coverage
            - **Previous year question papers** - Excellent for question generation
            - **Academic textbook chapters** - Great for detailed concept extraction
            - **Lecture notes and handouts** - Good for key point identification
            
            **⚠️ File Requirements:**
            - **Text-based PDFs only** (avoid scanned images)
            - **File size**: Keep under 10MB for optimal performance
            - **Content length**: 5-50 pages work best
            - **Language**: English content provides best results
            
            **🎯 Pro Tips:**
            - Upload one chapter/topic at a time for focused results
            - Ensure PDFs have selectable text (not just images)
            - Academic and technical content works better than general text
            - Use the generated questions to test your understanding
            """)
        
        # Usage instructions
        with gr.Accordion("📖 How to Use CramAI", open=False):
            gr.Markdown("""
            ### 🚀 Simple 3-Step Process:
            
            **Step 1: Upload** 📁
            - Click on the upload area above
            - Select your PDF study material
            - Wait for upload confirmation
            
            **Step 2: Generate** ⚡
            - Click the "Generate Study Materials" button
            - Watch the progress as CramAI processes your content
            - This usually takes 10-30 seconds
            
            **Step 3: Study** 📖
            - Review the organized study notes on the left
            - Test yourself with practice questions on the right
            - Use both together for comprehensive exam preparation
            
            **🔄 Need to Start Over?**
            - Use the "Clear All" button to reset
            - Upload a new PDF anytime
            - Generate materials for multiple topics
            """)
        
        # Footer
        gr.HTML("""
        <div style="text-align: center; padding: 20px; background-color: #f8f9fa; border-radius: 10px; margin-top: 30px; border: 1px solid #e9ecef;">
            <p style="margin: 5px 0; color: #666;"><strong>🏆 Built for the Gradio x MCP Hackathon</strong></p>
            <p style="margin: 5px 0; color: #888; font-size: 14px;">Powered by AI • Made with ❤️ for Students</p>
            <p style="margin: 5px 0; color: #999; font-size: 12px;">Help students succeed in their last-minute exam preparation!</p>
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
        
        # Optional: Auto-process when file is uploaded
        # pdf_input.change(
        #     fn=process_pdf,
        #     inputs=[pdf_input],
        #     outputs=[notes_output, questions_output, status_output]
        # )
    
    return demo

# Launch the app
if __name__ == "__main__":
    print("🚀 Starting CramAI - Enhanced Version...")
    print("📚 Ready to help students with their exam preparation!")
    app = create_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        show_error=True
    )
