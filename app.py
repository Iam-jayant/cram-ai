import gradio as gr
import os

def process_pdf(pdf_file):
    """Process PDF and return study materials"""
    if pdf_file is None:
        return "Please upload a PDF file.", ""
    
    try:
        # For demo purposes, return sample content
        # In production, you'd process the actual PDF here
        
        sample_notes = """# 📝 Study Notes Generated

## Key Concepts:
• **Important Topic 1**: Core principles and fundamental concepts
• **Important Topic 2**: Practical applications and real-world examples  
• **Important Topic 3**: Critical formulas and methodologies
• **Important Topic 4**: Common pitfalls and best practices
• **Important Topic 5**: Integration with other concepts

## Summary:
This section covers essential material for your exam preparation. Focus on understanding the underlying principles rather than just memorization."""

        sample_questions = """# ❓ Practice Questions

## Conceptual Questions:
1. **What are the fundamental principles discussed in this material?**
   - Explain the core concepts and their significance

2. **How do these concepts apply to real-world scenarios?**
   - Provide specific examples and use cases

3. **What are the key relationships between different topics?**
   - Analyze the connections and dependencies

4. **Why are these concepts important for your field of study?**
   - Discuss the practical relevance and applications

5. **What are common misconceptions about these topics?**
   - Identify potential areas of confusion and clarify them"""

        return sample_notes, sample_questions
        
    except Exception as e:
        return f"Error processing file: {str(e)}", ""

def test_function():
    """Test function to verify the app is working"""
    return "✅ CramAI is working perfectly!", "🎯 Ready to help you study!"

# Create the Gradio interface
def create_app():
    with gr.Blocks(title="CramAI Study Assistant") as demo:
        
        # Header
        gr.Markdown("""
        # 🧠 CramAI - Last-Minute Study Assistant
        
        **Upload your study materials and get instant study notes + practice questions!**
        
        Perfect for syllabus documents, previous year papers, and textbook chapters.
        """)
        
        # Test button
        test_btn = gr.Button("🧪 Test App", variant="secondary")
        
        # File upload
        with gr.Row():
            pdf_input = gr.File(
                label="📁 Upload PDF File",
                file_types=[".pdf"]
            )
        
        # Process button
        process_btn = gr.Button("🚀 Generate Study Materials", variant="primary", size="lg")
        
        # Output areas
        with gr.Row():
            with gr.Column():
                notes_output = gr.Markdown(
                    label="📝 Study Notes",
                    value="Upload a PDF file to generate study notes..."
                )
            
            with gr.Column():
                questions_output = gr.Markdown(
                    label="❓ Practice Questions",
                    value="Upload a PDF file to generate practice questions..."
                )
        
        # Footer
        gr.Markdown("""
        ---
        **Built for the Gradio x MCP Hackathon** | Powered by AI ❤️
        """)
        
        # Event handlers
        test_btn.click(
            fn=test_function,
            outputs=[notes_output, questions_output]
        )
        
        process_btn.click(
            fn=process_pdf,
            inputs=[pdf_input],
            outputs=[notes_output, questions_output]
        )
    
    return demo

# Launch the app
if __name__ == "__main__":
    app = create_app()
    app.launch()