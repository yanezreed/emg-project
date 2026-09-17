from PySide6.QtWidgets import QDialog, QMessageBox, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout
from user_class import USER_CLASS as user_class
from workflow_dialog import WORKFLOW_DIALOG as workflow_dialog
from create_account_dialog import CREATE_ACCOUNT_DIALOG as create_account_dialog
from datastore import authenticate_user
from ebay_client import load_tokens, token_expired_check
from oauth_start import OAUTH_START_DIALOG as oauth_start

class LOGIN_DIALOG(QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        self.setWindowTitle("Login")
        self.setFixedSize(420, 200)
        self.setModal(True)

        self.user_object = None

        major_layout = QVBoxLayout(self)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        major_layout.addWidget(self.username)

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)
        # password keyword specifies echomode type...

        major_layout.addWidget(self.password)

        login_button = QPushButton("Login")
        login_button.clicked.connect(self.login)
        # login fails -> user returned to widget

        create_button = QPushButton("Create account")
        create_button.clicked.connect(self.create_account)

        button_row = QHBoxLayout()
        button_row.addWidget(login_button)
        button_row.addWidget(create_button)
        major_layout.addLayout(button_row)


    def create_account(self):
        self.hide()
    
        create_account_object = create_account_dialog(self)
        dialog_result = create_account_object.exec()
        self.show()

        if dialog_result == QDialog.Accepted:
            self.username.setText(create_account_object.username.text())
        else:
            return

    def login(self):
        user = authenticate_user(self.username.text(), self.password.text())

        if user == None:
            QMessageBox.warning(self, "Login failed", "Invalid credentials.")
            return

        self.user_object = user_class(user)

        token_data = load_tokens()

        if token_data == None or token_data == {} or token_expired_check(token_data):
            auth_dialog = oauth_start(self)
            result = auth_dialog.exec()

            if result != QDialog.Accepted:
                self.hide() # hide qdialog
                QMessageBox.warning(self, "eBay Authorisation Required", "Authorisation required before an account can be accessed.")

                self.show()
                return
            
        workflow = workflow_dialog(self.user_object)
        outcome = workflow.exec()

        if outcome == QDialog.Accepted:
            self.accept()