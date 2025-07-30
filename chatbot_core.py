#!/usr/bin/env python3
"""
Core chatbot logic with Ollama integration
"""
import json
import sys
from pathlib import Path

# Handle ollama import with error checking
try:
    import ollama
except ImportError:
    print("❌ Ollama package not found. Install with: pip install ollama")
    sys.exit(1)

class GCDSChatbot:
    def __init__(self, knowledge_base_path="data/knowledge_base.json", model_name="hf.co/unsloth/gemma-3-1b-it-GGUF:Q4_K_M"):
        self.model_name = model_name
        self.knowledge_base = self._load_knowledge_base(knowledge_base_path)
        self.conversation_history = []
        
        # Test Ollama connection
        # try:
        #     ollama.list()
        #     print(f"✅ Connected to Ollama")
            
        #     # Check if model is available
        #     available_models = [model['name'] for model in ollama.list()['models']]
        #     if self.model_name not in available_models:
        #         print(f"⚠️  Model '{self.model_name}' not found locally")
        #         print(f"Available models: {', '.join(available_models) if available_models else 'None'}")
        #         print(f"To install: ollama pull {self.model_name}")
        # except Exception as e:
        #     print(f"❌ Could not connect to Ollama: {e}")
        #     print("Make sure Ollama is running with: ollama serve")
    
    def _load_knowledge_base(self, path):
        """Load the processed knowledge base"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                kb = json.load(f)
                print(f"✅ Loaded knowledge base with {len(kb.get('components', []))} components")
                return kb
        except FileNotFoundError:
            print(f"❌ Knowledge base not found at {path}")
            print("Run 'python setup_knowledge_base.py' first")
            return {"components": [], "categories": {}}
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in knowledge base: {e}")
            return {"components": [], "categories": {}}
    
    def chat(self, user_message):
        """Main chat function"""
        if not user_message.strip():
            return "Please ask me a question about GCDS components!"
        
        # Find relevant components
        relevant_components = self._find_relevant_components(user_message)
        
        # Build context
        context = self._build_context(user_message, relevant_components)
        
        # Generate response with Ollama
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user", 
                        "content": f"Context: {context}\n\nQuestion: {user_message}"
                    }
                ],
                options={
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 1000
                }
            )
            
            bot_response = response['message']['content']
            
            # Add to conversation history
            self.conversation_history.append({
                "user": user_message,
                "bot": bot_response,
                "components_used": [c["name"] for c in relevant_components]
            })
            
            return bot_response
            
        except Exception as e:
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            if "model" in str(e).lower():
                error_msg += f"\n\nMake sure the model '{self.model_name}' is installed. Try: ollama pull {self.model_name}"
            elif "connection" in str(e).lower():
                error_msg += "\n\nMake sure Ollama is running: ollama serve"
            return error_msg
    
    def _find_relevant_components(self, query):
        """Find components relevant to the user's query"""
        query_lower = query.lower()
        relevant = []
        
        # Score components based on relevance
        for component in self.knowledge_base.get("components", []):
            if not component.get("name"):
                continue
                
            score = 0
            
            # Check component name (high weight)
            name_words = component["name"].lower().split()
            query_words = query_lower.split()
            for name_word in name_words:
                for query_word in query_words:
                    if name_word in query_word or query_word in name_word:
                        score += 10
            
            # Check description (medium weight)
            if component.get("description"):
                description_lower = component["description"].lower()
                for word in query_words:
                    if word in description_lower:
                        score += 5
            
            # Check category (low weight)
            if component.get("category") and component["category"].lower() in query_lower:
                score += 3
            
            # Check for specific keywords with high relevance
            keyword_mappings = {
                "button": ["button", "click", "interactive", "action", "submit"],
                "link": ["link", "navigate", "url", "href", "anchor"],
                "input": ["input", "text", "field", "form", "textbox"],
                "textarea": ["textarea", "text area", "multiline", "description"],
                "select": ["select", "dropdown", "choose", "option", "picker"],
                "card": ["card", "container", "panel", "box"],
                "alert": ["alert", "message", "notification", "warning", "error"],
                "form": ["form", "validation", "submit", "field"],
                "navigation": ["nav", "menu", "breadcrumb", "pagination"]
            }
            
            component_name_lower = component["name"].lower()
            for component_type, keywords in keyword_mappings.items():
                if component_type in component_name_lower:
                    for keyword in keywords:
                        if keyword in query_lower:
                            score += 15
            
            if score > 0:
                relevant.append({**component, "relevance_score": score})
        
        # Sort by relevance and return top matches
        relevant.sort(key=lambda x: x["relevance_score"], reverse=True)
        return relevant[:3]  # Return top 3 most relevant
    
    def _build_context(self, query, relevant_components):
        """Build context for the LLM"""
        if not relevant_components:
            return "No specific GCDS components found for this query. Please provide general guidance about GCDS components."
        
        context_parts = []
        context_parts.append("You are a helpful assistant for the Government of Canada Design System (GCDS) components.")
        context_parts.append("Below are the most relevant components for this query:")
        
        for component in relevant_components:
            comp_context = f"\n--- {component['name']} ---"
            comp_context += f"\nType: {component.get('type', 'component')}"
            comp_context += f"\nCategory: {component.get('category', 'general')}"
            
            if component.get('description'):
                comp_context += f"\nDescription: {component['description']}"
            
            if component.get('props') and len(component['props']) > 0:
                comp_context += "\nKey Properties:"
                for prop in component['props'][:5]:  # Limit to avoid too much context
                    prop_line = f"\n  - {prop['name']}: {prop.get('type', 'any')}"
                    if prop.get('required'):
                        prop_line += " (required)"
                    comp_context += prop_line
            
            if component.get('usage_examples') and len(component['usage_examples']) > 0:
                comp_context += "\nUsage Examples:"
                for example in component['usage_examples'][:2]:  # Limit examples
                    if example.strip():
                        comp_context += f"\n```\n{example}\n```"
            
            context_parts.append(comp_context)
        
        return "\n".join(context_parts)
    
    def _get_system_prompt(self):
        """Get the system prompt for the LLM"""
        return """You are a helpful assistant specializing in the Government of Canada Design System (GCDS) components. 

Your role is to:
1. Help developers choose the right GCDS component for their needs
2. Provide accurate code examples using GCDS components
3. Explain how to use components properly
4. Give practical implementation advice

Guidelines:
- Always base your answers on the provided component information
- Provide working code examples when requested
- Be concise but thorough
- If you're not sure about something, say so rather than guessing
- Focus on practical, actionable advice
- Use proper HTML/web component syntax for GCDS components

When providing code examples:
- Use proper GCDS component syntax (e.g., <gcds-button>, <gcds-input>)
- Include relevant attributes and properties
- Show complete, working examples when possible
- Explain any important attributes or properties used
- Always include proper closing tags

Response format:
- Start with a direct answer to the question
- Provide code examples in code blocks when relevant
- Add explanatory notes after code examples
- Keep responses focused and helpful"""

    def get_available_components(self):
        """Get list of available components"""
        return [comp["name"] for comp in self.knowledge_base.get("components", []) if comp.get("name")]
    
    def get_component_categories(self):
        """Get component categories"""
        return self.knowledge_base.get("categories", {})
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        print("✅ Conversation history cleared")

# Test function for debugging
def test_chatbot():
    """Test the chatbot functionality"""
    print("Testing GCDS Chatbot...")
    chatbot = GCDSChatbot()
    
    test_queries = [
        "I need a button component",
        "How do I create a text input?",
        "What components are available for forms?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        response = chatbot.chat(query)
        print(f"Response: {response[:200]}...")

if __name__ == "__main__":
    test_chatbot()