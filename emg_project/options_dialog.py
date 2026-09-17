from PySide6.QtWidgets import QDialog, QPushButton, QMessageBox, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit

class OPTIONS_DIALOG(QDialog):
    def __init__(self, parent_window, user_object, customer, initial_text, messages):
        super().__init__(parent_window)

        self.user_object = user_object
        self.customer = customer
        self.original_text = initial_text

        if messages == None:
            self.messages = []
        else:
            self.messages = messages

        self.setWindowTitle("Support window")
        self.setModal(True)
        self.setMinimumSize(700, 450)

        major_layout = QVBoxLayout(self)
        major_layout.addWidget(QLabel("Support reply text"))

        toolbar_layout = QHBoxLayout()

        undo_button = QPushButton("Undo")
        toolbar_layout.addWidget(undo_button)

        redo_button = QPushButton("Redo")
        toolbar_layout.addWidget(redo_button)

        cut_button = QPushButton("Cut")
        toolbar_layout.addWidget(cut_button)

        copy_button = QPushButton("Copy")
        toolbar_layout.addWidget(copy_button)

        paste_button = QPushButton("Paste")
        toolbar_layout.addWidget(paste_button)

        select_all_button = QPushButton("Select All")
        toolbar_layout.addWidget(select_all_button)

        clear_button = QPushButton("Clear")
        toolbar_layout.addWidget(clear_button)

        self.text_input = QTextEdit()
        self.text_input.setPlainText(initial_text)
        major_layout.addWidget(self.text_input)

        undo_button.clicked.connect(self.text_input.undo)
        redo_button.clicked.connect(self.text_input.redo)
        cut_button.clicked.connect(self.text_input.cut)
        copy_button.clicked.connect(self.text_input.copy)
        paste_button.clicked.connect(self.text_input.paste)
        select_all_button.clicked.connect(self.text_input.selectAll)
        clear_button.clicked.connect(self.clear_text)

        major_layout.addLayout(toolbar_layout)

        button_bar = QHBoxLayout()

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.cancel_edit)
        button_bar.addWidget(cancel_button, 1)

        spell_check_button = QPushButton("-")
        spell_check_button.clicked.connect(self.spell_check)
        spell_check_button.setEnabled(False) # disabled
        button_bar.addWidget(spell_check_button, 1)

        continue_button = QPushButton("Continue")
        continue_button.clicked.connect(self.accept)
        button_bar.addWidget(continue_button, 1)

        major_layout.addLayout(button_bar)

    def clear_text(self):

        user_decision = QMessageBox.question(self, "Clear Text", "Are you sure you want to clear reply text?", QMessageBox.Yes | QMessageBox.No)

        if user_decision == QMessageBox.Yes:
            self.text_input.clear()

    def cancel_edit(self):

        # chat_widget reads text_input after this dialog closes, so restoring
        # the original value ensures Cancel does not apply any changes...
        self.text_input.setPlainText(self.original_text)
        self.reject()

    def spell_check(self):
    # Need to implement...
        return