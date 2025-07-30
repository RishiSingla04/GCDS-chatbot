#!/usr/bin/env python3
"""
Simple launcher script for the GCDS Chatbot
"""
import sys
import subprocess
import os

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    
    # Check if virtual environment exists
    if not os.path.exists("gcds-chatbot-env"):
        print("❌ Virtual environment not found")
        print("Run setup first: python -m venv gcds-chatbot-env")
        return False
    
    # Check if knowledge base exists
    if not os.path.exists("data/knowledge_base.json"):
        print("❌ Knowledge base not found")
        print("Run setup first: python setup_knowledge_base.py")
        return False
    
    print("✅ All requirements met")
    return True

def main():
    """Main launcher function"""
    print("🍁 GCDS Chatbot Launcher")
    print("=" * 30)
    
    if not check_requirements():
        print("\n❌ Please complete setup first")
        return
    
    print("🚀 Starting GCDS Chatbot...")
    try:
        from chatbot_gui import main as gui_main
        gui_main()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're in the virtual environment")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()