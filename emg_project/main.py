from PySide6.QtWidgets import QApplication
from initial_window import INITIAL_WIDGET as initial_widget
from qt_style_sheet import qss_style_sheet
from datastore import create_database
import sys

def main():

    create_database()

    app = QApplication()

    app.setStyleSheet(qss_style_sheet)
    # passes the qss string to qt tree

    widget = initial_widget()
    widget.show()

    app.exec()
    sys.exit()

if __name__ == "__main__":
    main()