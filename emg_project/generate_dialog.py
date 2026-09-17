from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox, QScrollArea, QWidget
from PySide6.QtCore import Qt
from config import user_ebay_account as users_ebay_username
from review_dialog import REVIEW_DIALOG as review_dialog
from reply_dialog import REPLY_DIALOG as reply_dialog

class GENERATE_DIALOG(QDialog):
    def __init__(self, parent, user_object, messages_list_of_dicts):
        # parent chatwidget, user messages_list_of_dicts also passed
        super().__init__(parent)

        self.user_object = user_object
        self.user_messages = messages_list_of_dicts
        # required for access, via signal/slot call

        self.sanitised_messages = None

        self.setWindowTitle("Generate ai reply")
        self.setModal(True)
        self.setFixedSize(725, 410)

        major_layout = QVBoxLayout(self)

        label_one = QLabel("The conversation history below will be used to generate a reply.")
        label_one.setWordWrap(True)
        major_layout.addWidget(label_one)

        label_two = QLabel("Please do sanitise the conversation before generating.")
        label_two.setWordWrap(True)
        major_layout.addWidget(label_two)

        # label_three = QLabel("Add additional instructions within the boxx at the bottom.")
        # label_three.setWordWrap(True)
        # major_layout.addWidget(label_three)

        self.message_display_window = QScrollArea()
        self.message_display_window.setWidgetResizable(True)
        # allow resize of widgets to fit the qscroll area...

        self.conversation_container = QWidget()

        self.conversation_layout = QVBoxLayout(self.conversation_container)
        self.conversation_layout.setAlignment(Qt.AlignTop)
        # keeps the message widgets grouped at the top...

        self.message_display_window.setWidget(self.conversation_container)
        major_layout.addWidget(self.message_display_window)

        bottom_button_row = QHBoxLayout()
        
        self.sanitise_button = QPushButton("Sanitise and review")
        self.sanitise_button.clicked.connect(self.sanitise_conversation)
        bottom_button_row.addWidget(self.sanitise_button)

        self.generate_button = QPushButton("Generate reply")
        self.generate_button.clicked.connect(self.generate)
        self.generate_button.setEnabled(False)
        self.generate_button.setStyleSheet("QPushButton:disabled { color: #B8B8B8; }")
        bottom_button_row.addWidget(self.generate_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        bottom_button_row.addWidget(cancel_button)

        major_layout.addLayout(bottom_button_row)

        self.render_messages(self.user_messages)

    def render_messages(self, messages_list_of_dicts):

        self.clear_messages()

        messages_list_of_dicts = self.reverse_messages(messages_list_of_dicts)

        for message_dict in messages_list_of_dicts:

            sender_username = message_dict["senderUsername"]
            text = message_dict["messageBody"]

            if type(text) != str:
                text = "[Message contains a non str data type.]"

            if sender_username != users_ebay_username:
                message_attached_name = "Customer"
            else:
                message_attached_name = "You"

            sender_identity = QLabel(message_attached_name)

            message_text_label = QLabel(text)
            message_text_label.setWordWrap(True)
            message_text_label.setMaximumWidth(515)

            message_block_layout = QVBoxLayout()

            message_block_layout.setSpacing(2) # qlabel gap
            message_block_layout.addWidget(sender_identity)
            message_block_layout.addWidget(message_text_label)

            # layout to hold all...
            new_row = QHBoxLayout()

            if sender_username == users_ebay_username:
                sender_identity.setAlignment(Qt.AlignRight)
                # stretch added to push message right as...
                # now the left side is unavailable
                new_row.addStretch()
                new_row.addLayout(message_block_layout)
            else:
                new_row.addLayout(message_block_layout)
                new_row.addStretch() # fills right side


            row_widget = QWidget()
            row_widget.setLayout(new_row)
            # layout must be wrapped in a widget
            # before being added to another layout...
            self.conversation_layout.addWidget(row_widget)

        scrollbar = self.message_display_window.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        # scrollbar set to maximum outside loop

    def clear_messages(self):

        message_count = self.conversation_layout.count()

        while message_count != 0:

            layout_item = self.conversation_layout.takeAt(0)
            # taken from the top, layout items hold a widget

            widget = layout_item.widget()
            widget.deleteLater()

            message_count -= 1

    def reverse_messages(self, messages_list_of_dicts):
        # [{
        #       "senderUsername": "random_username",
        #       "recipientUsername": "random_username",
        #       "messageBody": "message"
        # },]

        reversed_messages = []

        for message_dict in messages_list_of_dicts:

            # dictionary inserted at the 0 index, top
            reversed_messages.insert(0, message_dict)
            
        return reversed_messages          

    def sanitise_conversation(self):

        reversed_user_messages = self.reverse_messages(self.user_messages)

        sanitised_messages = []

        for message_dict in reversed_user_messages:

            sender_username = message_dict["senderUsername"]
            text = message_dict["messageBody"]

            sanitised_message_text = self.user_object.sanitise_text(text)

            sanitised_message = {"senderUsername": sender_username, "messageBody": sanitised_message_text}

            sanitised_messages.append(sanitised_message)

        self.sanitised_messages = sanitised_messages

        text_instruction_to_user = f"Please now conduct a manual review.\nTo ensure all personally identifiable information has been removed."

        QMessageBox.information(self, "Sanitization complete", text_instruction_to_user)

        self.review_dialog = review_dialog(self, self.sanitised_messages)

        self.review_dialog.accepted.connect(self.review_confirmed)
        self.review_dialog.rejected.connect(self.review_cancelled)

        self.sanitise_button.setEnabled(False)
        # ensures sanitise button isnt pressed
        # while the review_dialog is open...
        self.review_dialog.show()

    def review_confirmed(self):
        self.sanitised_messages = self.review_dialog.sanitised_messages

        self.generate_button.setEnabled(True)
        self.sanitise_button.setEnabled(True)

        text_information_for_user = f"You can now generate a reply using the reviewed sanitised conversation."

        QMessageBox.information(self, "Review confirmed", text_information_for_user)

    def review_cancelled(self):
        self.generate_button.setEnabled(False)
        self.sanitise_button.setEnabled(True)

    def generate(self):
        self.hide() # generate_dialog is hidden, but still active...
        # reply_dialog can access the user_object + sanitised_messages

        reply_dialog_window = reply_dialog(self) # parent of reply_dialog

        reply_dialog_running = reply_dialog_window.exec()

        if reply_dialog_running == QDialog.Accepted:

            self.returned_reply = reply_dialog_window.current_generated_reply
            self.accept()
        else:
            self.show() # cancelling reply_dialog will return user here...