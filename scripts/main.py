#!/usr/bin/env python3
"""
Main script to run the NOMAD RAGalicious application.
This script handles the initialization and launch of the Gradio interface
that uses functions from server.py.
"""

import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are available."""
    missing_deps = []
    
    try:
        import gradio
    except ImportError:
        missing_deps.append("gradio")
    
    try:
        import chromadb
    except ImportError:
        missing_deps.append("chromadb")
    
    try:
        import openai
    except ImportError:
        missing_deps.append("openai")
    
    try:
        import requests
    except ImportError:
        missing_deps.append("requests")
    
    if missing_deps:
        print("❌ Missing dependencies:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\n📦 Install missing dependencies with:")
        print(f"   pip install {' '.join(missing_deps)}")
        return False
    
    return True

def check_files():
    """Check if required files exist."""
    required_files = ["server.py", "gradio_app.py"]
    missing_files = []
    
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    return True

def check_data_and_services():
    """Check if data files and external services are accessible."""
    # Import here to avoid circular imports
    from server import JSONL_PATH
    
    issues = []
    
    # Check data file
    if not Path(JSONL_PATH).exists():
        issues.append(f"Data file not found: {JSONL_PATH}")
    
    # Check embedding service
    try:
        import requests
        response = requests.get("http://172.28.105.142:11434", timeout=5)
        print("✅ Embedding service is accessible")
    except Exception as e:
        issues.append(f"Embedding service not accessible: {e}")
    
    if issues:
        print("⚠️  Warning - Some components may not work:")
        for issue in issues:
            print(f"   - {issue}")
        print("\n🔄 The application will still start, but functionality may be limited.")
        
        response = input("\nContinue anyway? (y/N): ")
        if response.lower() != 'y':
            return False
    
    return True

def main():
    """Main function to run the application."""
    print("🚀 NOMAD RAGalicious Startup")
    print("=" * 50)
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    print("✅ All dependencies found")
    
    # Check files
    print("📁 Checking required files...")
    if not check_files():
        sys.exit(1)
    print("✅ All required files found")
    
    # Check data and services
    print("🌐 Checking data and external services...")
    if not check_data_and_services():
        sys.exit(1)
    
    print("\n🎨 Starting Gradio interface...")
    print("📚 The interface will use functions from server.py")
    print("💡 Access the web interface at: http://localhost:7860")
    print("👋 Press Ctrl+C to stop the application")
    print("=" * 50)
    
    try:
        # Import and run the Gradio app
        from gradio_app import create_gradio_app
        
        app = create_gradio_app()
        app.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            show_error=True,
            quiet=False
        )
        
    except KeyboardInterrupt:
        print("\n\n🛑 Application stopped by user")
    except Exception as e:
        print(f"\n❌ Error running application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()