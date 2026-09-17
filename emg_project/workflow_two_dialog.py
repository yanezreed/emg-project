from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QMessageBox
from PySide6.QtGui import QTextCursor, QTextCharFormat, QBrush, QColor
from prompt_workflow_two import workflow_two_instructions
from config import ollama_url
import requests

class WORKFLOW_TWO_DIALOG(QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        self.setWindowTitle("Ai Support")
        self.setFixedSize(1025, 600)
        self.setModal(False)

        major_layout = QVBoxLayout(self)
        layout_label = QLabel("Ai response widget")
        major_layout.addWidget(layout_label)

        self.ollama_conversation = QTextEdit()
        self.ollama_conversation.setReadOnly(True)
        self.ollama_conversation.setStyleSheet("background-color: #F0F0F0;")
        major_layout.addWidget(self.ollama_conversation)

        self.text_conversation = []

        initial_message = ("This window has been designed to be used alongside the main conversation window.\n\n"
            "The customer conversation is never passed to the ai within this workflow. So please never enter personally identifiable customer information.\n"
            "Feel free however to ask questions about products, policies and how to prepare a reply. As the ai has access to internal business information.")
        
        self.add_message_to_conversation(initial_message)

        self.user_input = QTextEdit()
        self.user_input.setMaximumHeight(80)
        self.user_input.setPlaceholderText("Ask for business information or support with preparing your reply...")
        major_layout.addWidget(self.user_input)

        button_row = QHBoxLayout()

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_row.addWidget(cancel_button)

        ask_button = QPushButton("Send to AI")
        ask_button.clicked.connect(self.ask_ai)
        button_row.addWidget(ask_button)

        continue_button = QPushButton("Continue")
        continue_button.clicked.connect(self.accept)
        button_row.addWidget(continue_button)

        major_layout.addLayout(button_row)

    def load_business_information(self):
        try:
            with open("business_info.txt", "r", encoding = "utf-8") as file:
                business_information = file.read()
        except FileNotFoundError:
            business_information = "Error: business_info.txt not found."
        return business_information

    def build_prompt(self, newest_user_question):

        prompt = workflow_two_instructions + "\n\n"
        prompt += self.load_business_information() + "\n\n"

        prompt += "Previous AI assistance conversation:\n"

        for conversation_message in self.text_conversation:
            prompt += conversation_message + "\n"

        prompt += "\n"
        prompt += "User question:\n" + newest_user_question + "\n\n"
        return prompt

    def ask_ai(self):
        user_question = self.user_input.toPlainText().strip()

        if user_question == "":
            QMessageBox.warning(self, "Question required", "Please enter a question for llama.")
            return

        self.add_message_to_conversation("You: " + user_question, "white")

        prompt = self.build_prompt(user_question)
        generated_text = self.call_ai(prompt)

        if generated_text == None: # returns no reply
            return

        self.add_message_to_conversation("Llama 3.1: " + generated_text)

        self.text_conversation.append("User: " + user_question)
        self.text_conversation.append("Llama 3.1: " + generated_text)
        # both sides of exchange stored, for furture reply generation
        self.user_input.clear()

    def add_message_to_conversation(self, text, highlight_colour=None):

        cursor = self.ollama_conversation.textCursor()
        cursor.movePosition(QTextCursor.End)

        # again, this creates a format for
        # the text to go within...
        message_format = QTextCharFormat()

        if highlight_colour == "white":

            colour = QColor("white")
            brush = QBrush(colour)
            message_format.setBackground(brush)

        cursor.insertText(text, message_format)

        normal_format = QTextCharFormat()
        cursor.insertText("\n\n", normal_format)
        # normalises format after text insert...

        # scrolls the window to the newest, at the lists end
        self.ollama_conversation.moveCursor(QTextCursor.End)

    def call_ai(self, prompt):

        model = "llama3.1:8b"
        try:
            response = requests.post(ollama_url, json = {"model": model, "prompt": prompt, "stream": False}, timeout = 60)
            # sends prompt to ollamas ran local api server
            response_python_dict = response.json()
            llama_reply = response_python_dict["response"]

            return llama_reply

        except:
            QMessageBox.warning(self, "Ollama Error", "No response received from Ollama.\nPlease check the program is running.")