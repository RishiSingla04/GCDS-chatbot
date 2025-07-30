# GCDS Components Chatbot

# A local chatbot that helps developers with Government of Canada Design System (GCDS) components. Uses Ollama for local LLM inference with no API keys required.

# Features:

🤖 Local LLM powered by Ollama
🎨 Answers design-related questions about GCDS components
💻 Provides code examples and usage guidance
🖥️ Simple GUI interface built with Tkinter
📚 Knowledge base built from GCDS components repository
🔒 100% local and private - no API keys needed

# Prerequisites

Python 3.8+ installed on your system
Ollama installed and running (Download here)
Git for cloning repositories
Setup Instructions

1. Clone this repository
   git clone <https://github.com/RishiSingla04/GCDS-chatbot.git>
   cd gcds-chatbot
2. Install Ollama and pull a model
   Install ollama (if not already installed)
   Visit https://ollama.ai/ for installation instructions

Pull the recommended model
ollama pull hf.co/unsloth/gemma-3-1b-it-GGUF:Q4_K_M

3. Set up Python environment (optional, you may skip to step 4. if you are not using a python environment)
   python -m venv gcds-chatbot-env

Activate virtual environment
On macOS/Linux:
source gcds-chatbot-env/bin/activate

On Windows:
gcds-chatbot-env\Scripts\activate

4. Install dependencies

pip install -r requirements.txt

5. Initialize the knowledge base
   python setup_knowledge_base.py

6. Run the chatbot
   python chatbot_gui.py

# Project Structure

gcds-chatbot/
├── README.md
├── requirements.txt
├── setup_knowledge_base.py # Clones GCDS repo and processes components
├── chatbot_gui.py # Main GUI application
├── chatbot_core.py # Core chatbot logic and Ollama integration
├── knowledge_processor.py # Processes GCDS components into knowledge base
├── data/
│ ├── gcds-components/ # Cloned GCDS repository
│ └── knowledge_base.json # Processed component knowledge
└── gcds-chatbot-env/ # Virtual environment (created during setup)
Usage Examples
Question: "I need an interactive link, what component should I use?"
Answer: "You can use the gcds-link component for interactive links. Here's the code:
html
<gcds-link href="https://example.com">Link text</gcds-link>
For buttons that look like links, you can also use:
html
<gcds-button button-role="secondary" button-id="link-button">
Button Link
</gcds-button>

````"

**Question:** "Can you give me the code for a text area?"

**Answer:** "You can use the `gcds-textarea` component:

```html
<gcds-textarea
  textarea-id="description"
  label="Description"
  hint="Enter your description here"
  required>
</gcds-textarea>
```"

## Supported Models

This chatbot works with various Ollama models:
- **mistral:7b** - Recommended default (fast and efficient)
- **llama3.1:8b** - Good balance of speed and quality
- **codellama:7b** - Optimized for code generation
- **llama3.1:70b** - Highest quality (requires more RAM)

You can change the model in `chatbot_core.py` by modifying the `MODEL_NAME` variable.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Troubleshooting

### Ollama not responding
- Ensure Ollama is running: `ollama serve`
- Check if your model is available: `ollama list`
- Try pulling the model again: `ollama pull mistral:7b`

### Knowledge base empty
- Run `python setup_knowledge_base.py` again
- Check internet connection for cloning GCDS repository
- Ensure Git is installed and accessible

### GUI not appearing
- Make sure you're in the correct virtual environment
- Try: `pip install --upgrade tkinter` (though it's usually built-in)
- On Linux, you might need: `sudo apt-get install python3-tk`

## License

MIT License - Feel free to use this project for learning and development.
````
