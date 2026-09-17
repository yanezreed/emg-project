from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QScrollArea, QWidget
from PySide6.QtCore import Qt
from config import user_ebay_account as users_ebay_username

class REVIEW_DIALOG(QDialog):
    def __init__(self, parent, sanitised_messages):
        super().__init__(parent)

        self.setWindowTitle("Manual review")
        self.setFixedSize(1025, 600)
        self.setModal(False)

        self.sanitised_messages = sanitised_messages 
        # passed from parent generate_dialog...

        self.qtextedit_reference_list = []

        major_layout = QVBoxLayout(self)

        review_label_one = QLabel("This is a non modal window, allowing you to compare both versions and restore incorrectly removed information if not sensitive.")
        review_label_one.setWordWrap(True)
        major_layout.addWidget(review_label_one)

        review_label_two = QLabel("Confirm the review only when you are satisfied that no sensitive customer information remains.")
        review_label_two.setWordWrap(True)
        major_layout.addWidget(review_label_two)

        self.message_window = QScrollArea()
        self.message_window.setWidgetResizable(True)
        # enables widgets to resize to fit this qscrollarea

        self.conversation_container = QWidget()
        self.conversation_layout = QVBoxLayout(self.conversation_container)
        self.conversation_layout.setSpacing(6)
        self.conversation_layout.setAlignment(Qt.AlignTop)

        self.message_window.setWidget(self.conversation_container)
        major_layout.addWidget(self.message_window)

        self.render_messages(sanitised_messages)

        button_row = QHBoxLayout()
        button_row.addStretch()

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_row.addWidget(cancel_button)

        confirm_button = QPushButton("Confirm review")
        confirm_button.clicked.connect(self.review_confirm)
        button_row.addWidget(confirm_button)

        major_layout.addLayout(button_row)

    def render_messages(self, messages_list_of_dicts):

        self.qtextedit_reference_list = []
        # stores each sender username + reference to the qtextedit, 
        # allowing the users edited text to be accessed in review_confirm

        for message_dict in messages_list_of_dicts:

            sender_username = message_dict["senderUsername"]
            message_text = message_dict["messageBody"]

            if sender_username != users_ebay_username:
                display_name = "Customer"
            else:
                display_name = "You"

            message_sender_identity = QLabel(display_name)

            editable_textbox = QTextEdit()
            editable_textbox.setPlainText(message_text)
            # note, editable_textbox is storing a refference to the qtextedit and not simply text...
            self.qtextedit_reference_list.append({"senderUsername": sender_username, "text_box": editable_textbox})

            message_layout = QVBoxLayout()

            message_layout.addWidget(message_sender_identity)
            message_layout.addWidget(editable_textbox)

            new_row = QHBoxLayout()

            if sender_username != users_ebay_username:
                # stretch occupies half the qboxlayout
                new_row.addLayout(message_layout)
                new_row.addStretch()
            else:
                message_sender_identity.setAlignment(Qt.AlignRight)
                new_row.addStretch()
                new_row.addLayout(message_layout)

            row_widget = QWidget()
            row_widget.setLayout(new_row)
            # layout must be wrapped within a widget
            # before it is added to yet another layout
            self.conversation_layout.addWidget(row_widget)

        scrollbar = self.message_window.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        # scrollbar set to maximum outside loop

    def review_confirm(self):
        reviewed_messages = []

        for updated_qtext_widget in self.qtextedit_reference_list:
        # builds a reviewed message list from the updated qtext...

            sender_username = updated_qtext_widget["senderUsername"]
            message_body = updated_qtext_widget["text_box"].toPlainText()

            reviewed_message = {"senderUsername": sender_username, "messageBody": message_body}
            reviewed_messages.append(reviewed_message)

        self.sanitised_messages = reviewed_messages 
        # hand reviewed messages to generate_dialog
        self.accept()