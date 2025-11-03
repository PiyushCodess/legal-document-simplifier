import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from backend.api import app

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Starting Legal Document Simplifier")
    print("=" * 60)
    print("\n📍 Server running at: http://localhost:5000")
    print("📝 Press CTRL+C to stop the server\n")
    
    if not os.environ.get('GROQ_API_KEY'):
        print("⚠️  WARNING: GROQ_API_KEY not set!")
        print("Get your free API key at: https://console.groq.com")
        print("Set it with: export GROQ_API_KEY='your-key-here'")
        print()
    
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)