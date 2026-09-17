from PySide6.QtWidgets import QWidget, QListWidget, QListWidgetItem, QVBoxLayout, QTextEdit, QHBoxLayout, QMessageBox, QLabel, QPushButton, QDialog
from PySide6.QtGui import QTextBlockFormat, QTextCursor, QTextCharFormat, QBrush, QColor
from PySide6.QtCore import Qt, QTimer

from options_dialog import OPTIONS_DIALOG as options_dialog
from generate_dialog import GENERATE_DIALOG as generate_dialog
from workflow_two_dialog import WORKFLOW_TWO_DIALOG as workflow_two_dialog

from faulted_conversations import permanent_faulted_conversation_ids

from qt_style_sheet import qss_style_sheet
from ebay_client import get_conversations, get_conversation_messages, send_message
from config import user_ebay_account as users_ebay_username
from item_ref_dict import item_reference_dict

class CHAT_WIDGET(QWidget):
    def __init__(self, user_object):
        super().__init__()

        self.user_object = user_object

        self.customer_selected = None
        self.current_conversation_id = None
        self.messages_stored = [] # stored within object
        # as cant be passed as value via signals & slots

        self.excluded_conversation_ids = []
        self.load_permanent_faulted_ids()

        self.setStyleSheet(qss_style_sheet)
        self.setWindowTitle("Project")
        self.setMinimumSize(1025, 600)

        major_layout = QHBoxLayout(self)

        left_layout = QVBoxLayout()
        conversation_label = QLabel("Customer conversations")
        left_layout.addWidget(conversation_label)

        self.conversations_list = QListWidget()
        self.conversations_list.itemClicked.connect(self.conversation_selected)
        left_layout.addWidget(self.conversations_list)

        self.refresh_button = QPushButton("Refresh conversations")
        self.refresh_button.clicked.connect(self.conversations_loaded)
        left_layout.addWidget(self.refresh_button)

        major_layout.addLayout(left_layout, 1)

        right_layout = QVBoxLayout()
        messages_label = QLabel("Conversational messages")
        right_layout.addWidget(messages_label)

        self.message_qtextinput_window = QTextEdit()
        self.message_qtextinput_window.setReadOnly(True)
        right_layout.addWidget(self.message_qtextinput_window, 2)

        reply_label = QLabel("Reply")
        right_layout.addWidget(reply_label)

        self.reply_qtext = QTextEdit()
        right_layout.addWidget(self.reply_qtext, 1)

        button_row = QHBoxLayout()

        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self.open_options)
        button_row.addWidget(self.edit_button)

        self.support_button = QPushButton("Support")
        self.support_button.clicked.connect(self.open_support)
        button_row.addWidget(self.support_button)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_reply)
        button_row.addWidget(self.send_button)

        right_layout.addLayout(button_row)

        major_layout.addLayout(right_layout, 2)

        self.conversations_loaded()
        self.start_timer()

    def start_timer(self):
        self.conversations_refresh = QTimer(self)
        self.conversations_refresh.timeout.connect(self.conversations_loaded)
        # note, refresh causes widget to deselect the current conversation...
        # while messages are still displayed, because theyre within qtextedit

        # refresh conversation list every 10sec
        self.conversations_refresh.start(10000)

    def load_permanent_faulted_ids(self):
        for faulty_id in permanent_faulted_conversation_ids:
        # permanenty faulty_ids appened to instance variable
            
            faulty_id = str(faulty_id)
            self.excluded_conversation_ids.append(faulty_id)

    def display_messages(self, list_of_dicts):
        self.message_qtextinput_window.clear()

        # messages arrive newest at the top of the list
        messages = self.reverse_messages(list_of_dicts)

        current_writing_position = (self.message_qtextinput_window.textCursor())
        # stores current position within the qtextinput window...
        text_colour_highlight = QColor(240, 240, 240)

        for message in messages:
            sender = message["senderUsername"]
            text = message["messageBody"]

            self.create_text_block(sender, text, current_writing_position, text_colour_highlight)

        self.message_qtextinput_window.moveCursor(QTextCursor.End) # moves cursor to end of convo

    def create_text_block(self, sender, message, current_writing_position, colour):

        new_paragraph = QTextBlockFormat()
        #  enables paragraph to be aligned

        if sender == users_ebay_username:
            new_paragraph.setAlignment(Qt.AlignLeft)
        else:
            new_paragraph.setAlignment(Qt.AlignRight)

        current_writing_position.insertBlock(new_paragraph)
        # new block for this text is formatted and coloured
        char_format = QTextCharFormat()
        char_format.setBackground(QBrush(colour))

        final_text = f"{sender}: {message}\n"
        current_writing_position.insertText(final_text, char_format)
        # char_format is applied to the text adding the highlight...

    def reverse_messages(self, list_of_dicts):
        reversed_messages = []

        for dict_data in list_of_dicts:
            reversed_messages.insert(0, dict_data)
            # dict data inserted at the 0 index...

        return reversed_messages

    def conversations_loaded(self):

        list_dicts = get_conversations()

        # then rebuilds the convo list
        self.populate_list(list_dicts)

        # finds the list item, open within conversation window
        current_list_item = self.identify_current_convo_item()

        if current_list_item != None:
            self.conversations_list.setCurrentItem(current_list_item)
            # currently selected conversation, is then re highlighted
        
    def identify_current_convo_item(self):
        if self.current_conversation_id == None:
            return None

        # identifies current user selected item, highlighted
        for index in range(self.conversations_list.count()):

            current_list_item = self.conversations_list.item(index)

            if current_list_item.data(Qt.UserRole) == self.current_conversation_id:
                return current_list_item

        return None

    def populate_list(self, list_dicts):
        # response format via json.dumps
        # obtained via get_conversations
        #
        # "conversations": [
        # {   "conversationId": "122385230201",
        #     "referenceId": "123456789",
        #     "latestMessage": {
        #         "senderUsername": "random_user",
        #         "messageBody": "hi, how are u?"}
        # }

        self.conversations_list.clear()

        for current_dict in list_dicts:

            conversation_id = str(current_dict["conversationId"])

            if conversation_id in self.excluded_conversation_ids:
                continue

            latest_message = current_dict["latestMessage"]
            sender_username = latest_message["senderUsername"]
            recipient_username = latest_message["recipientUsername"]

            if sender_username != users_ebay_username:
                customer_username = sender_username
            else: # identifies customer/business
                customer_username = recipient_username

            if "referenceId" in current_dict:
                reference_id = str(current_dict["referenceId"])
                item_name = item_reference_dict[reference_id]
            else:
                reference_id = "No reference id"
                item_name = "No item could be found"

            message_preview = latest_message["messageBody"].strip()

            if len(message_preview) > 28:
                message_preview = message_preview[:28]
                message_preview += "..."

            item_text = f"Customer: {customer_username}\n"
            item_text += f"Ref: {reference_id} | Message: {message_preview}\n"
            item_text += f"Item: {item_name}"

            # list widget stores text data, to be added to list
            list_conversation_item = QListWidgetItem(item_text)
            # values stored in lists items, userrole + i used as the key
            list_conversation_item.setData(Qt.UserRole, conversation_id)
            list_conversation_item.setData(Qt.UserRole + 1, customer_username)

            self.conversations_list.addItem(list_conversation_item)

    def conversation_selected(self, list_item):
        item_conversation_id = list_item.data(Qt.UserRole)
        item_customer_username = list_item.data(Qt.UserRole + 1)

        self.current_conversation_id = item_conversation_id
        self.customer_selected = item_customer_username

        try:
            python_list = get_conversation_messages(self.current_conversation_id)
            # returns a python list of dictionaries including the values below...
            # "senderUsername": "username",
            # "recipientUsername": "username",
            # "messageBody": "..."
            self.messages_stored = python_list
            self.display_messages(python_list)

        except:

            self.customer_selected = None
            self.messages_stored = []
            self.message_qtextinput_window.clear()

            # current conversation id added to the temporarily excluded id list
            self.excluded_conversation_ids.append(self.current_conversation_id)
            self.current_conversation_id = None

            # new list is then reloaded
            self.conversations_loaded()

            QMessageBox.warning(self, "Error", "This conversation could not be opened.")
            return

    def open_options(self):
        if self.customer_selected == None:
            QMessageBox.warning(self, "Error", "Select a conversation first.")
            return

        dialog = options_dialog(self, self.user_object, self.customer_selected, self.reply_qtext.toPlainText(), self.messages_stored)
        dialog.exec()
        returned_dialog_text = dialog.text_input.toPlainText()
        # toplain required to access python str from qtextedit

        self.reply_qtext.setPlainText(returned_dialog_text)

    def open_support(self):

        if self.customer_selected == None:
            QMessageBox.warning(self, "Error", "Please first select a conversation.")
            return

        if self.user_object.workflow == "Workflow two":

            self.workflow_two_support = workflow_two_dialog(self)
            # avoids multiple convos at the same time with ollama
            self.support_button.setEnabled(False)

            self.workflow_two_support.finished.connect(self.enable_workflow_two_support)
            # signal/slot system requires a method to call, doesnt accept method call...
            self.workflow_two_support.show()
            return

        else:
            ebay_conversation = self.messages_stored
            # conversation updated before its passed
            
            support_dialog = generate_dialog(self, self.user_object, ebay_conversation)
            dialog_outcome = support_dialog.exec()

            if dialog_outcome == QDialog.Accepted:
                self.reply_qtext.setPlainText(support_dialog.returned_reply)
    
    def enable_workflow_two_support(self):
        self.support_button.setEnabled(True)

    def send_reply(self):

        if self.customer_selected == None:
            QMessageBox.warning(self, "Error", "No conversation selected.")
            return

        reply_to_customer = self.reply_qtext.toPlainText().strip()

        if reply_to_customer == "":
            QMessageBox.warning(self, "Error", "Reply cannot be empty.")
            return

        confirmation = QMessageBox.question(self, "Confirmation", "Do you want to send this message?", QMessageBox.Yes | QMessageBox.No)
        if confirmation == QMessageBox.No:
            return

        try:
            send_message(self.current_conversation_id, reply_to_customer)
            QMessageBox.information(self, "Sent", "Reply sent successfully.")

            # reply cleared from box
            self.reply_qtext.clear()

            self.conversations_loaded()

            current_list_item = self.identify_current_convo_item()
            if current_list_item != None:
                # calls for current item to again be selected
                self.conversation_selected(current_list_item)
        except:
            QMessageBox.critical(self, "Error", "Failed to send message.")