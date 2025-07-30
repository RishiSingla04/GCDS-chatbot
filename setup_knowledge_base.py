#!/usr/bin/env python3
"""
Setup script to clone GCDS components repository and build knowledge base
"""
import os
import json
import subprocess
import sys
from pathlib import Path

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def clone_with_git_command(repo_url, target_path):
    """Clone repository using git command directly"""
    try:
        subprocess.check_call(["git", "clone", repo_url, target_path])
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def clone_repository(repo_url, target_path):
    """Clone repository with fallback methods"""
    # Method 1: Try GitPython
    try:
        import git
        git.Repo.clone_from(repo_url, target_path)
        return True
    except ImportError:
        print("GitPython not found, trying to install...")
        if install_package("GitPython"):
            try:
                import git
                git.Repo.clone_from(repo_url, target_path)
                return True
            except Exception as e:
                print(f"GitPython installation succeeded but clone failed: {e}")
        else:
            print("Failed to install GitPython")
    except Exception as e:
        print(f"GitPython clone failed: {e}")
    
    # Method 2: Try direct git command
    print("Trying direct git command...")
    if clone_with_git_command(repo_url, target_path):
        return True
    
    # Method 3: Manual instructions
    print(f"""
❌ Automatic cloning failed. Please clone manually:

1. Open terminal/command prompt
2. Navigate to the {os.path.dirname(target_path)} directory
3. Run: git clone {repo_url}

Or download the repository as a ZIP file from:
https://github.com/cds-snc/gcds-components/archive/refs/heads/main.zip
""")
    return False

def main():
    """Main setup function"""
    print("🚀 Setting up GCDS Chatbot Knowledge Base...")
    
    # Create data directory
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    print(f"✅ Created {data_dir} directory")
    
    # Clone GCDS components repository
    gcds_repo_path = data_dir / "gcds-components"
    
    if not gcds_repo_path.exists():
        print("📥 Cloning GCDS components repository...")
        repo_url = "https://github.com/cds-snc/gcds-components.git"
        
        if not clone_repository(repo_url, str(gcds_repo_path)):
            print("❌ Failed to clone repository automatically")
            return False
        
        print("✅ Successfully cloned GCDS components repository")
    else:
        print("✅ GCDS components repository already exists")
    
    # Check if knowledge_processor module exists
    try:
        from knowledge_processor import GCDSKnowledgeProcessor
    except ImportError:
        print("❌ knowledge_processor module not found!")
        print("Please ensure knowledge_processor.py exists in the same directory")
        return False
    
    # Process knowledge base
    print("🔍 Processing GCDS components...")
    try:
        processor = GCDSKnowledgeProcessor(str(gcds_repo_path))
        knowledge_base = processor.build_knowledge_base()
    except Exception as e:
        print(f"❌ Error processing knowledge base: {e}")
        return False
    
    # Save knowledge base
    knowledge_base_path = data_dir / "knowledge_base.json"
    try:
        with open(knowledge_base_path, 'w', encoding='utf-8') as f:
            json.dump(knowledge_base, f, indent=2, ensure_ascii=False)
        print(f"✅ Knowledge base saved to {knowledge_base_path}")
        print(f"📊 Processed {len(knowledge_base.get('components', []))} components")
    except Exception as e:
        print(f"❌ Error saving knowledge base: {e}")
        return False
    
    print("\n🎉 Setup complete! You can now run the chatbot with: python chatbot_gui.py")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)