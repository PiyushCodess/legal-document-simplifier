# Legal Document Simplifier(LawSimplify)

AI-powered web application that converts complex legal documents into simple, easy-to-understand language.

## Features

- 📄 Upload PDF, DOCX, or TXT files
- 🤖 AI-powered analysis using Llama 3.3
- ⚠️ Automatic risk detection with severity ratings
- 🔍 Compare multiple documents side-by-side
- 💬 Interactive chat to ask questions
- 📥 Export analysis as PDF

## Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/PiyushCodess/legal-document-simplifier.git
cd legal-document-simplifier
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up API key**
- Get free API key from https://console.groq.com
- Create `backend/.env` file:
```
GROQ_API_KEY=your_api_key_here
```

4. **Run the application**
```bash
python run.py
```

5. **Open browser**
```
http://localhost:5000
```

## Tech Stack

- **Backend:** Python, Flask
- **AI:** Groq API (Llama 3.3)
- **Frontend:** JavaScript, HTML, CSS
- **Libraries:** PyPDF2, python-docx, fpdf

## How to Use

1. Upload a legal document
2. Click "Analyze Document" for summary
3. Click "Find Concerns" to identify risks
4. Ask questions in the chat
5. Save results as PDF

## Deployment

LIVE :  (https://lawsimplify-bs3p.onrender.com)

## License

MIT License - See LICENSE file

## Author

Piyush Patrikar - [GitHub](https://github.com/PiyushCodess)
