---
title: CramAI - Last-Minute Study Assistant
emoji: 🧠
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 5.33.0
app_file: app.py
pinned: false
---

# 🧠 CramAI - Last-Minute Study Assistant

**Built for the Gradio x MCP Hackathon**

CramAI is an AI-powered study assistant that helps students prepare for theory exams by automatically generating study notes and practice questions from uploaded PDF documents.

## 🚀 Features

- **PDF Upload**: Upload syllabus documents or previous year question papers
- **Automatic Text Extraction**: Clean text extraction using PyMuPDF
- **Smart Chunking**: Intelligently splits content into manageable sections
- **Study Notes Generation**: Creates bullet-point summaries focusing on high-yield information
- **Practice Questions**: Generates conceptual questions for exam preparation
- **Beautiful UI**: Clean, responsive Gradio interface

## 📁 Project Structure

```
cramai/
├── app.py                    # Main Gradio application
├── utils.py                  # Core processing functions
├── requirements.txt          # Python dependencies
├── README.md                # This file
└── prompts/                 # AI prompt templates
    ├── __init__.py
    ├── claude_prompt_notes.py
    └── claude_prompt_qna.py
```

## 🛠️ Installation & Setup

1. **Clone or download the project files**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Access the web interface:**
   - Local: http://localhost:7860
   - Public: Use the generated Gradio share link

## 📖 How to Use

1. **Upload PDF**: Click on the file upload area and select your PDF document
2. **Generate Materials**: Click the "🚀 Generate Study Materials" button
3. **Review Notes**: Study the generated bullet-point notes in the left panel
4. **Practice Questions**: Test yourself with the conceptual questions in the right panel

## 💡 Best Results Tips

- Upload clear, text-based PDFs (avoid scanned images)
- Syllabus documents work excellently
- Previous year question papers are perfect
- Academic textbook chapters also work well

## 🔧 Technical Details

### Core Components

- **Text Extraction**: Uses PyMuPDF (fitz) for reliable PDF text extraction
- **Content Processing**: Smart text chunking with overlap for context preservation
- **AI Integration**: Structured prompts for consistent note and question generation
- **UI/UX**: Modern Gradio interface with responsive design

### Processing Pipeline

1. PDF Upload → Text Extraction
2. Text Cleaning → Smart Chunking
3. Chunk Processing → Notes & Questions Generation
4. Markdown Formatting → Display

## 🚀 Deployment

### Hugging Face Spaces

1. Create a new Space on Hugging Face
2. Upload all project files
3. Set SDK to "gradio"
4. The app will automatically deploy

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run with auto-reload for development
python app.py
```

## 🎯 Future Enhancements

- [ ] Integration with actual Claude API
- [ ] Support for multiple file formats (DOCX, TXT)
- [ ] Flashcard generation
- [ ] Export to PDF functionality
- [ ] Progress tracking and study analytics
- [ ] Multiple language support

## 🤝 Contributing

This project was built for the Gradio x MCP Hackathon. Feel free to fork and enhance!

## 📄 License

MIT License - Feel free to use and modify for your projects.

## 🙏 Acknowledgments

- Built with [Gradio](https://gradio.app/) for the amazing UI framework
- Uses [PyMuPDF](https://pymupdf.readthedocs.io/) for PDF processing
- Created for the Gradio x MCP Hackathon

---

**Happy Studying! 📚✨**