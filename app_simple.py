import gradio as gr
import os
import traceback

def simple_test():
    """Simple test function"""
    return "✅ CramAI is working! Upload functionality coming up...", "🎯 Ready to generate practice questions!"

def process_pdf_simple(pdf_file):
    """Simplified PDF processing for testing"""
    try:
        if pdf_file is None:
            return "Please upload a PDF file.", ""
        
        # For now, just return a success message
        return f"✅ PDF uploaded successfully: {pdf_file.name}\n\n📝 **Sample Study Notes:**\n• Key concept 1: Important information\n• Key concept 2: Critical details\n• Key concept 3: Essential knowledge", "❓ **Sample Practice Questions:**\n1. What are the main concepts covered?\n2. How do these relate to practical applications?\n3. Why are these topics important for exams?"
        
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        return error_msg, ""

# Create simple interface
with gr.Blocks(
    title="CramAI - Study Assistant",
    theme=gr.themes.Soft()
) as app:
    
    gr.HTML("""
    <div style="text-align: center; margin: 20px;">
        <h1>🧠 CramAI - Last-Minute Study Assistant</h1>
        <p>Upload your study materials and get instant notes + questions!</p>
    </div>
    """)
    
    with gr.Row():
        with gr.Column():
            pdf_input = gr.File(
                label="📁 Upload PDF File",
                file_types=[".pdf"]
            )
            
            test_btn = gr.Button("🧪 Test App", variant="secondary")
            process_btn = gr.Button("🚀 Process PDF", variant="primary")
    
    with gr.Row():
        with gr.Column():
            notes_output = gr.Markdown(
                label="📝 Study Notes",
                value="Upload a PDF to see study notes here..."
            )
        
        with gr.Column():
            questions_output = gr.Markdown(
                label="❓ Practice Questions", 
                value="Upload a PDF to see practice questions here..."
            )
    
    # Event handlers
    test_btn.click(
        fn=simple_test,
        outputs=[notes_output, questions_output]
    )
    
    process_btn.click(
        fn=process_pdf_simple,
        inputs=[pdf_input],
        outputs=[notes_output, questions_output]
    )

if __name__ == "__main__":
    print("🚀 Starting Simple CramAI...")
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        show_error=True
    )