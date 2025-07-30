#!/usr/bin/env python3
"""
Setup script to build the GCDS knowledge base
"""
import os
import json
import sys
from pathlib import Path
from knowledge_processor import GCDSKnowledgeProcessor

def setup_directories():
    """Create necessary directories"""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    print(f"✅ Created data directory: {data_dir}")

def find_gcds_repo():
    """Try to find GCDS components repository"""
    possible_paths = [
        Path("data/gcds-components"),
        Path("../gcds-components"),
        Path("../../gcds-components"),
        Path.home() / "gcds-components",
        Path("C:/gcds-components"),  # Windows
        Path("/opt/gcds-components")  # Linux
    ]
    
    for path in possible_paths:
        if path.exists():
            print(f"📁 Found GCDS repository at: {path}")
            return path
    
    return None

def download_gcds_repo():
    """Download GCDS components repository"""
    data_dir = Path("data")
    repo_path = data_dir / "gcds-components"
    
    if repo_path.exists():
        print(f"📁 Repository already exists at: {repo_path}")
        return repo_path
    
    try:
        import git
        print("📥 Cloning GCDS components repository...")
        git.Repo.clone_from(
            "https://github.com/cds-snc/gcds-components.git",
            repo_path
        )
        print(f"✅ Successfully cloned repository to: {repo_path}")
        return repo_path
    except ImportError:
        print("⚠️  GitPython not available for cloning")
        return None
    except Exception as e:
        print(f"❌ Error cloning repository: {e}")
        return None

def build_knowledge_base(repo_path=None):
    """Build the knowledge base"""
    if repo_path:
        print(f"🔍 Processing repository: {repo_path}")
        processor = GCDSKnowledgeProcessor(repo_path)
    else:
        print("⚠️  No repository found, creating with defaults")
        # Create a temporary directory for the processor
        import tempfile
        temp_dir = tempfile.mkdtemp()
        processor = GCDSKnowledgeProcessor(temp_dir)
    
    # Build knowledge base
    knowledge_base = processor.build_knowledge_base()
    
    # Save to file
    output_path = Path("data/knowledge_base.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(knowledge_base, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Knowledge base saved to: {output_path}")
    print(f"📊 Total components: {len(knowledge_base.get('components', []))}")
    
    return output_path

def test_ollama_model():
    """Test if gemma3n:2b model is available"""
    try:
        import requests
        
        # Check Ollama connection
        response = requests.get("http://localhost:11434/api/version", timeout=5)
        if response.status_code != 200:
            print("❌ Ollama is not running. Please start it with: ollama serve")
            return False
        
        print("✅ Ollama is running")
        
        # Check for gemma3n:2b model
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        if response.status_code == 200:
            models = response.json()
            available_models = [model['name'] for model in models.get('models', [])]
            
            if 'gemma3n:2b' in available_models:
                print("✅ gemma3n:2b model is available")
                return True
            else:
                print(f"⚠️  gemma3n:2b not found. Available models: {available_models}")
                print("📥 To install: ollama pull gemma3n:2b")
                return False
        else:
            print("⚠️  Could not check available models")
            return False
            
    except Exception as e:
        print(f"❌ Error checking Ollama: {e}")
        return False

def main():
    """Main setup function"""
    print("🍁 GCDS Chatbot Knowledge Base Setup")
    print("=" * 40)
    
    # Create directories
    setup_directories()
    
    # Find or download GCDS repository
    repo_path = find_gcds_repo()
    if not repo_path:
        print("📥 Attempting to download GCDS repository...")
        repo_path = download_gcds_repo()
    
    # Build knowledge base
    try:
        kb_path = build_knowledge_base(repo_path)
        print(f"✅ Knowledge base created: {kb_path}")
    except Exception as e:
        print(f"❌ Error building knowledge base: {e}")
        return False
    
    # Test Ollama and model
    print("\n🔍 Checking Ollama setup...")
    if test_ollama_model():
        print("✅ Ollama setup is ready")
    else:
        print("⚠️  Please set up Ollama and gemma3n:2b model")
        print("   1. Install Ollama: https://ollama.com/download")
        print("   2. Start Ollama: ollama serve")
        print("   3. Pull model: ollama pull gemma3n:2b")
    
    print("\n🎉 Setup complete!")
    print("Run the chatbot with: python chatbot_gui.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)