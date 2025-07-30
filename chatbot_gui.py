#!/usr/bin/env python3
"""
Simple GUI for the GCDS Chatbot using Tkinter
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import datetime
from chatbot_core import GCDSChatbot

class GCDSChatbotGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GCDS Components Chatbot")
        self.root.geometry("800x600")
        self.root.configure(bg='#f8f9fa')
        
        # Initialize chatbot
        try:
            self.chatbot = GCDSChatbot()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize chatbot: {e}")
            self.root.destroy()
            return
        
        self.setup_ui()
        self.add_welcome_message()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Title
        title_frame = tk.Frame(self.root, bg='#f8f9fa')
        title_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        title_label = tk.Label(
            title_frame,
            text="🍁 GCDS Components Chatbot",
            font=('Arial', 28, 'bold'),
            bg='#f8f9fa',
            fg='#2c3e50'
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="Ask me about Government of Canada Design System components",
            font=('Arial', 20),
            bg='#f8f9fa',
            fg='#7f8c8d'
        )
        subtitle_label.pack()
        
        # Chat display area
        chat_frame = tk.Frame(self.root, bg='#f8f9fa')
        chat_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            width=80,
            height=25,
            font=('Consolas', 20),
            bg='white',
            fg='#2c3e50',
            relief='solid',
            borderwidth=1
        )
        self.chat_display.pack(fill='both', expand=True)
        self.chat_display.config(state='disabled')
        
        # Input area
        input_frame = tk.Frame(self.root, bg='#f8f9fa')
        input_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        self.input_entry = tk.Entry(
            input_frame,
            font=('Arial', 21),
            relief='solid',
            borderwidth=1
        )
        self.input_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        self.input_entry.bind('<Return>', self.send_message)
        
        self.send_button = tk.Button(
            input_frame,
            text="Send",
            command=self.send_message,
            bg='#3498db',
            fg='white',
            font=('Arial', 20, 'bold'),
            relief='flat',
            padx=20
        )
        self.send_button.pack(side='right')
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            relief='sunken',
            anchor='w',
            bg='#ecf0f1',
            fg='#7f8c8d'
        )
        status_bar.pack(side='bottom', fill='x')
        
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Example Questions", command=self.show_examples)
        help_menu.add_command(label="Available Components", command=self.show_components)
        help_menu.add_separator()
        help_menu.add_command(label="Clear Chat", command=self.clear_chat)
    
    def add_welcome_message(self):
        """Add welcome message to chat"""
        welcome_msg = """👋 Welcome to the GCDS Components Chatbot!

I can help you with:
• Finding the right GCDS component for your needs
• Providing code examples and usage instructions
• Explaining component properties and attributes

Try asking:
• "I need an interactive button, what should I use?"
• "Can you give me the code for a text input?"
• "How do I create a form with GCDS components?"

Type your question below and press Enter!
"""
        self.add_message("Chatbot", welcome_msg)
    
    def send_message(self, event=None):
        """Send user message and get bot response"""
        user_message = self.input_entry.get().strip()
        if not user_message:
            return
        
        # Clear input
        self.input_entry.delete(0, tk.END)
        
        # Add user message to chat
        self.add_message("You", user_message)
        
        # Show typing indicator
        self.status_var.set("Thinking...")
        self.send_button.config(state='disabled')
        
        # Get bot response in separate thread to avoid freezing UI
        def get_response():
            try:
                bot_response = self.chatbot.chat(user_message)
                self.root.after(0, lambda: self.handle_bot_response(bot_response))
            except Exception as e:
                error_msg = f"Sorry, I encountered an error: {str(e)}"
                self.root.after(0, lambda: self.handle_bot_response(error_msg))
        
        threading.Thread(target=get_response, daemon=True).start()
    
    def handle_bot_response(self, response):
        """Handle bot response in main thread"""
        self.add_message("Chatbot", response)
        self.status_var.set("Ready")
        self.send_button.config(state='normal')
        self.input_entry.focus()
    
    def add_message(self, sender, message):
        """Add message to chat display"""
        self.chat_display.config(state='normal')
        
        # Add timestamp
        timestamp = datetime.datetime.now().strftime("%H:%M")
        
        # Add sender and message
        if sender == "You":
            self.chat_display.insert(tk.END, f"\n[{timestamp}] You: ", "user")
            self.chat_display.insert(tk.END, f"{message}\n", "user_msg")
        else:
            self.chat_display.insert(tk.END, f"\n[{timestamp}] 🤖: ", "bot")
            self.chat_display.insert(tk.END, f"{message}\n", "bot_msg")
        
        # Configure text tags for styling
        self.chat_display.tag_configure("user", foreground="#2980b9", font=('Arial', 20, 'bold'))
        self.chat_display.tag_configure("user_msg", foreground="#2c3e50")
        self.chat_display.tag_configure("bot", foreground="#27ae60", font=('Arial', 20, 'bold'))
        self.chat_display.tag_configure("bot_msg", foreground="#2c3e50")
        
        # Scroll to bottom
        self.chat_display.see(tk.END)
        self.chat_display.config(state='disabled')
    
    def show_examples(self):
        """Show example questions"""
        examples = """Example Questions:

🔸 Component Selection:
• "I need an interactive link, what component should I use?"
• "What component should I use for user input?"
• "How do I create a dropdown menu?"

🔸 Code Examples:
• "Can you give me the code for a text area?"
• "Show me how to create a button"
• "How do I make a form with validation?"

🔸 Component Properties:
• "What properties does the button component have?"
• "How do I make an input field required?"
• "What are the different button styles available?"

🔸 Layout and Design:
• "How do I create a card layout?"
• "What components can I use for navigation?"
• "How do I display error messages?"
"""
        messagebox.showinfo("Example Questions", examples)
    
    def show_components(self):
        """Show available components"""
        components = self.chatbot.get_available_components()
        categories = self.chatbot.get_component_categories()
        
        info = "Available GCDS Components:\n\n"
        
        if categories:
            for category, comps in categories.items():
                info += f"📁 {category.title()}:\n"
                for comp in comps[:5]:  # Limit to avoid too long dialog
                    info += f"  • {comp}\n"
                info += "\n"
        else:
            info += "\n".join(f"• {comp}" for comp in components[:20])
        
        if len(components) > 20:
            info += f"\n... and {len(components) - 20} more components"
        
        messagebox.showinfo("Available Components", info)
    
    def clear_chat(self):
        """Clear chat history"""
        self.chat_display.config(state='normal')
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state='disabled')
        self.chatbot.clear_history()
        self.add_welcome_message()
    
    def run(self):
        """Start the GUI application"""
        self.input_entry.focus()
        self.root.mainloop()

def main():
    """Main function to run the chatbot GUI"""
    try:
        app = GCDSChatbotGUI()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error starting application: {e}")

if __name__ == "__main__":
    main()