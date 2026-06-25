import sys

from PyQt5.QtWidgets import QApplication

from src.database import initialize_database
from src.ui import Log_In_Window


def main():
    initialize_database()
    app = QApplication(sys.argv)
    window = Log_In_Window()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
