from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt
import webbrowser

class WORKFLOW_DIALOG(QDialog):
    def __init__(self, user_object):
        super().__init__()

        self.setWindowTitle("Workflow selection")
        self.setFixedSize(475, 225)

        major_layout = QVBoxLayout(self)
        major_layout.setAlignment(Qt.AlignCenter)

        row_layout = QHBoxLayout()

        self.workflow_one_button = QPushButton("Workflow one")
        self.workflow_one_button.setFixedSize(186, 30)
        self.workflow_one_button.clicked.connect(self.first_workflow_select)

        self.workflow_one_info = QPushButton("i")
        self.workflow_one_info.setFixedSize(30, 30)
        self.workflow_one_info.clicked.connect(self.first_info_action)

        self.workflow_two_button = QPushButton("Workflow two")
        self.workflow_two_button.setFixedSize(186, 30)
        self.workflow_two_button.clicked.connect(self.second_workflow_select)

        self.workflow_two_info = QPushButton("i")
        self.workflow_two_info.setFixedSize(30, 30)
        self.workflow_two_info.clicked.connect(self.second_info_action)

        workflow_one_layout = QHBoxLayout()
        workflow_one_layout.addWidget(self.workflow_one_button)
        workflow_one_layout.addWidget(self.workflow_one_info)

        workflow_two_layout = QHBoxLayout()
        workflow_two_layout.addWidget(self.workflow_two_button)
        workflow_two_layout.addWidget(self.workflow_two_info)

        row_layout.addLayout(workflow_one_layout)
        row_layout.addLayout(workflow_two_layout)

        major_layout.addLayout(row_layout)

        self.policy_button = QPushButton("Ebay data handling policy")
        self.policy_button.setFixedHeight(36)
        self.policy_button.clicked.connect(self.policy_action)
        major_layout.addWidget(self.policy_button)

        self.user_object = user_object

    def first_workflow_select(self):
        self.user_object.workflow = "Workflow one"
        self.accept() # will close current Qdialog

    def second_workflow_select(self):
        self.user_object.workflow = "Workflow two"
        self.accept()

    def info_dialog(self, title, text):
        lesser_dialog = QDialog(self)
        lesser_dialog.setWindowTitle(title)
        lesser_dialog.setFixedSize(475, 225)

        dialog_layout = QVBoxLayout(lesser_dialog)

        message = QLabel(text)
        message.setWordWrap(True)
        dialog_layout.addWidget(message)

        close_button = QPushButton("Close")
        close_button.clicked.connect(lesser_dialog.accept)
        dialog_layout.addWidget(close_button)

        lesser_dialog.exec()

    def first_info_action(self):
        self.info_dialog("Workflow one", "This workflow offers ai reply generation.\n\n"
            "Customer conversations can be viewed, sanitised and passed to the local ai to generate a baseline reply.\n\n"
            "A manual review is required to ensure that all personal identifiable information has been removed.\n\n"
            "This generated reply can then be edited and sent to the customer.")


    def second_info_action(self):
        self.info_dialog("Workflow two", "This workflow offers an alternative process.\n\n"
            "Customer conversations are not passed to the local ai.\n\n"
            "Instead, the ai can be used to offer business information and responses to frequently asked questions.\n\n"
            "Providing advice/information on how to compose the final response which can then be sent to the customer.")

    def policy_action(self):
        webbrowser.open("https://developer.ebay.com/join/api-license-agreement")