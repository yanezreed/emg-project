from PySide6.QtWidgets import QMessageBox, QDialog, QPushButton, QLineEdit, QVBoxLayout
from datastore import create_user

class CREATE_ACCOUNT_DIALOG(QDialog):
    def __init__(self, parent_qdialog):
        super().__init__(parent_qdialog)

        self.setWindowTitle("Create account")
        self.setFixedSize(475, 225)
        self.setModal(True)

        major_layout = QVBoxLayout(self)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)

        self.confirm_password = QLineEdit()
        self.confirm_password.setPlaceholderText("Confirm password")
        self.confirm_password.setEchoMode(QLineEdit.Password)

        create_button = QPushButton("Create account")
        create_button.clicked.connect(self.create_account)

        major_layout.addStretch()
        major_layout.addWidget(self.username)
        major_layout.addSpacing(10)
        major_layout.addWidget(self.password)
        major_layout.addSpacing(10)
        major_layout.addWidget(self.confirm_password)
        major_layout.addSpacing(16)
        major_layout.addWidget(create_button)
        major_layout.addStretch()

    def create_account(self):
        username = self.username.text().strip()
        password = self.password.text()
        confirm = self.confirm_password.text()

        if username == "" or password == "":
            QMessageBox.warning(self, "Error", "Every field requires a value.")
            return

        if password != confirm:
            QMessageBox.warning(self, "Error", "Passwords do not match.")
            return

        success = create_user(username, password)
        if success == False:
            QMessageBox.warning(self, "Error", "Username already exists.")
            return
        else:
            QMessageBox.information(self, "Success", "Account created.")
            self.accept()
