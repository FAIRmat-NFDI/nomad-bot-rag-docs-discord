#!/usr/bin/env python3
"""
NOMAD RAGBot Web Interface Launcher

This script starts the beautiful web interface for the NOMAD RAGBot chatbot.
The web interface provides a modern, responsive chat interface with blue theming
and connects to the existing RAG backend.

Usage:
    python run_web_interface.py

The web interface will be available at:
- Main interface: http://localhost:8001
- API documentation: http://localhost:8001/docs
"""

import os
import sys
import uvicorn

# Add the scripts directory to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
scripts_dir = os.path.join(script_dir, "scripts")
sys.path.insert(0, scripts_dir)

def main():
    """Launch the NOMAD RAGBot web interface."""
    print("🤖 NOMAD RAGBot Web Interface")
    print("=" * 50)
    print("🚀 Starting web server...")
    print("📖 Web interface: http://localhost:8001")
    print("🔗 API docs: http://localhost:8001/docs")
    print("💡 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Import the FastAPI app from the server module
        from server import app
        
        # Run the server
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8001,
            log_level="info",
            access_log=True
        )
    except ImportError as e:
        print(f"❌ Error importing server module: {e}")
        print("Make sure you're running this from the project root directory.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down NOMAD RAGBot web interface...")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
