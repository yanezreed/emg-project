from PySide6.QtWidgets import QPushButton, QVBoxLayout, QDialog, QWidget, QLabel
from login_dialog import LOGIN_DIALOG as login_dialog
from chat_widget import CHAT_WIDGET as chat_widget
from PySide6.QtCore import Qt

class INITIAL_WIDGET(QWidget):
    def __init__(self):
        super().__init__()

        self.setFixedSize(1025, 600)
        self.setWindowTitle("Project")

        self.chat_widget = None

        major_layout = QVBoxLayout(self)
        major_layout.setAlignment(Qt.AlignCenter)
        # aligns/groups subsequent child object's
        # similar to html box structure

        placeholder = QLabel("Animation placeholder")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("font-size: 40px")
        major_layout.addWidget(placeholder)

        major_layout.addSpacing(35)

        start_button = QPushButton("Start")
    
        # start_button.setFixedWidth(155)...
        major_layout.addWidget(start_button)

        start_button.clicked.connect(self.login)
        start_button.setDefault(True)

    def login(self):
        login_action = login_dialog(self)
        # self is required for stacking..

        result = login_action.exec()

        if result == QDialog.Accepted:
            self.hide()
            
            self.chat_widget = chat_widget(login_action.user_object)
            self.chat_widget.show()

        else:
            self.show() # if login canceled the initial widget shown