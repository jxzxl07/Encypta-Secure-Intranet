from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget

from ..config import SERVER_IP, asset_path


class GUI_Window(QMainWindow): # Defines a custom GUI window class which uses PyQT to inherit from.
    def __init__(self, title="Encrypta Secure Intranet"): # Constructor method initialises the window.
        super().__init__() # Calls the parent class contructor to set up the base functions.

        # Sets the title of the window to the value passed as an argument (defaults to it).                              
        self.setWindowTitle(title)

        # Set the minimum size of the window. 
        self.setMinimumSize(1000, 600)

        # Create a main container for the window's components here and set it.
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Create a vertical box layout for organising widgets in columns.
        self.layout = QVBoxLayout(self.central_widget)

        # Sets the icon of the window.
        self.setWindowIcon(QIcon(asset_path("icon.png")))


class ConnectionHandler(QObject):
    # Update the signal to include sender_ip
    connection_request_received = pyqtSignal(str, str, object, str)  
    # username, public_key, client_socket, sender_ip
    connection_accepted = pyqtSignal(str, str, str)  
    # username, public_key
    connection_rejected = pyqtSignal(str) 
     # username
    connection_error = pyqtSignal(str)  
    # error message

# Change this with the ENCRYPTA_SERVER_IP environment variable.
server_ip = SERVER_IP
