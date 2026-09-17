from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QMessageBox
from PySide6.QtGui import QTextCursor, QTextCharFormat, QBrush, QColor

from config import ollama_url, user_ebay_account
from prompt_workflow_one import llama_prompt_instructions
import requests

class REPLY_DIALOG(QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        self.generate_dialog = parent
        # enables access to formatted
        # sanitised messages...

        self.recording_ai_conversation_history = []
        self.current_generated_reply = ""
        self.user_instructions = ""

        self.setWindowTitle("Generated reply")
        self.setFixedSize(1025, 600)
        self.setModal(True)

        major_layout = QVBoxLayout(self)
        major_layout.addWidget(QLabel("Ai response widget"))

        self.ai_conversation_window = QTextEdit()
        self.ai_conversation_window.setReadOnly(True)
        # for simplicity sake, ive excluded this styling from qt_style_sheet.py
        self.ai_conversation_window.setStyleSheet("background-color: #F0F0F0;")
        major_layout.addWidget(self.ai_conversation_window)

        self.user_instruction_window = QTextEdit()
        self.user_instruction_window.setPlaceholderText("Ask llama questions or request an improvement to the reply...")
        self.user_instruction_window.setMaximumHeight(80)
        major_layout.addWidget(self.user_instruction_window)

        major_layout.addWidget(QLabel("Generated reply"))
        self.returned_reply = QTextEdit()
        self.returned_reply.setPlaceholderText("Copy the text following 'Generated reply:' in the conversation box to here...")
        self.returned_reply.setMaximumHeight(80)
        major_layout.addWidget(self.returned_reply)

        button_row = QHBoxLayout()

        back_button = QPushButton("Back")
        back_button.clicked.connect(self.reject)
        button_row.addWidget(back_button)

        self.generate_button = QPushButton("Reply")
        self.generate_button.clicked.connect(self.generate_reply)
        button_row.addWidget(self.generate_button)

        self.continue_button = QPushButton("Continue")
        self.continue_button.clicked.connect(self.continue_to_chat_widget)
        button_row.addWidget(self.continue_button)

        major_layout.addLayout(button_row)

        QMessageBox.information(self,"Generating reply", "The initial reply is now being generated.")
        # messagebox required to inform user that the program hasnt crashed but is generating a reply

        self.generate_initial_reply()

    def load_business_information(self):

        try:
            with open("business_info.txt", "r", encoding = "utf-8") as file:
                internal_business_information = ""

                for text_line in file:
                    internal_business_information += text_line
        except:
            internal_business_information = "business_info.txt not found."

        return internal_business_information

    def build_conversation_text(self):
        formatted_conversation = "Reviewed conversation history:\n"
        
        for sanitised_message in self.generate_dialog.sanitised_messages:
            # accessing passed sanitised messages from generate_dialog...

            if sanitised_message["senderUsername"] != user_ebay_account:
                sender_username = "Customer"

            else:
                sender_username = "Seller" 

            formatted_conversation += f"{sender_username}: "
            formatted_conversation += f"{sanitised_message['messageBody']}\n"

        return formatted_conversation

    def build_ai_conversation_text(self):

        formatted_ai_conversation = "Previous assistance conversation:\n"

        for conversation_message in self.recording_ai_conversation_history:
            formatted_ai_conversation += conversation_message + "\n"

        return formatted_ai_conversation

    def build_current_reply_text(self):

        current_reply = self.returned_reply.toPlainText().strip()

        formatted_current_reply = "Current customer reply:\n"
        formatted_current_reply += current_reply

        return formatted_current_reply

    def build_user_instruction_text(self):

        formatted_user_instruction = "New application user instruction:\n"
        formatted_user_instruction += self.user_instructions

        return formatted_user_instruction

    def build_prompt(self):

        internal_business_information = self.load_business_information()

        reviewed_ebay_conversation_text = self.build_conversation_text()

        current_reply_text = self.build_current_reply_text()
        # note, this is the current reply being worked on...

        ai_conversation_text = self.build_ai_conversation_text()
        # note, this is the current user conversation with llama

        user_instruction_text = self.build_user_instruction_text()
        # note, this is instructions written right now by the user

        prompt = llama_prompt_instructions + "\n\n"
        # prompt_workflow_one.py text instructions...
        
        prompt += internal_business_information + "\n\n"
        prompt += reviewed_ebay_conversation_text + "\n\n"
        prompt += current_reply_text + "\n\n"
        prompt += ai_conversation_text + "\n\n"
        prompt += user_instruction_text + "\n\n"

        return prompt

    def call_ai(self, prompt):
        model = "llama3.1:8b"  # the exact model name can always be found by running `ollama list` in local command prompt
        try:
            response = requests.post(ollama_url, json = {"model": model, "prompt": prompt, "stream": False}, timeout = 60)

            response_python_dict = response.json()
            llama_reply = response_python_dict["response"]

            return llama_reply

        except:
            QMessageBox.warning(self, "Ollama Error", "No response received from ollama.\nPlease check the program is running.")

    def generate_initial_reply(self):

        self.ai_conversation_window.clear()
        self.returned_reply.clear()

        self.recording_ai_conversation_history = []
        self.current_generated_reply = ""
        self.user_instructions = ""

        line_one = "A reply will be generated using the reviewed and sanitised conversation.\n"
        line_two = ("You can ask Llama to alter the reply. Copy the text following "
            "'Generated Reply:' into the reply box before continuing.")
        self.add_message_to_conversation_window(line_one + line_two)

        prompt = self.build_prompt()

        generated_text = self.call_ai(prompt)

        if generated_text == None:
            # stops generation attempt
            # returned to reply_dialog
            # user can try reply again
            return

        self.display_ai_response(generated_text)

        # stores initial request and llama response with labels as a record allowing later prompts to understand the previous convo
        self.recording_ai_conversation_history.append("Previous application instruction: Create an initial reply to the customer.")

        self.recording_ai_conversation_history.append("Llama response: " + generated_text)

    def generate_reply(self):

        self.user_instructions = self.user_instruction_window.toPlainText().strip()

        if self.user_instructions == "":
            QMessageBox.warning(self, "Instruction missing", "Ai requires instructions to imrpove the reply.")
            return

        self.add_message_to_conversation_window("You: " + self.user_instructions, "white")

        prompt = self.build_prompt()
        generated_text = self.call_ai(prompt)

        if generated_text == None:
        # llama fault, return none
            return

        self.display_ai_response(generated_text)

        self.recording_ai_conversation_history.append("You: " + self.user_instructions)
        self.recording_ai_conversation_history.append("Llama response: " + generated_text)

        # clear window and instance variable
        self.user_instruction_window.clear()
        self.user_instructions = ""

    def display_ai_response(self, generated_text):

        self.add_message_to_conversation_window("Llama 3.1: " + generated_text)

    def continue_to_chat_widget(self):

        reply_text = self.returned_reply.toPlainText().strip()

        if reply_text == "":
            QMessageBox.warning(self, "Reply Required", "Please ensure there is text within the reply box.")
            return

        self.current_generated_reply = reply_text
        self.accept()

    def add_message_to_conversation_window(self, text, highlight_colour = None):

        cursor = self.ai_conversation_window.textCursor()
        cursor.movePosition(QTextCursor.End)
        # identifies cursor position in text
        # moves cursor to end of textedit...

        # note, required as even set as readonly the user can still accidently alter the position

        message_format = QTextCharFormat()

        if highlight_colour == "white":

            colour = QColor("white")
            brush = QBrush(colour)
            message_format.setBackground(brush)

        cursor.insertText(text, message_format)

        normal_format = QTextCharFormat()
        # spacing after a highlighted now
        # not highlighted...

        cursor.insertText("\n\n", normal_format)

        self.ai_conversation_window.moveCursor(QTextCursor.End) # scrolls to end of convo...