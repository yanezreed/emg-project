from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout, QMessageBox, QPushButton
from PySide6.QtCore import Qt, QTimer
from config import render_url
from ebay_client import save_tokens
import webbrowser
import requests

class OAUTH_START_DIALOG(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.setWindowTitle("Ebay authorisation")
        self.setFixedSize(420, 200)
        self.setModal(True)

        self.connect_attempts = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.request_server)
        # `timeout` singal enabled by `QTimer` class...
        # `.timer` called within `start_oauth` ie. `timer.start(2000)`
        
        major_layout = QVBoxLayout(self)
        major_layout.setAlignment(Qt.AlignCenter)

        self.label = QLabel("Below you will be able to authorise this app using your ebay account.\n")

        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)
        major_layout.addWidget(self.label)

        self.connect_button = QPushButton("Connect ebay account")
        self.connect_button.clicked.connect(self.start_oauth)
        major_layout.addWidget(self.connect_button)

    def start_oauth(self):
        webbrowser.open(f"{render_url}/start")
        self.connect_attempts = 0

        # self.lesser_dialog = QDialog(self)
        # self.lesser_dialog.setWindowTitle("eBay Authorisation")
        # self.lesser_dialog.setFixedSize(300, 150)
        # self.lesser_dialog.setModal(True)

        # lesser_layout = QVBoxLayout(self.lesser_dialog)
        # lesser_layout.setAlignment(Qt.AlignCenter)

        # text_label = QLabel("Please complete the process in your browser.")
        # text_label.setAlignment(Qt.AlignCenter)
        # text_label.setWordWrap(True)
        # lesser_layout.addWidget(text_label)

        # cancel_button = QPushButton("Cancel")
        # cancel_button.clicked.connect(self.cancel_process)
        # lesser_layout.addWidget(cancel_button)

        self.timer.start(2000) # timer triggers `request_server` every two seconds...
        self.label.setText("Continue to your browser to complete the login process.")
        self.connect_button.hide()

    def request_server(self):
        self.connect_attempts += 1

        if self.connect_attempts > 30:

            self.timer.stop()

            # self.lesser_dialog.reject()

            QMessageBox.warning(self, "Process timed out", "Authorisation process timed out.")

            self.reject()

            return

        try:
            server_response = requests.get(f"{render_url}/check_token", timeout = 10)
            # calls `/check-token` within flask server
            # if a valid token exists, token data is returned as json, via a http response

            if server_response.status_code != 200:
            # catches the 202 status code response
                return
            
            response_data = server_response.json()

            save_tokens({
                "access_token": response_data["access_token"],
                "expires_in": response_data["expires_in"],
                "received_at": response_data["received_at"]
            })

            self.timer.stop()
            
            # self.lesser_dialog.accept()
            self.accept()
            return

        except:
            return

    def cancel_process(self):
        self.timer.stop()
        self.lesser_dialog.reject()
        # user returned to login...