#!/usr/bin/env python3
"""
Processes GCDS components repository to build knowledge base
"""
import os
import json
import re
from pathlib import Path

class GCDSKnowledgeProcessor:
    def __init__(self, repo_path):
        self.repo_path = Path(repo_path)
        self.components = []
        
        if not self.repo_path.exists():
            raise FileNotFoundError(f"Repository path does not exist: {repo_path}")
            
        print(f"✅ Initialized processor for: {self.repo_path}")
        
    def build_knowledge_base(self):
        """Build complete knowledge base from GCDS repository"""
        print("🔍 Building knowledge base...")
        
        # Find all component directories - try multiple possible structures
        possible_paths = [
            self.repo_path / "packages" / "web" / "src" / "components",
            self.repo_path / "packages" / "web",
            self.repo_path / "src" / "components",
            self.repo_path / "components",
            self.repo_path
        ]
        
        components_dir = None
        for path in possible_paths:
            if path.exists():
                components_dir = path
                print(f"📁 Found components directory: {path}")
                break
        
        if not components_dir:
            print("⚠️  Could not find standard components directory, scanning entire repo...")
            components_dir = self.repo_path
        
        # Process components
        self._scan_for_components(components_dir)
        
        # Add some default components if none found
        if not self.components:
            print("⚠️  No components found, adding default GCDS components...")
            self._add_default_components()
        
        # Build knowledge base structure
        knowledge_base = {
            "version": "1.0",
            "source": "https://github.com/cds-snc/gcds-components",
            "generated_at": str(Path.cwd()),
            "components": self.components,
            "categories": self._categorize_components(),
            "usage_patterns": self._extract_usage_patterns(),
            "total_components": len(self.components)
        }
        
        print(f"✅ Built knowledge base with {len(self.components)} components")
        return knowledge_base
    
    def _scan_for_components(self, directory):
        """Recursively scan for component files"""
        print(f"🔍 Scanning directory: {directory}")
        
        file_count = 0
        for item in directory.rglob("*"):
            if item.is_file() and not any(skip in str(item) for skip in ['.git', 'node_modules', 'dist', 'build']):
                file_count += 1
                
                if item.suffix in ['.ts', '.tsx', '.js', '.jsx', '.vue', '.svelte']:
                    self._process_component_file(item)
                elif item.suffix in ['.md'] and any(keyword in item.name.lower() for keyword in ['readme', 'component', 'usage']):
                    self._process_documentation_file(item)
        
        print(f"📊 Scanned {file_count} files")
    
    def _process_component_file(self, file_path):
        """Process individual component files"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Skip if file doesn't seem to be a component
            if not self._is_component_file(content, file_path):
                return
            
            # Extract component information
            component_info = {
                "name": self._extract_component_name(file_path, content),
                "file_path": str(file_path.relative_to(self.repo_path)),
                "type": self._determine_component_type(content),
                "props": self._extract_props(content),
                "usage_examples": self._extract_usage_examples(content),
                "description": self._extract_description(content),
                "category": self._categorize_component(file_path, content),
                "source_file": file_path.name
            }
            
            if component_info["name"] and not self._is_duplicate(component_info["name"]):
                self.components.append(component_info)
                print(f"  ✅ Found component: {component_info['name']}")
                
        except Exception as e:
            print(f"  ⚠️  Error processing {file_path.name}: {e}")
    
    def _is_component_file(self, content, file_path):
        """Check if file appears to be a component"""
        # Look for component indicators
        indicators = [
            '@Component',
            'customElements.define',
            'class.*Component',
            'export.*Component',
            'gcds-',
            'React.Component',
            '<template>',
            'Vue.extend'
        ]
        
        for indicator in indicators:
            if re.search(indicator, content, re.IGNORECASE):
                return True
        
        # Check filename patterns
        filename_patterns = [
            r'gcds-.*\.(ts|tsx|js|jsx)$',
            r'.*component\.(ts|tsx|js|jsx)$',
            r'.*\.component\.(ts|tsx|js|jsx)$'
        ]
        
        for pattern in filename_patterns:
            if re.search(pattern, str(file_path), re.IGNORECASE):
                return True
        
        return False
    
    def _is_duplicate(self, name):
        """Check if component name already exists"""
        return any(comp["name"].lower() == name.lower() for comp in self.components)
    
    def _process_documentation_file(self, file_path):
        """Process documentation files"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Extract examples and usage from documentation
            examples = self._extract_code_blocks(content)
            component_name = self._guess_component_from_path(file_path)
            
            # Find existing component and add documentation
            for component in self.components:
                if component_name and component_name.lower() in component["name"].lower():
                    component["documentation"] = content[:1000]  # Limit size
                    component["usage_examples"].extend(examples[:3])  # Limit examples
                    break
                    
        except Exception as e:
            print(f"  ⚠️  Error processing documentation {file_path.name}: {e}")
    
    def _extract_component_name(self, file_path, content):
        """Extract component name from file"""
        # Try to extract from various patterns
        patterns = [
            r'@Component\s*\(\s*{\s*tag:\s*[\'"]([a-z-]+)[\'"]',  # Stencil
            r'customElements\.define\s*\(\s*[\'"]([a-z-]+)[\'"]',  # Web Components
            r'class\s+([A-Z][a-zA-Z0-9]*)\s*(?:extends|implements)',  # Class definitions
            r'export\s+(?:default\s+)?(?:class|function|const)\s+([A-Z][a-zA-Z0-9]*)',  # Exports
            r'const\s+([A-Z][a-zA-Z0-9]*)\s*=.*(?:React\.Component|Component)',  # React
            r'name:\s*[\'"]([A-Z][a-zA-Z0-9]*)[\'"]',  # Vue name property
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                name = match.group(1)
                # Convert to proper format
                if name.startswith('gcds-'):
                    return name
                elif '-' in name:
                    return name
                else:
                    # Convert PascalCase to kebab-case for web components
                    return re.sub(r'(?<!^)(?=[A-Z])', '-', name).lower()
        
        # Fallback to filename
        filename = file_path.stem
        if filename.startswith('gcds-'):
            return filename
        elif 'gcds' in filename.lower():
            return f"gcds-{filename.replace('gcds', '').strip('-_.')}"
        else:
            return f"gcds-{filename.replace('_', '-').replace('.component', '')}"
    
    def _determine_component_type(self, content):
        """Determine the type of component"""
        if re.search(r'@Component|customElements\.define', content):
            return "web-component"
        elif re.search(r'React\.|from [\'"]react[\'"]', content):
            return "react-component"
        elif re.search(r'Vue\.|<template>', content):
            return "vue-component"
        elif re.search(r'<script.*svelte', content):
            return "svelte-component"
        else:
            return "component"
    
    def _extract_props(self, content):
        """Extract component properties/attributes"""
        props = []
        
        # Look for @Prop decorators (Stencil)
        prop_pattern = r'@Prop\(\s*(?:{[^}]*})?\s*\)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[?!]?\s*:\s*([^;=\n]+)'
        for match in re.finditer(prop_pattern, content):
            props.append({
                "name": match.group(1),
                "type": match.group(2).strip(),
                "required": '?' not in match.group(0)
            })
        
        # Look for interface definitions
        interface_pattern = r'interface\s+\w*Props\s*{([^}]+)}'
        interface_match = re.search(interface_pattern, content, re.DOTALL)
        if interface_match:
            prop_lines = interface_match.group(1).strip().split('\n')
            for line in prop_lines:
                line = line.strip()
                if not line or line.startswith('//') or line.startswith('*'):
                    continue
                    
                prop_match = re.match(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\??\s*:\s*([^;,\n]+)', line)
                if prop_match:
                    props.append({
                        "name": prop_match.group(1),
                        "type": prop_match.group(2).strip().rstrip(';,'),
                        "required": '?' not in line
                    })
        
        # Look for TypeScript property definitions
        property_pattern = r'(?:public|private|protected)?\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*[?!]?\s*:\s*([^;=\n]+)'
        for match in re.finditer(property_pattern, content):
            if not any(p["name"] == match.group(1) for p in props):  # Avoid duplicates
                props.append({
                    "name": match.group(1),
                    "type": match.group(2).strip(),
                    "required": '?' not in match.group(0)
                })
        
        return props[:10]  # Limit to avoid too many props
    
    def _extract_usage_examples(self, content):
        """Extract usage examples from comments and code"""
        examples = []
        
        # Look for JSDoc examples
        example_pattern = r'/\*\*[\s\S]*?@example\s*([\s\S]*?)\*/'
        for match in re.finditer(example_pattern, content):
            example = match.group(1).strip()
            if example and len(example) < 500:
                examples.append(example)
        
        # Look for HTML/JSX in comments
        comment_html_pattern = r'//\s*(<[^>]+>.*?<\/[^>]+>)'
        for match in re.finditer(comment_html_pattern, content):
            examples.append(match.group(1))
        
        # Look for template literals or JSX
        template_pattern = r'`(<[^`]+>.*?<\/[^`]+>)`'
        for match in re.finditer(template_pattern, content, re.DOTALL):
            if len(match.group(1)) < 300:
                examples.append(match.group(1))
        
        return examples[:5]  # Limit examples
    
    def _extract_description(self, content):
        """Extract component description"""
        # Look for JSDoc comments at the beginning
        jsdoc_pattern = r'/\*\*\s*(.*?)\s*\*/'
        match = re.search(jsdoc_pattern, content, re.DOTALL)
        if match:
            description = match.group(1)
            # Clean up the description
            description = re.sub(r'\*\s*', '', description)
            description = re.sub(r'@\w+.*', '', description, flags=re.DOTALL)
            description = description.strip()
            if description and len(description) < 500:
                return description
        
        # Look for single-line comments
        comment_pattern = r'//\s*(.+)'
        comments = re.findall(comment_pattern, content)
        if comments:
            return comments[0].strip()
        
        return ""
    
    def _categorize_component(self, file_path, content):
        """Categorize component based on path and content"""
        path_str = str(file_path).lower()
        content_lower = content.lower()
        
        categories = {
            "interactive": ["button", "link", "toggle", "switch"],
            "form": ["input", "textarea", "form", "select", "checkbox", "radio", "fieldset"],
            "layout": ["card", "panel", "container", "grid", "flex"],
            "navigation": ["nav", "header", "footer", "breadcrumb", "pagination", "menu"],
            "feedback": ["alert", "toast", "modal", "dialog", "notification"],
            "display": ["table", "list", "tag", "badge", "avatar"],
            "media": ["image", "icon", "video"]
        }
        
        for category, keywords in categories.items():
            if any(keyword in path_str or keyword in content_lower for keyword in keywords):
                return category
        
        return "general"
    
    def _categorize_components(self):
        """Create category mappings"""
        categories = {}
        for component in self.components:
            category = component.get("category", "general")
            if category not in categories:
                categories[category] = []
            categories[category].append(component["name"])
        return categories
    
    def _extract_usage_patterns(self):
        """Extract common usage patterns"""
        patterns = {
            "interactive_elements": [c["name"] for c in self.components if c.get("category") == "interactive"],
            "form_elements": [c["name"] for c in self.components if c.get("category") == "form"],
            "layout_elements": [c["name"] for c in self.components if c.get("category") == "layout"],
            "navigation_elements": [c["name"] for c in self.components if c.get("category") == "navigation"],
            "feedback_elements": [c["name"] for c in self.components if c.get("category") == "feedback"]
        }
        return patterns
    
    def _extract_code_blocks(self, content):
        """Extract code blocks from markdown content"""
        code_blocks = []
        pattern = r'```(?:\w+)?\s*(.*?)```'
        for match in re.finditer(pattern, content, re.DOTALL):
            block = match.group(1).strip()
            if block and len(block) < 500:
                code_blocks.append(block)
        return code_blocks
    
    def _guess_component_from_path(self, file_path):
        """Guess component name from file path"""
        parts = file_path.parts
        for part in reversed(parts):
            if part.startswith('gcds-') or 'component' in part.lower():
                return part.replace('.md', '').replace('.component', '')
        return file_path.stem
    
    def _add_default_components(self):
        """Add default GCDS components if none were found"""
        default_components = [
            {
                "name": "gcds-button",
                "type": "web-component",
                "category": "interactive",
                "description": "Interactive button component for user actions",
                "props": [
                    {"name": "button-id", "type": "string", "required": True},
                    {"name": "button-role", "type": "string", "required": False},
                    {"name": "disabled", "type": "boolean", "required": False}
                ],
                "usage_examples": ["<gcds-button button-id=\"my-button\">Click me</gcds-button>"],
                "file_path": "default"
            },
            {
                "name": "gcds-input",
                "type": "web-component",
                "category": "form",
                "description": "Text input component for forms",
                "props": [
                    {"name": "input-id", "type": "string", "required": True},
                    {"name": "label", "type": "string", "required": True},
                    {"name": "required", "type": "boolean", "required": False}
                ],
                "usage_examples": ["<gcds-input input-id=\"name\" label=\"Full Name\" required></gcds-input>"],
                "file_path": "default"
            },
            {
                "name": "gcds-link",
                "type": "web-component",
                "category": "interactive",
                "description": "Link component for navigation",
                "props": [
                    {"name": "href", "type": "string", "required": True},
                    {"name": "external", "type": "boolean", "required": False}
                ],
                "usage_examples": ["<gcds-link href=\"https://canada.ca\">Visit Canada.ca</gcds-link>"],
                "file_path": "default"
            }
        ]
        
        self.components.extend(default_components)
        print(f"✅ Added {len(default_components)} default components")

# Test function
def test_processor():
    """Test the knowledge processor"""
    import tempfile
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        test_processor = GCDSKnowledgeProcessor(temp_dir)
        kb = test_processor.build_knowledge_base()
        print(f"Test knowledge base created with {len(kb['components'])} components")

if __name__ == "__main__":
    test_processor()