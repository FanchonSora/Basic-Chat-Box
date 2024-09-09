import tkinter as tk
from tkinter import scrolledtext
import json
from difflib import get_close_matches

def load_knowledge_base(file_path: str) -> dict:
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print("Knowledge base file not found. Creating a new one.")
        return {"questions": []}

def save_knowledge_base(file_path: str, data: dict) -> None:
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

def find_best_match(user_question: str, questions: list[str]) -> str | None:
    matches = get_close_matches(user_question, questions, n=1, cutoff=0.7)
    return matches[0] if matches else None

def get_answer_for_question(question: str, knowledge_base: dict) -> str | None:
    for q in knowledge_base["questions"]:
        if q["question"] == question:
            return q["answer"]
    return None

class ChatBoxApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chatbox")

        # Load knowledge base
        self.knowledge_base = load_knowledge_base("knowledge_base.json")

        # Create GUI components
        self.create_widgets()

    def create_widgets(self):
        # Create a scrolled text widget for displaying conversation
        self.conversation_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, state='disabled')
        self.conversation_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Create an entry widget for user input
        self.user_input = tk.Entry(self.root, width=80)
        self.user_input.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)
        self.user_input.bind("<Return>", self.on_send)

        # Create a send button
        self.send_button = tk.Button(self.root, text="Send", command=self.on_send)
        self.send_button.pack(side=tk.RIGHT, padx=10, pady=10)

    def on_send(self, event=None):
        user_question = self.user_input.get()
        if user_question.lower() == "quit":
            self.root.quit()
            return

        self.display_message(f"You: {user_question}")

        best_match = find_best_match(user_question, [q["question"] for q in self.knowledge_base["questions"]])

        if best_match:
            answer = get_answer_for_question(best_match, self.knowledge_base)
            self.display_message(f"Bot: {answer}")
        else:
            self.display_message("Bot: I don't know what you meant. Can you teach me?")
            self.user_input.delete(0, tk.END)

            # Prompt for new answer
            self.root.after(100, self.prompt_for_new_answer, user_question)
        self.user_input.delete(0, tk.END)

    def prompt_for_new_answer(self, user_question):
        # Display a message asking for a new answer
        self.display_message("Bot: Provide an answer to the next box or type 'skip' to skip")

        # Create a new entry field for new answer input
        self.new_answer_entry = tk.Entry(self.root, width=80)
        self.new_answer_entry.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)
        self.new_answer_entry.bind("<Return>", lambda event: self.submit_new_answer(user_question))

    def submit_new_answer(self, user_question):
        new_answer = self.new_answer_entry.get().strip()
        self.new_answer_entry.destroy()
        if new_answer.lower() != "skip":
            self.knowledge_base["questions"].append({"question": user_question, "answer": new_answer})
            save_knowledge_base("knowledge_base.json", self.knowledge_base)
            self.display_message("Bot: Thanks for your answer!")
        else:
            self.display_message("Bot: Hope you teach me next time")

    def display_message(self, message):
        self.conversation_area.config(state='normal')
        self.conversation_area.insert(tk.END, f"{message}\n")
        self.conversation_area.config(state='disabled')
        self.conversation_area.yview(tk.END)

if __name__ == '__main__':
    root = tk.Tk()
    app = ChatBoxApp(root)
    root.mainloop()
