from .common import *
from .base import GUI_Window
from ..crypto.encryption import AsymmetricEncryption, SymmetricEncryption
from ..utils.helpers import get_ip_address


class Direct_Messages_Window(GUI_Window):
    # Constructor method initialises the window.
    def __init__(self, username):
        super().__init__(title="Encrypta - Direct Messages")
        self.username = username
        self.encryption = AsymmetricEncryption()
        self.init_ui()
        self.showMaximized()
        
    def init_ui(self):
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header with back button
        header = QWidget()
        header.setStyleSheet("background-color: #f8f9fa;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        self.back_button = QPushButton("Back")
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-size: 20px;
                font-weight: 600;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
        """)
        header_layout.addWidget(self.back_button, alignment=Qt.AlignLeft)
        header_layout.addStretch()
        self.back_button.clicked.connect(self.back)
        main_layout.addWidget(header)
        
        # Main content container
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setSpacing(0)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Left image panel
        left_panel = QWidget()
        left_panel.setStyleSheet("background-color: #f8f9fa;")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(25, 25, 25, 25)
        
        left_image = QLabel()
        left_pixmap = QPixmap(asset_path("group.png"))
        left_scaled = left_pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        left_image.setPixmap(left_scaled)
        left_image.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(left_image, alignment=Qt.AlignCenter)
        
        # Center panel - Direct Messages
        center_panel = QWidget()
        center_panel.setStyleSheet("""
            QWidget {
                background-color: white;
                border-left: 1px solid #e9ecef;
                border-right: 1px solid #e9ecef;
            }
        """)
        center_layout = QVBoxLayout(center_panel)
        center_layout.setContentsMargins(20, 20, 20, 20)
        center_layout.setSpacing(15)
        
        dm_header = QLabel("Direct Messages")
        dm_header.setStyleSheet("""
            QLabel {
                font-size: 40px;
                font-weight: bold;
                color: #212529;
                padding-bottom: 5px;
            }
        """)
        dm_header.setAlignment(Qt.AlignCenter)
        center_layout.addWidget(dm_header)

        # DM list with enhanced styling
        self.dm_list = QListWidget()
        self.dm_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #e9ecef;
                border-radius: 8px;
                background-color: white;
                padding: 5px;
            }
            QListWidget::item {
                padding: 12px 15px;
                border-bottom: 1px solid #f1f3f5;
                border-radius: 4px;
            }
            QListWidget::item:hover {
                background-color: #f8f9fa;
            }
            QListWidget::item:selected {
                background-color: #e9ecef;
                color: #212529;
            }
        """)


        # increase font size of the list items
        font = self.dm_list.font()
        font.setPointSize(24)
        self.dm_list.setFont(font)


        center_layout.addWidget(self.dm_list)
        self.dm_list.itemDoubleClicked.connect(self.open_direct_message)
        
        # Right image panel
        right_panel = QWidget()
        right_panel.setStyleSheet("background-color: #f8f9fa;")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(25, 25, 25, 25)
        
        right_image = QLabel()
        right_pixmap = QPixmap(asset_path("group.png"))
        right_scaled = right_pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        right_image.setPixmap(right_scaled)
        right_image.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(right_image, alignment=Qt.AlignCenter)
        
        # Set panel sizes and policies
        left_panel.setMinimumWidth(300)
        center_panel.setMinimumWidth(400)
        right_panel.setMinimumWidth(300)
        
        left_panel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        center_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_panel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        # Add panels to content layout
        content_layout.addWidget(left_panel)
        content_layout.addWidget(center_panel)
        content_layout.addWidget(right_panel)
        
        # Add content to main layout
        main_layout.addWidget(content_widget)
        
        # Load user connections
        self.load_connections()




    def load_connections(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Get current user's ID from the database
            cursor.execute("SELECT user_id FROM User WHERE username = ?", (self.username,))
            user_id = cursor.fetchone()[0]
            
            # Get all connected users except the current user
            cursor.execute("""
                SELECT u.username 
                FROM Connection c
                JOIN User u ON (c.receiver_id = u.user_id OR c.sender_id = u.user_id)
                WHERE (c.sender_id = ? OR c.receiver_id = ?)
                AND c.status = 'connected'
                AND u.username != ?
                ORDER BY u.username
            """, (user_id, user_id, self.username))

            connections = cursor.fetchall()

            # Clear existing items
            self.dm_list.clear()

            # Add items to the list
            for connection in connections:
                username = connection[0]
                item = QListWidgetItem(username)
                item.setToolTip(f"Double click to chat with {username}")
                self.dm_list.addItem(item)
            # Add placeholder if no connections    
            if self.dm_list.count() == 0:
                placeholder = QListWidgetItem("No connections yet")
                placeholder.setFlags(placeholder.flags() & ~Qt.ItemIsEnabled)
                self.dm_list.addItem(placeholder)
        # Error handling         
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to load connections: {str(e)}")
            print(f"Database error details: {str(e)}")  # For debugging
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            print(f"Error details: {str(e)}")  # For debugging
        finally:
            if conn:
                conn.close()


    def open_direct_message(self, item):
        """Open direct message window when connection is double-clicked"""
        selected_username = item.text()
        if selected_username != "No connections yet":
            self.dm_window = DirectMessage(self.username, selected_username)
            self.dm_window.show()
            self.close()

    def back(self):
        from .dashboard import Main_Menu_Window

        self.redirect = Main_Menu_Window(self.username)
        self.redirect.show()
        self.close()






class DirectMessage(GUI_Window):
    message_received = pyqtSignal(str, str, str, bool)
    # sender, filename, timestamp, file_data, is_sender
    file_received = pyqtSignal(str, str, str, str, bool)  

    def __init__(self, username, connection_username):
        super().__init__()
        self.setWindowTitle(f"Chat with {connection_username}")

        # Store attributes
        self.message_received.connect(self.display_message)
        self.file_received.connect(self.display_file)
        self.username = username
        self.connection = connection_username
        self.encryption = AsymmetricEncryption()
        self.message_port = DIRECT_MESSAGE_PORT
        self.file_port = DIRECT_FILE_PORT
        self.is_listening = False
        self._file_cache = {}

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.init_ui()
        
        # Connect loadFinished signal to load messages and files
        self.chat_area.loadFinished.connect(self.on_web_view_loaded)
        
        self.start_message_server()
        self.start_file_server()
        self.showMaximized()

    
    def on_web_view_loaded(self, ok):
        # Load messages and files only after web view is ready
        if ok:
            # Load messages and files only after web view is ready
            self.load_messages()
            self.load_files()


    # GUI setup method
    def init_ui(self):
        # Top bar
        top_bar = QWidget()
        top_bar.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                stop:0 #2c3e50, stop:1 #3498db);
                color: white;
            }
        """)
        top_bar.setFixedHeight(60)
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(15, 0, 15, 0)

        # # Back button
        back_button = QPushButton("← Back")
        back_button.setStyleSheet("""
            QPushButton {
                color: white;
                border: none;
                padding: 8px 15px;
                font-size: 14px;
                font-weight: bold;
                background: transparent;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 5px;
            }
        """)
        back_button.clicked.connect(self.back)
        top_layout.addWidget(back_button)

        # Chat title
        title_label = QLabel(f"Chat with {self.connection}")
        title_label.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        top_layout.addWidget(title_label)
        top_layout.addStretch()

        self.main_layout.addWidget(top_bar)

        # Chat area
        chat_container = QWidget()
        chat_container.setStyleSheet("background-color: #f0f2f5;")
        chat_layout = QVBoxLayout(chat_container)
        chat_layout.setContentsMargins(20, 20, 20, 20)

        # Chat area (QWebEngineView) for displaying messages and files
        self.chat_area = QWebEngineView()
        self.chat_area.setStyleSheet("""
            QWebEngineView {
                border: none;
                border-radius: 10px;
                background-color: #f0f2f5;
            }
        """)

        # Create a bridge object to handle file downloads
        class Bridge(QObject):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.parent = parent
            # Method to download file
            @pyqtSlot(str)
            def downloadFile(self, file_id):
                self.parent.save_file(file_id)
        # Register the bridge object with the web view
        self.bridge = Bridge(self)
        self.channel = QWebChannel()
        self.channel.registerObject('bridge', self.bridge)
        self.chat_area.page().setWebChannel(self.channel)

        # Initialise HTML content
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
            <style>
                body { 
                    background-color: #f0f2f5;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    margin: 20px;
                }
                #chat-content {
                    width: 100%;
                }
            </style>
            <script>
                let bridge;
                document.addEventListener('DOMContentLoaded', function() {
                    new QWebChannel(qt.webChannelTransport, function(channel) {
                        bridge = channel.objects.bridge;
                        window.downloadFile = function(fileId) {
                            bridge.downloadFile(fileId);
                        };
                    });
                });
            </script>
        </head>
        <body>
            <div id="chat-content"></div>
        </body>
        </html>
        """
        # Set the HTML content to the web view
        self.chat_area.setHtml(html_content)
        chat_layout.addWidget(self.chat_area)
        # Add the chat area to the main layout
        self.main_layout.addWidget(chat_container, stretch=1)

        # Bottom input area
        bottom_container = QWidget()
        bottom_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border-top: 1px solid #e0e0e0;
            }
        """)
        bottom_layout = QHBoxLayout(bottom_container)
        bottom_layout.setContentsMargins(20, 15, 20, 15)

        # File button
        self.file_button = QPushButton("📎")
        self.file_button.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                color: #2980b9;
                border: 2px solid #e0e0e0;
                border-radius: 20px;
                padding: 12px 20px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        self.file_button.clicked.connect(self.select_file)
        bottom_layout.addWidget(self.file_button)

        # Message input
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type your message...")
        self.message_input.returnPressed.connect(self.send_message)
        self.message_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e0e0e0;
                border-radius: 20px;
                padding: 12px 25px;
                font-size: 16px;
                background-color: #f8f9fa;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                background-color: white;
            }
        """)
        bottom_layout.addWidget(self.message_input)

        # Send button
        self.send_button = QPushButton("Send")
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #2980b9;
                color: white;
                border: none;
                border-radius: 20px;
                padding: 12px 30px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
        """)
        self.send_button.clicked.connect(self.send_message)
        bottom_layout.addWidget(self.send_button)

        self.main_layout.addWidget(bottom_container)




    def start_message_server(self):
        # Initialize and start message server 
        try:
            # Create a socket and start listening for incoming messages
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('', self.message_port))
            self.server_socket.listen(5)
            self.server_socket.settimeout(1)
            # Start listening thread
            self.is_listening = True
            self.server_thread = threading.Thread(target=self.listen_for_messages)
            self.server_thread.daemon = True
            self.server_thread.start()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start message server: {str(e)}")


    # Method to load messages from the database
    def listen_for_messages(self):
        # Listen for incoming messages
        while self.is_listening:
            client = None
            try:
                # Accept incoming connection
                client, addr = self.server_socket.accept()
                client.settimeout(5)  # 5 second timeout
                data = client.recv(4096)
                if data:
                    message = json.loads(data.decode())
                    # Get private key and decrypt
                    private_key = self._get_private_key()
                    decrypted = self.encryption.decrypt(message['content'], private_key)
                    
                    # Update UI in thread-safe way
                    QMetaObject.invokeMethod(self, "display_message",
                    # Use Qt.QueuedConnection to ensure thread safety
                                           Qt.QueuedConnection,
                                           Q_ARG(str, message['sender']),
                                           Q_ARG(str, decrypted),
                                           Q_ARG(str, message['timestamp']),
                                           Q_ARG(bool, False))
            # Handle exceptions
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Error receiving message: {e}")
            finally:
                if client:
                    try:
                        client.shutdown(socket.SHUT_RDWR)
                    except:
                        pass
                    client.close()

    # Method to get private key from the database
    def _get_private_key(self):
        conn = None
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT private_key 
                FROM User 
                WHERE username = ?
            """, (self.username,))
            # Get private key from the database
            result = cursor.fetchone()
            if not result:
                raise Exception(f"No private key found for user {self.username}")
                
            private_key_str = result[0]
            # Note: Parse as (d, n) to match encryption class expectations
            d, n = map(int, private_key_str.split(','))
            return (d, n)
        finally:
            if conn:
                conn.close()

    # Method to display messages in the chat area
    def send_message(self):
        content = self.message_input.text().strip()
        if not content:
            QMessageBox.warning(self, "Error", "Message cannot be empty")
            return
        # Send message to the recipient
        conn = None
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # Get recipient's IP address first
            cursor.execute("""
                SELECT connection_ip_address 
                FROM Connection 
                WHERE username = ?
            """, (self.connection,))
            ip_result = cursor.fetchone()
            if not ip_result:
                raise Exception("Recipient connection not found")
            ip = ip_result[0]

            # Check if recipient's server is online
            if not self.check_server_online(ip, self.message_port):
                QMessageBox.warning(
                    self, 
                    "User Offline",
                    f"{self.connection} is currently offline. Please try again later."
                )
                return

            # Get recipient's public key
            cursor.execute("""
                SELECT public_key, user_id FROM User 
                WHERE username = ?
            """, (self.connection,))
            result = cursor.fetchone()
            # Check if recipient exists
            if not result:
                raise Exception("Recipient not found")
            # Parse public key and user ID
            public_key_str, receiver_id = result
            e, n = map(int, public_key_str.split(','))
            public_key = (e, n)

            # Get sender's user_id
            cursor.execute("SELECT user_id FROM User WHERE username = ?", 
                        (self.username,))
            sender_id = cursor.fetchone()[0]

            # Encrypt message
            encrypted_list = self.encryption.encrypt(content, public_key)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Prepare message packet
            message = {
                'sender': self.username,
                'content': encrypted_list,
                'timestamp': timestamp
            }

            # Send message via socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                client.settimeout(5)
                client.connect((ip, self.message_port))
                client.send(json.dumps(message).encode())

            # Store in database with both encrypted and plain content
            cursor.execute("""
                INSERT INTO Messages 
                (sender_id, receiver_id, content, plain_content, timestamp) 
                VALUES (?, ?, ?, ?, ?)
            """, (sender_id, receiver_id, json.dumps(encrypted_list), content, timestamp))
            conn.commit()

            # Update UI
            self.display_message(self.username, content, timestamp, True)
            self.message_input.clear()

        # Handle exceptions
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to send message: {str(e)}")
        finally:
            if conn:
                conn.close()

                
    def listen_for_messages(self):
        # Listen for incoming messages
        while self.is_listening:
            try:
                # Accept incoming connection
                client, _ = self.server_socket.accept()
                client.settimeout(5)
                # Receive message
                data = client.recv(4096)
                if data:
                    message = json.loads(data.decode())
                    
                    # Get private key for decryption
                    private_key = self._get_private_key()
                    
                    # Get encrypted content and ensure it's a list
                    encrypted_list = message['content']
                    if isinstance(encrypted_list, str):
                        encrypted_list = json.loads(encrypted_list)
                    
                    # Decrypt the message
                    decrypted = self.encryption.decrypt(encrypted_list, private_key)
                    
                    # Save to database
                    with sqlite3.connect(DB_PATH) as conn:
                        cursor = conn.cursor()
                        
                        # Get user IDs
                        cursor.execute("SELECT user_id FROM User WHERE username = ?", 
                                     (message['sender'],))
                        sender_id = cursor.fetchone()[0]
                        cursor.execute("SELECT user_id FROM User WHERE username = ?", 
                                     (self.username,))
                        receiver_id = cursor.fetchone()[0]
                        
                        # Store message
                        cursor.execute("""
                            INSERT INTO Messages 
                            (sender_id, receiver_id, content, timestamp)
                            VALUES (?, ?, ?, ?)
                        """, (sender_id, receiver_id, json.dumps(encrypted_list), 
                             message['timestamp']))
                        conn.commit()
                    
                    # Update UI
                    self.message_received.emit(
                        message['sender'],
                        decrypted,
                        message['timestamp'],
                        False
                    )
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Error in listen_for_messages: {str(e)}")
            finally:
                if 'client' in locals():
                    try:
                        client.close()
                    except:
                        pass



    def load_messages(self):
        # Load messages from the database
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                # Get messages between the current user and the connection
                cursor.execute("""
                    SELECT m.content, m.plain_content, m.timestamp, u.username, m.sender_id
                    FROM Messages m
                    JOIN User u ON m.sender_id = u.user_id
                    WHERE (m.sender_id = (SELECT user_id FROM User WHERE username = ?)
                    AND m.receiver_id = (SELECT user_id FROM User WHERE username = ?))
                    OR (m.sender_id = (SELECT user_id FROM User WHERE username = ?)
                    AND m.receiver_id = (SELECT user_id FROM User WHERE username = ?))
                    ORDER BY m.timestamp ASC
                """, (self.username, self.connection, self.connection, self.username))
                # Fetch all messages
                messages = cursor.fetchall()
                private_key = self._get_private_key()
                # Display messages
                for content, plain_content, timestamp, username, sender_id in messages:
                    is_sender = username == self.username
                    
                    if is_sender:
                        # Use plain content for messages we sent
                        display_content = plain_content
                    else:
                        # Decrypt received messages
                        try:
                            encrypted_list = json.loads(content)
                            display_content = self.encryption.decrypt(encrypted_list, private_key)
                        except Exception as e:
                            display_content = f"[Unable to decrypt message: {str(e)}]"
                    
                    self.display_message(username, display_content, timestamp, is_sender)
        # Error handling
        except Exception as e:
            print(f"Error loading messages: {str(e)}")
            QMessageBox.warning(self, "Warning", 
                              "Some messages could not be loaded properly.")




    def display_message(self, username, content, timestamp, is_sender):
        dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        formatted_time = dt.strftime("%I:%M %p")
        formatted_date = dt.strftime("%B %d, %Y")
        
        message_html = f"""
            <div style="
                margin: 35px 0; 
                display: flex;
                flex-direction: column;
                clear: both;
                float: {'right' if is_sender else 'left'};
                max-width: 70%;
            ">
                <div style="
                    display: flex;
                    justify-content: space-between;
                    align-items: baseline;
                    margin-bottom: 12px;
                ">
                    <span style="font-size: 16px; color: #444; font-weight: bold;">
                        {username}
                    </span>
                    <span style="font-size: 14px; color: #777; margin-left: 15px;">
                        {formatted_time} • {formatted_date}
                    </span>
                </div>
                <div style="
                    background-color: {'#dcf8c6' if is_sender else '#fff'};
                    padding: 25px;
                    border-radius: 16px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                    border: 1px solid {'#c5e9b4' if is_sender else '#e5e5e5'};
                    font-size: 18px;
                    line-height: 1.6;
                    word-wrap: break-word;
                ">
                    {content}
                </div>
            </div>
        """
        
        script = f"""
            var content = document.getElementById('chat-content');
            if (content) {{
                content.insertAdjacentHTML('beforeend', `{message_html}`);
                window.scrollTo(0, document.body.scrollHeight);
            }}
        """
        self.chat_area.page().runJavaScript(script)


    # Method to handle back button click
    def back(self):
        try:
            # First stop the listening thread and close socket
            self.is_listening = False
            # Close existing client connections first
            if hasattr(self, 'server_socket'):
                try:
                    # Create a final connection to unblock accept()
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        try:
                            s.connect(('localhost', self.message_port))
                        except:
                            pass
                    # Now close the server socket
                    self.server_socket.close()
                except:
                    pass
            
            # Wait for thread to finish
            if hasattr(self, 'server_thread'):
                self.server_thread.join(timeout=1)
            
            # Create new window and show it
            self.redirect = Direct_Messages_Window(self.username)
            self.redirect.show()
            self.close()

        # Error handling
        except Exception as e:
            print(f"Back button error: {e}")
            QMessageBox.critical(self, "Error", f"Error returning to messages: {str(e)}")

    def closeEvent(self, event):
        """Clean up servers on window close"""
        self.is_listening = False
        if hasattr(self, 'server_socket'):
            self.server_socket.close()
        if hasattr(self, 'file_socket'):
            self.file_socket.close()
        super().closeEvent(event)

    # Method to check if a server is online    
    def check_server_online(self, ip, port, timeout=2):
        try:
            # Check if server is online
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                result = sock.connect_ex((ip, port))
                return result == 0
        except:
            return False




    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", "All Files (*.*)")
        
        if file_path:
            self.send_file(file_path)




    def send_file(self, file_path):
        try:
            # Read file data
            with open(file_path, 'rb') as file:
                file_data = file.read()
            
            # Get filename
            filename = os.path.basename(file_path)
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # Get sender's user_id
            cursor.execute("SELECT user_id FROM User WHERE username = ?", (self.username,))
            sender_id = cursor.fetchone()[0]

            # Get recipient's IP and public key
            cursor.execute("""
                SELECT C.connection_ip_address, U.public_key, U.user_id 
                FROM Connection C
                JOIN User U ON U.username = C.username
                WHERE C.username = ?
            """, (self.connection,))
            
            result = cursor.fetchone()
            if not result:
                raise Exception("Recipient not found")
            
            ip, public_key_str, receiver_id = result
            e, n = map(int, public_key_str.split(','))
            public_key = (e, n)

            # Check if recipient is online
            if not self.check_server_online(ip, self.file_port):
                QMessageBox.warning(
                    self, 
                    "User Offline",
                    f"{self.connection} is currently offline. Please try again later."
                )
                return

            # Convert file data to base64 for encryption
            file_data_b64 = base64.b64encode(file_data).decode('utf-8')
            
            # Encrypt file data
            encrypted_data = self.encryption.encrypt(file_data_b64, public_key)
            
            # Prepare file packet
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file_packet = {
                'sender': self.username,
                'filename': filename,
                'content': encrypted_data,
                'timestamp': timestamp,
                'type': 'file'
            }

            # Send file via socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                client.settimeout(30)  # Longer timeout for files
                client.connect((ip, self.file_port))
                client.send(json.dumps(file_packet).encode())

            # Store in Files table
            cursor.execute("""
                INSERT INTO Files 
                (sender_id, receiver_id, filename, content, timestamp) 
                VALUES (?, ?, ?, ?, ?)
            """, (
                sender_id,
                receiver_id,
                filename,
                json.dumps(encrypted_data),  # Encrypted content as JSON string
                timestamp
            ))
            conn.commit()

            # Display file in chat
            self.display_file(self.username, filename, timestamp, file_data_b64, True)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to send file: {str(e)}")
        finally:
            if conn:
                conn.close()




    def start_file_server(self):
        # Start file server
        try:
            # Create a socket and start listening for incoming files
            self.file_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.file_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.file_socket.bind(('', self.file_port))
            self.file_socket.listen(5)
            self.file_socket.settimeout(1)
            # Start listening thread
            self.file_thread = threading.Thread(target=self.listen_for_files)
            self.file_thread.daemon = True
            self.file_thread.start()
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start file server: {str(e)}")



    def listen_for_files(self):
        # Listen for incoming files
        while self.is_listening:
            try:
                # Accept incoming connection
                client, _ = self.file_socket.accept()
                client.settimeout(30)  # Longer timeout for files
                # Receive file data
                data = b""
                while True:
                    chunk = client.recv(8192)
                    if not chunk:
                        break
                    data += chunk
                # Parse file packet
                if data:
                    file_packet = json.loads(data.decode())
                    
                    # Get private key
                    private_key = self._get_private_key()
                    
                    # Decrypt file data
                    encrypted_data = file_packet['content']
                    if isinstance(encrypted_data, str):
                        encrypted_data = json.loads(encrypted_data)
                    # Decrypt file data
                    decrypted_data = self.encryption.decrypt(encrypted_data, private_key)
                    
                    # Store in database
                    with sqlite3.connect(DB_PATH) as conn:
                        cursor = conn.cursor()
                        
                        # Get user IDs
                        cursor.execute("SELECT user_id FROM User WHERE username = ?", 
                                    (file_packet['sender'],))
                        sender_id = cursor.fetchone()[0]
                        # Get receiver IDD
                        cursor.execute("SELECT user_id FROM User WHERE username = ?", 
                                    (self.username,))
                        receiver_id = cursor.fetchone()[0]
                        
                        # Insert into Files table
                        cursor.execute("""
                            INSERT INTO Files 
                            (sender_id, receiver_id, filename, content, timestamp)
                            VALUES (?, ?, ?, ?, ?)
                        """, (
                            sender_id,
                            receiver_id,
                            file_packet['filename'],
                            json.dumps(encrypted_data),  # Store encrypted content
                            file_packet['timestamp']
                        ))
                        
                        conn.commit()

                    # Emit signal to update UI
                    self.file_received.emit(
                        file_packet['sender'],
                        file_packet['filename'],
                        file_packet['timestamp'],
                        decrypted_data,
                        False
                    )

            except socket.timeout:
                continue
            except Exception as e:
                print(f"Error receiving file: {e}")
            finally:
                if 'client' in locals():
                    client.close()

    def display_file(self, username, filename, timestamp, file_data, is_sender):
        dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        formatted_time = dt.strftime("%I:%M %p")
        formatted_date = dt.strftime("%B %d, %Y")

        file_id = f"file_{timestamp.replace(' ', '_')}_{filename}"
        self._file_cache[file_id] = file_data

        message_html = f"""
            <div style="
                margin: 35px 0; 
                display: flex;
                flex-direction: column;
                clear: both;
                float: {'right' if is_sender else 'left'};
                max-width: 70%;
            ">
                <div style="
                    display: flex;
                    justify-content: space-between;
                    align-items: baseline;
                    margin-bottom: 12px;
                ">
                    <span style="font-size: 16px; color: #444; font-weight: bold;">
                        {username}
                    </span>
                    <span style="font-size: 14px; color: #777; margin-left: 15px;">
                        {formatted_time} • {formatted_date}
                    </span>
                </div>
                <div style="
                    background-color: {'#dcf8c6' if is_sender else '#fff'};
                    padding: 25px;
                    border-radius: 16px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                    border: 1px solid {'#c5e9b4' if is_sender else '#e5e5e5'};
                ">
                    <div style="
                        display: flex;
                        align-items: center;
                    ">
                        <span>📎 {filename}</span>
                        <button 
                            onclick="downloadFile('{file_id}')"
                            style="
                                background-color: #2980b9;
                                color: white;
                                padding: 5px 15px;
                                border-radius: 15px;
                                margin-left: 15px;
                                font-size: 14px;
                                border: none;
                                cursor: pointer;
                            "
                        >
                            Download
                        </button>
                    </div>
                </div>
            </div>
        """
        
        script = f"""
            var content = document.getElementById('chat-content');
            if (content) {{
                content.insertAdjacentHTML('beforeend', `{message_html}`);
                window.scrollTo(0, document.body.scrollHeight);
            }}
        """
        self.chat_area.page().runJavaScript(script)





    def save_file(self, file_id):
        # Save file to disk
        if file_id not in self._file_cache:
            QMessageBox.warning(self, "Error", "File data not found")
            return
        # Get file data from cache
        file_data = self._file_cache[file_id]
        filename = file_id.split('_')[-1]

        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save File", filename, "All Files (*.*)")
        # Save file to disk
        if save_path:
            try:
                file_bytes = base64.b64decode(file_data)
                with open(save_path, 'wb') as f:
                    f.write(file_bytes)
                QMessageBox.information(self, "Success", "File downloaded successfully")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")





    def load_files(self):
        # Load files from the database
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                
                # Get all files between current user and connection
                cursor.execute("""
                    SELECT F.content, F.timestamp, U.username, F.sender_id, F.filename
                    FROM Files F
                    JOIN User U ON F.sender_id = U.user_id
                    WHERE (F.sender_id = (SELECT user_id FROM User WHERE username = ?)
                        AND F.receiver_id = (SELECT user_id FROM User WHERE username = ?))
                    OR (F.sender_id = (SELECT user_id FROM User WHERE username = ?)
                        AND F.receiver_id = (SELECT user_id FROM User WHERE username = ?))
                    ORDER BY F.timestamp ASC
                """, (self.username, self.connection, self.connection, self.username))
                # Fetch all files
                files = cursor.fetchall()
                
                # Get private key for decryption
                private_key = self._get_private_key()
                
                for encrypted_content, timestamp, username, sender_id, filename in files:
                    is_sender = username == self.username
                    # Decrypt file content
                    if is_sender:
                        # For files we sent, we need to decrypt them again for display
                        encrypted_data = json.loads(encrypted_content)
                        content = self.encryption.decrypt(encrypted_data, private_key)
                    else:
                        # For received files, decrypt the stored content
                        encrypted_data = json.loads(encrypted_content)
                        content = self.encryption.decrypt(encrypted_data, private_key)
                    
                    self.display_file(username, filename, timestamp, content, is_sender)
                    
        except Exception as e:
            print(f"Error loading files: {str(e)}")
            QMessageBox.warning(self, "Warning", 
                            "Some files could not be loaded properly.")






class Group_Messages_Window(GUI_Window):

    # Add new signal at class level
    group_notification_received = pyqtSignal(str, str, str)  # group_name, creator, group_id
    create_group_chat_signal = pyqtSignal(str, str, str)

    # Constructor method initialises the window.
    def __init__(self, username):
        super().__init__(title="Encrypta - Group Messages")
        self.username = username
        # Initialize the group chat windows dictionary
        self.group_chat_windows = {}
        # Initialize server-related attributes
        self.server_running = True
        self.base_port = GROUP_PORT
        self.symmetric = SymmetricEncryption()
        # Connect the signal to window creation method
        self.create_group_chat_signal.connect(self.create_group_chat_window)
        self.group_notification_received.connect(self.handle_group_notification)
        self.init_server()
        self.init_ui()
        self.showMaximized()


    def create_group_chat_window(self, username, group_name, group_id):
        """Create group chat window in the main thread"""
        print(f"Creating group chat window for group {group_name} (ID: {group_id})")
        try:
            if group_id not in self.group_chat_windows:
                window = GroupMessage(username, group_name, group_id)
                self.group_chat_windows[group_id] = window
                window.show()
            return self.group_chat_windows[group_id]
        except Exception as e:
            print(f"Error creating group chat window: {e}")
            traceback.print_exc()

    
    def handle_group_message(self, notification):
        """Handle incoming group message"""
        try:
            group_id = str(notification['group_id'])
            
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Get group key
            cursor.execute("SELECT symmetric_key FROM 'Group' WHERE group_id = ?", (group_id,))
            group_key = cursor.fetchone()[0]
            
            # Decrypt message
            encrypted = bytes.fromhex(notification['message'])
            decrypted = self.symmetric.decrypt(group_key, encrypted)
            message_text = decrypted.decode()
            
            # Store message
            cursor.execute("""
                INSERT INTO GroupMessages 
                (group_id, sender_id, message_content, timestamp)
                VALUES (?, 
                    (SELECT user_id FROM User WHERE username = ?),
                    ?, ?)
            """, (group_id, notification['sender'], message_text, notification['timestamp']))
            
            conn.commit()
            
            # Update UI
            if group_id in self.group_chat_windows:
                window = self.group_chat_windows[group_id]
                window.message_received.emit(
                    notification['sender'],
                    message_text,
                    notification['timestamp']
                )
            else:
                # Create new window if needed
                cursor.execute("SELECT group_name FROM 'Group' WHERE group_id = ?", (group_id,))
                group_name = cursor.fetchone()[0]
                
                self.create_group_chat_signal.emit(
                    self.username,
                    group_name,
                    group_id
                )
                
        except Exception as e:
            print(f"Error processing group message: {e}")
            traceback.print_exc()
        finally:
            if conn:
                conn.close()



    def _process_message_safe(self, window, notification):
        """Process message in main thread"""
        try:
            window.process_incoming_message(notification)
        except Exception as e:
            print(f"Error processing message: {e}")
            traceback.print_exc()


    def init_server(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM User WHERE username = ?", (self.username,))
            user_id = cursor.fetchone()[0]
            
            # Start socket server for online status
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                # Use 0.0.0.0 instead of localhost to accept external connections
                self.server_socket.bind(('0.0.0.0', self.base_port))
                self.server_socket.listen(5)
                print(f"Server started for {self.username} on port {self.base_port}")
                
                # Start listener thread
                self.server_running = True
                self.listener_thread = threading.Thread(target=self.listen_for_connections)
                self.listener_thread.daemon = True
                self.listener_thread.start()
                
            except Exception as e:
                print(f"Server initialization error: {str(e)}")
                QMessageBox.warning(self, "Warning", f"Server initialization error: {str(e)}")
        except Exception as e:
            print(f"Database error during server init: {str(e)}")
        finally:
            if conn:
                conn.close()


        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Back button with modern styling
        self.back_button = QPushButton("Back")
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 20px;
                font-weight: bold;
                max-width: 100px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        main_layout.addWidget(self.back_button, alignment=Qt.AlignLeft)
        self.back_button.clicked.connect(self.back)

        # Keep DM functionality but hide it
        self.dm_web = QWebEngineView()
        self.dm_list = QListWidget()
        self.dm_list.hide()  # Hide the DM list
        
        # Main container for centered content
        main_container = QWidget()
        main_container_layout = QHBoxLayout(main_container)
        main_container_layout.setContentsMargins(50, 20, 50, 20)  # Add padding around the main container
        
        # Center container for Group Chats
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setContentsMargins(0, 0, 0, 0)
        
        # Group header with modern styling
        header_container = QWidget()
        header_container.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-radius: 10px;
                margin-bottom: 10px;
            }
        """)
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        group_title = QLabel("Group Chats")
        group_title.setStyleSheet("""
            font-size: 40px;
            font-weight: bold;
            color: #2c3e50;
        """)
        
        create_group_btn = QPushButton("Create Group")
        create_group_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 7px;
                padding: 12px 25px;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        create_group_btn.clicked.connect(self.show_create_group_dialog)
        
        header_layout.addWidget(group_title)
        header_layout.addStretch()
        header_layout.addWidget(create_group_btn)
        
        center_layout.addWidget(header_container)
        
        # Group list with modern styling
        self.group_list = QListWidget()
        self.group_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #e9ecef;
                border-radius: 10px;
                padding: 10px;
                background-color: white;
                font-size: 24px;
            }
            QListWidget::item {
                padding: 15px;
                border-bottom: 1px solid #f1f3f5;
                border-radius: 5px;
                margin-bottom: 5px;
                
            }
            QListWidget::item:hover {
                background-color: #f8f9fa;
            }
            QListWidget::item:selected {
                background-color: #e9ecef;
                color: #212529;
            }
        """)
        
        
        self.group_list.itemDoubleClicked.connect(self.open_group_chat)
        center_layout.addWidget(self.group_list)
        
        # Add center widget to main container
        main_container_layout.addWidget(center_widget)
        
        # Add main container to main layout
        main_layout.addWidget(main_container)
        
        # Set window minimum size
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        # Load connections and groups
        self.load_connections()
        self.load_groups()
        
        # Start online status check timer
        self.ping_timer = QTimer()
        self.ping_timer.timeout.connect(self.check_user_online)
        self.ping_timer.start(30000)


    def load_groups(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT DISTINCT g.group_name, g.group_id
                FROM "Group" g
                JOIN GroupMembership gm ON g.group_id = gm.group_id
                JOIN User u ON gm.user_id = u.user_id
                WHERE u.username = ?
                GROUP BY g.group_id
                ORDER BY g.group_name
            """, (self.username,))
            
            groups = cursor.fetchall()
            
            js_code = "const groupList = document.getElementById('group-list'); groupList.innerHTML = '';"
            
            if groups:
                for group_name, group_id in groups:
                    js_code += f"""
                    const item = document.createElement('div');
                    item.className = 'item';
                    item.innerHTML = '{group_name}';
                    item.onclick = function() {{ window.qt.open_group_chat('{group_id}', '{group_name}'); }};
                    groupList.appendChild(item);
                    """
            else:
                js_code += """
                const placeholder = document.createElement('div');
                placeholder.className = 'placeholder';
                placeholder.textContent = 'No group chats yet';
                groupList.appendChild(placeholder);
                """
                
            self.web_view.page().runJavaScript(js_code)
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to load groups: {str(e)}")
        finally:
            if conn:
                conn.close()



    @pyqtSlot(str)
    def open_direct_message(self, username):
        self.dm_window = DirectMessage(self.username, username)
        self.dm_window.show()
        self.close()



    def handle_group_notification(self, group_name, creator, group_id):
        """Handle group notification in the main thread"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Verify the group membership exists
            cursor.execute("""
                SELECT COUNT(*) FROM GroupMembership gm
                JOIN User u ON u.user_id = gm.user_id
                WHERE gm.group_id = ? AND u.username = ?
            """, (group_id, self.username))
            
            if cursor.fetchone()[0] == 0:
                print(f"Group membership not found for group {group_id}")
                return
                
            QMessageBox.information(
                self,
                "New Group Chat",
                f"You have been added to group '{group_name}' by {creator}"
            )
            self.load_groups()  # Refresh groups list
            
        except Exception as e:
            print(f"Error handling group notification: {e}")
        finally:
            if conn:
                conn.close()


        
    
    def load_connections(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Get current user's ID from the database
            cursor.execute("SELECT user_id FROM User WHERE username = ?", (self.username,))
            user_id = cursor.fetchone()[0]
            
            # Get all connected users except the current user
            cursor.execute("""
                SELECT u.username, c.connection_ip_address 
                FROM Connection c
                JOIN User u ON (c.receiver_id = u.user_id OR c.sender_id = u.user_id)
                WHERE (c.sender_id = ? OR c.receiver_id = ?)
                AND c.status = 'connected'
                AND u.username != ?
                ORDER BY u.username
            """, (user_id, user_id, self.username))

            connections = cursor.fetchall()
            
            # Clear existing items
            self.dm_list.clear()

            # Add items to the list with online status
            for username, ip_address in connections:
                is_online = self.check_server_online(ip_address, user_id)
                item = QListWidgetItem()
                status_text = "🟢 Online" if is_online else "🔴 Offline"
                item.setText(f"{username} ({status_text})")
                item.setToolTip(f"Double click to chat with {username}")
                self.dm_list.addItem(item)

            # Add placeholder if no connections    
            if self.dm_list.count() == 0:
                placeholder = QListWidgetItem("No connections yet")
                placeholder.setFlags(placeholder.flags() & ~Qt.ItemIsEnabled)
                self.dm_list.addItem(placeholder)
                
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to load connections: {str(e)}")
        finally:
            if conn:
                conn.close()



    def open_direct_message(self, item):
        """Open direct message window when connection is double-clicked"""
        selected_username = item.text()
        if selected_username != "No connections yet":
            self.dm_window = DirectMessage(self.username, selected_username)
            self.dm_window.show()
            self.close()





    def check_server_online(self, ip, user_id):
        """Check if a server is running at the given IP and port"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2)  # Increase timeout
                print(f"Checking {ip}:{self.base_port}")  # Debug print
                result = s.connect_ex((ip, self.base_port))
                is_online = result == 0
                print(f"Server check result for {ip}: {is_online}")  # Debug print
                return is_online
        except Exception as e:
            print(f"Error checking server {ip}: {e}")
            return False


    
    def listen_for_connections(self):
        """Listen for incoming connections, notifications, and group updates"""
        while self.server_running:
            try:
                self.server_socket.settimeout(1)
                client, addr = self.server_socket.accept()
                
                data = client.recv(4096).decode()
                if data:
                    try:
                        notification = json.loads(data)
                        print(f"Received notification: {notification}")  # Debug print
                        
                        if notification['type'] == 'new_group':
                            self.handle_new_group_notification(notification)
                        elif notification['type'] == 'group_message':
                            self.handle_group_message(notification)
                            
                    except json.JSONDecodeError as e:
                        print(f"JSON decode error: {e}")
                    except Exception as e:
                        print(f"Error processing notification: {e}")
                        
                client.close()
            except socket.timeout:
                continue
            except Exception as e:
                if self.server_running:
                    print(f"Server error: {e}")


    def handle_new_group_notification(self, notification):
        """Handle new group creation notification"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute("SELECT user_id FROM User WHERE username = ?", (self.username,))
            user_id = cursor.fetchone()[0]
            
            # Begin transaction
            cursor.execute("BEGIN TRANSACTION")
            
            group_key = bytes.fromhex(notification['group_key'])
            
            # First create/update group record
            cursor.execute("""
                INSERT OR REPLACE INTO "Group" 
                (group_id, group_name, group_size, creator, creator_id, symmetric_key)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                notification['group_id'],
                notification['group_name'],
                notification['group_size'],
                notification['creator'],
                notification['creator_id'],
                group_key
            ))
            
            # Add membership
            cursor.execute("""
                INSERT OR REPLACE INTO GroupMembership (group_id, user_id)
                VALUES (?, ?)
            """, (notification['group_id'], user_id))
            
            # Store all member IPs
            for username, ip in notification['members']:
                cursor.execute("""
                    INSERT OR REPLACE INTO GroupMemberConnections 
                    (group_id, username, member_ip) 
                    VALUES (?, ?, ?) """, (notification['group_id'], username, ip))
            


            cursor.execute("SELECT connection_ip_address FROM Connection WHERE username = ?", (notification['creator'],))
            creator_ip = cursor.fetchone()[0]

            conn.commit()
            
            # Update UI
            self.group_notification_received.emit(
                notification['group_name'],
                notification['creator'],
                str(notification['group_id'])
            )
            
        except Exception as e:
            print(f"Error handling new group: {e}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()


    def handle_group_message_notification(self, notification):
        """Handle incoming group message notification"""
        try:
            group_id = str(notification['group_id'])
            print(f"Handling group message for {group_id}")
            
            # If window doesn't exist, create it
            if group_id not in self.group_chat_windows:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                try:
                    cursor.execute("""
                        SELECT group_name FROM "Group" 
                        WHERE group_id = ?
                    """, (group_id,))
                    group_name = cursor.fetchone()[0]
                    
                    # Create window via signal
                    self.create_group_chat_signal.emit(
                        self.username,
                        group_name,
                        group_id
                    )
                finally:
                    conn.close()
            
            # Process message in window
            if group_id in self.group_chat_windows:
                window = self.group_chat_windows[group_id]
                # Use QTimer to ensure main thread processing
                QTimer.singleShot(0, lambda: window.process_incoming_message(notification))
            else:
                print(f"Error: Window for group {group_id} not found")
                
        except Exception as e:
            print(f"Error handling group message: {e}")
            traceback.print_exc()




    def show_create_group_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Create Group Chat")
        dialog.setModal(True)
        layout = QVBoxLayout()

        # Group name input with validation
        name_layout = QHBoxLayout()
        name_label = QLabel("Group Name:")
        name_input = QLineEdit()
        name_input.setPlaceholderText("Enter group name (3-30 characters)")
        name_layout.addWidget(name_label)
        name_layout.addWidget(name_input)
        layout.addLayout(name_layout)

        # Connections list
        connections_label = QLabel("Select Members:")
        layout.addWidget(connections_label)
        
        connections_list = QListWidget()
        connections_list.setSelectionMode(QListWidget.MultiSelection)
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Get current user's ID
            cursor.execute("SELECT user_id FROM User WHERE username = ?", (self.username,))
            user_id = cursor.fetchone()[0]
            
            # Get all connected users
            cursor.execute("""
                SELECT u.username, u.user_id, c.connection_ip_address 
                FROM Connection c
                JOIN User u ON (c.receiver_id = u.user_id OR c.sender_id = u.user_id)
                WHERE (c.sender_id = ? OR c.receiver_id = ?)
                AND c.status = 'connected'
                AND u.username != ?
                ORDER BY u.username
            """, (user_id, user_id, self.username))

            connections = cursor.fetchall()

            # Add connections to list with online status
            for username, conn_user_id, ip_address in connections:
                print(f"Checking user {username}: ID={conn_user_id}, IP={ip_address}")  # Debug print
                is_online = self.check_server_online(ip_address, conn_user_id)
                print(f"Online status: {is_online}")  # Debug print
                item = QListWidgetItem()
                status_text = "🟢 Online" if is_online else "🔴 Offline"
                item.setText(f"{username} ({status_text})")
                item.setData(Qt.UserRole, (conn_user_id, ip_address, is_online))
                connections_list.addItem(item)
            
            if connections_list.count() == 0:
                placeholder = QListWidgetItem("No connections available")
                placeholder.setFlags(placeholder.flags() & ~Qt.ItemIsEnabled)
                connections_list.addItem(placeholder)
                
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to load connections: {str(e)}")
        finally:
            if conn:
                conn.close()
            
        layout.addWidget(connections_list)

        # Buttons
        button_layout = QHBoxLayout()
        create_btn = QPushButton("Create")
        cancel_btn = QPushButton("Cancel")
        button_layout.addWidget(create_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        dialog.setLayout(layout)

        def create_group():
            group_name = name_input.text().strip()
            
            if not group_name:
                QMessageBox.warning(dialog, "Error", "Please enter a group name")
                return
                
            if len(group_name) < 3 or len(group_name) > 30:
                QMessageBox.warning(dialog, "Error", "Group name must be between 3 and 30 characters")
                return

            # Check if group name already exists
            for i in range(self.group_list.count()):
                item = self.group_list.item(i)
                if item.text() == group_name:
                    QMessageBox.warning(dialog, "Error", "Group name already exists")
                    return

            selected_members = []
            offline_members = []
            
            for i in range(connections_list.count()):
                item = connections_list.item(i)
                if item.isSelected():
                    username = item.text().split(" (")[0]  # Extract username without status
                    user_id, ip_address, is_online = item.data(Qt.UserRole)
                    
                    # Double-check online status before creating group
                    if self.check_server_online(ip_address, user_id):
                        selected_members.append((username, user_id))
                    else:
                        offline_members.append(username)
                                
            if offline_members:
                QMessageBox.warning(
                    dialog, 
                    "Offline Members", 
                    f"Cannot create group: The following members are offline:\n{', '.join(offline_members)}"
                )
                return
                
            if len(selected_members) == 0:
                QMessageBox.warning(dialog, "Error", "Please select at least one online member")
                return
                
            success = self.create_group(group_name, selected_members)
            if success:
                QMessageBox.information(dialog, "Success", f"Group '{group_name}' created successfully!")
                dialog.accept()
        
        create_btn.clicked.connect(create_group)
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.exec_()




    def create_group(self, group_name, members):
        """Create a new group and notify members"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Start transaction
            cursor.execute("BEGIN TRANSACTION")
            
            # Get current user's ID
            cursor.execute("SELECT user_id FROM User WHERE username = ?", (self.username,))
            creator_id = cursor.fetchone()[0]
            print(f"Creator ID: {creator_id}")  # Debug print

            # Generate symmetric key for the group
            group_key = self.symmetric.generate_key()
            print(f"Group key: {group_key.hex()}")  # Debug print
            
            # Create new group
            cursor.execute("""
                INSERT INTO "Group" (group_name, group_size, creator, creator_id, symmetric_key)
                VALUES (?, ?, ?, ?, ?)
            """, (group_name, len(members) + 1, self.username, creator_id, group_key))

            print(f"Group created: {group_name}")  # Debug print
            
            group_id = cursor.lastrowid
            
            # Add creator to group membership
            cursor.execute("""
                INSERT INTO GroupMembership (group_id, user_id)
                VALUES (?, ?)
            """, (group_id, creator_id))

            print(f"Creator added to group: {self.username}")  # Debug print
            
            creator_ip = get_ip_address()

            print(f"Creator IP: {creator_ip}")  # Debug print
            
            # Store creator's connection
            cursor.execute("""
                INSERT INTO GroupMemberConnections (group_id, member_id, member_ip, username)
                VALUES (?, ?, ?, ?)
            """, (group_id, creator_id, creator_ip, self.username))
            
            print(f"Creator connection stored")  # Debug print

            # Process each member
            notification_failures = []
            for username, user_id in members:
                try:
                    # Get member's IP directly from Connection table
                    cursor.execute("""
                        SELECT connection_ip_address FROM Connection
                        WHERE username = ?
                    """, (username,))
                    
                    ip_address = cursor.fetchone()[0]
                    print(f"Member {username} IP: {ip_address}")  # Debug print
                    
                    # Add to group membership
                    cursor.execute("""
                        INSERT INTO GroupMembership (group_id, user_id)
                        VALUES (?, ?)
                    """, (group_id, user_id))

                    print(f"Member {username} added to group")  # Debug print
                    
                    # Store member connection
                    cursor.execute("""
                        INSERT INTO GroupMemberConnections (group_id, member_id, member_ip, username)
                        VALUES (?, ?, ?, ?)
                    """, (group_id, user_id, ip_address, username))
                    

                    print(f"Member {username} connection stored")  # Debug print


                    # Prepare member notification
                    notification_data = {
                        'type': 'new_group',
                        'group_id': group_id,
                        'group_name': group_name,
                        'group_size': len(members) + 1,
                        'creator': self.username,
                        'creator_id': creator_id,
                        'group_key': group_key.hex(),
                        # List of all members in the group
                        'members': [ (self.username, creator_ip) ] + members
                    }
                    
                    if not self.notify_new_group_member(ip_address, notification_data):
                        notification_failures.append(username)
                        
                except Exception as e:
                    print(f"Error processing member {username}: {e}")
                    notification_failures.append(username)
                    continue
            
            conn.commit()
            
            # Refresh group list
            self.load_groups()
            
            if notification_failures:
                QMessageBox.warning(
                    self, 
                    "Partial Success", 
                    f"Group created but failed to notify: {', '.join(notification_failures)}"
                )
            return True
            
        except Exception as e:
            if conn:
                conn.rollback()
            QMessageBox.critical(self, "Error", f"Failed to create group: {str(e)}")
            return False
            
        finally:
            if conn:
                conn.close()



    def notify_new_group_member(self, ip_address, notification_data):
        """Send notification and key to new group member"""
        try:
            print(f"Attempting to notify member at {ip_address}")  # Debug print
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2)
                s.connect((ip_address, self.base_port))
                data = json.dumps(notification_data).encode()
                s.send(data)
                print(f"Successfully sent notification: {data}")  # Debug print
            return True
        except Exception as e:
            print(f"Failed to notify member at {ip_address}: {str(e)}")
            return False

    def notify_member(self, user_id, group_name, group_id):
        """Send notification to group member about new group"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Get member's IP address
            cursor.execute("""
                SELECT connection_ip_address 
                FROM Connection 
                WHERE (sender_id = ? OR receiver_id = ?)
                AND status = 'connected'
            """, (user_id, user_id))
            
            ip_address = cursor.fetchone()[0]
            
            # Create notification message
            notification = {
                'type': 'group_invite',
                'group_name': group_name,
                'group_id': group_id,
                'creator': self.username
            }
            
            # Send notification to member's IP
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(2)
                    s.connect((ip_address, self.base_port))
                    s.send(json.dumps(notification).encode())
            except Exception as e:
                print(f"Failed to notify member: {str(e)}")
                
        except sqlite3.Error as e:
            print(f"Database error in notify_member: {str(e)}")
        finally:
            if conn:
                conn.close()





    def check_user_online(self):
        """Check online status of all connected users"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Get current user's ID
            cursor.execute("SELECT user_id FROM User WHERE username = ?", (self.username,))
            user_id = cursor.fetchone()[0]
            
            # Get all connections
            cursor.execute("""
                SELECT u.username, c.connection_ip_address, u.user_id 
                FROM Connection c
                JOIN User u ON (c.receiver_id = u.user_id OR c.sender_id = u.user_id)
                WHERE (c.sender_id = ? OR c.receiver_id = ?)
                AND c.status = 'connected'
                AND u.username != ?
            """, (user_id, user_id, self.username))
            
            connections = cursor.fetchall()
            
            # Update DM list items
            for i in range(self.dm_list.count()):
                item = self.dm_list.item(i)
                username = item.text().split(" (")[0]  # Remove any existing status
                
                # Find matching connection
                connection = next((conn for conn in connections if conn[0] == username), None)
                if connection:
                    username, ip_address, conn_user_id = connection
                    is_online = self.check_server_online(ip_address, conn_user_id)
                    
                    if is_online:
                        item.setForeground(QColor('#28a745'))
                        item.setText(f"{username} (Online)")
                    else:
                        item.setForeground(QColor('#dc3545'))
                        item.setText(f"{username} (Offline)")
        
        except sqlite3.Error as e:
            print(f"Database error in check_user_online: {str(e)}")
        except Exception as e:
            print(f"Error in check_user_online: {str(e)}")
        finally:
            if conn:
                conn.close()



    def load_groups(self):
        """Load all groups for current user"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Simple query to get user's groups
            cursor.execute("""
                SELECT DISTINCT g.group_name, g.group_id
                FROM "Group" g
                JOIN GroupMembership gm ON g.group_id = gm.group_id
                JOIN User u ON gm.user_id = u.user_id
                WHERE u.username = ?
                ORDER BY g.group_name
            """, (self.username,))
            
            groups = cursor.fetchall()
            
            self.group_list.clear()
            
            for group_name, group_id in groups:
                item = QListWidgetItem(group_name)
                item.setData(Qt.UserRole, group_id)
                item.setToolTip(f"Double click to open {group_name}")
                self.group_list.addItem(item)
                
            if self.group_list.count() == 0:
                placeholder = QListWidgetItem("No group chats yet")
                placeholder.setFlags(placeholder.flags() & ~Qt.ItemIsEnabled)
                self.group_list.addItem(placeholder)
                
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to load groups: {str(e)}")
            print(f"Database error: {e}")
            
        finally:
            if conn:
                conn.close()


    def open_group_chat(self, item):
        """Open group chat window when group is double-clicked"""
        if item.text() != "No group chats yet":
            try:
                group_id = str(item.data(Qt.UserRole))  # Convert to string to ensure consistency
                group_name = item.text()
                print(f"Opening group chat: {group_name} (ID: {group_id})")  # Debug print
                
                # Create and show the group chat window using self.username
                group_window = GroupMessage(self.username, group_name, group_id)
                self.group_chat_windows[group_id] = group_window  # Store reference to window
                group_window.show()
                
            except Exception as e:
                print(f"Error opening group chat: {e}")
                QMessageBox.critical(self, "Error", f"Failed to open group chat: {str(e)}")


    def back(self):
        from .dashboard import Main_Menu_Window

        self.redirect = Main_Menu_Window(self.username)
        self.redirect.show()
        self.close()


    def closeEvent(self, event):
        """Clean up server on window close"""
        self.server_running = False
        if hasattr(self, 'server_socket'):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(0.5)
                    s.connect(('localhost', self.base_port))
            except Exception:
                pass
            try:
                self.server_socket.close()
            except Exception:
                pass
        if hasattr(self, 'listener_thread'):
            self.listener_thread.join(timeout=1)
        super().closeEvent(event)





class GroupMessage(GUI_Window):
    # Add message signal at class level
    message_received = pyqtSignal(str, str, str)  # sender, message, timestamp

    def __init__(self, username, group_name, group_id):
        super().__init__(title=f"Encrypta - {group_name}")
        self.username = username
        self.group_name = group_name 
        self.group_id = group_id
        self.symmetric = SymmetricEncryption()
        self.base_port = GROUP_PORT
        self.members = []
        
        # Initialize UI components
        self.init_ui()
        
        # Connect signal after UI setup
        self.message_received.connect(self.update_chat)
        
        # Load data after UI and signal setup
        self.load_group_key()
        self.load_members()
        
        # Important: Load messages after web view is fully loaded
        self.web_view.loadFinished.connect(self.on_web_view_loaded)
        
        # Store reference to main window
        self.messages_window = None
        for window in QApplication.topLevelWidgets():
            if isinstance(window, Group_Messages_Window):
                self.messages_window = window
                self.messages_window.group_chat_windows[str(group_id)] = self
                break

        # Start status check timer
        self.start_status_timer()
        
        self.showMaximized()


    def process_incoming_message(self, notification):
        """Process incoming encrypted message"""
        try:
            print(f"Processing message in group {self.group_id} from {notification['sender']}")
            
            # Decrypt message
            encrypted = bytes.fromhex(notification['message'])
            decrypted = self.symmetric.decrypt(self.group_key, encrypted)
            message_text = decrypted.decode()
            timestamp = notification['timestamp']
            
            print(f"Decrypted message: {message_text}")  # Debug print
            
            # Save to database first
            self.save_message(
                message_text,
                notification['sender'],
                timestamp
            )
            
            # Update UI in main thread using signal
            self.message_received.emit(
                notification['sender'],
                message_text, 
                timestamp
            )
                
        except Exception as e:
            print(f"Error processing message: {e}")
            traceback.print_exc()



    @pyqtSlot(str, str, str)
    def update_chat(self, sender, message, timestamp):
        """Update chat area with new message"""
        try:
            formatted_message = f"[{timestamp}] {sender}: {message}\n"
            
            # Always update in main thread
            if QThread.currentThread() == QApplication.instance().thread():
                self.web_view.append(formatted_message)
                self.web_view.verticalScrollBar().setValue(
                    self.web_view.verticalScrollBar().maximum()
                )
            else:
                QMetaObject.invokeMethod(
                    self.web_view,
                    "append",
                    Qt.QueuedConnection,
                    Q_ARG(str, formatted_message)
                )
            print(f"Message displayed: {formatted_message}")  # Debug print
        
        except Exception as e:
            print(f"Error in update_chat: {e}")
            traceback.print_exc()


    def load_group_key(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT symmetric_key 
                FROM "Group" 
                WHERE group_name = ?
            """, (self.group_name,))
            
            result = cursor.fetchone()
            if not result or not result[0]:
                raise Exception("Group key not found")
                
            key_data = result[0]
            print(f"Raw key data type: {type(key_data)}")
            print(f"Raw key length: {len(key_data)}")
            
            # Convert to bytes if needed
            if isinstance(key_data, str):
                try:
                    # Try hex decode if it's hex encoded
                    self.group_key = bytes.fromhex(key_data)
                except:
                    # Otherwise encode as bytes
                    self.group_key = key_data.encode()
            else:
                # Already bytes
                self.group_key = key_data
                
            print(f"Final key type: {type(self.group_key)}")
            print(f"Final key length: {len(self.group_key)}")
            print(f"Key hex: {self.group_key.hex()}")
            
        except Exception as e:
            print(f"Error loading group key: {e}")
            QMessageBox.critical(self, "Error", "Failed to load encryption key")
            self.close()
        finally:
            if conn:
                conn.close()




    def init_ui(self):
        """Initialize the UI components with improved layout"""
        # Main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Top bar with search - now using QGridLayout for better alignment
        top_bar = QGridLayout()
        top_bar.setSpacing(10)
        
        # Back button
        back_button = QPushButton("←")
        back_button.clicked.connect(self.back)
        back_button.setFixedWidth(40)
        back_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        top_bar.addWidget(back_button, 0, 0)
        
        # Group name label
        group_label = QLabel(self.group_name)
        group_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                padding: 5px;
            }
        """)
        top_bar.addWidget(group_label, 0, 1)
        
        # Search bar - aligned with members list
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search messages...")
        self.search_bar.returnPressed.connect(self.search_messages)
        self.search_bar.setFixedWidth(200)
        self.search_bar.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #2196F3;
            }
        """)
        top_bar.addWidget(self.search_bar, 0, 2, Qt.AlignRight)
        
        # Add stretch to push search bar to the right
        top_bar.setColumnStretch(1, 1)
        
        main_layout.addLayout(top_bar)
        
        # Chat area and members list in horizontal layout
        chat_container = QHBoxLayout()
        chat_container.setSpacing(15)  # Increased spacing between chat and members
        
        # Messages area
        self.web_view = QWebEngineView()
        self.web_view.setMinimumHeight(400)
        chat_container.addWidget(self.web_view, stretch=7)
        
        # Members section with improved styling
        members_container = QWidget()
        members_container.setFixedWidth(220)  # Slightly wider for better appearance
        members_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
            }
        """)
        
        members_layout = QVBoxLayout(members_container)
        members_layout.setContentsMargins(10, 10, 10, 10)
        members_layout.setSpacing(10)
        
        members_label = QLabel("Group Members")
        members_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333;
                padding: 5px;
                border-bottom: 1px solid #eee;
            }
        """)
        members_layout.addWidget(members_label)
        
        self.members_list = QListWidget()
        self.members_list.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: transparent;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
            }
            QListWidget::item:hover {
                background-color: #f5f5f5;
            }
        """)
        members_layout.addWidget(self.members_list)
        
        chat_container.addWidget(members_container)
        
        main_layout.addLayout(chat_container)
        
        # Message input area with improved styling
        input_container = QHBoxLayout()
        input_container.setSpacing(10)
        
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type a message...")
        self.message_input.returnPressed.connect(self.send_message_from_input)
        self.message_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 20px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #2196F3;
            }
        """)
        
        send_button = QPushButton("Send")
        send_button.clicked.connect(self.send_message_from_input)
        send_button.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                border: none;
                border-radius: 20px;
                background-color: #2196F3;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
        """)
        
        input_container.addWidget(self.message_input)
        input_container.addWidget(send_button)
        
        main_layout.addLayout(input_container)
        
        # Set up web channel and load HTML template
        self.setup_web_channel()
        self.load_html_template()



    def on_web_view_loaded(self, success):
        """Handle web view load completion"""
        if success:
            # Now it's safe to load messages
            self.load_messages()
        else:
            print("Failed to load web view")


    def setup_web_channel(self):
        """Set up web channel for JS communication"""
        self.channel = QWebChannel()
        self.web_view.page().setWebChannel(self.channel)
        # Create handler object to send messages
        class Handler(QObject):
            def __init__(self, parent):
                super().__init__()
                self.parent = parent
            # Send message to Python
            @pyqtSlot(str)
            def sendMessage(self, message):
                self.parent.send_group_message(message)
        # Register handler object
        self.handler = Handler(self)
        self.channel.registerObject("handler", self.handler)



    def update_chat(self, sender, message, timestamp):
        """Update chat with proper message display"""
        try:
            # Escape special characters for JavaScript
            sender_escaped = sender.replace('"', '\\"').replace("'", "\\'")
            message_escaped = message.replace('"', '\\"').replace("'", "\\'")
            timestamp_escaped = timestamp.replace('"', '\\"').replace("'", "\\'")
            
            # Check if message is from current user
            is_self = sender == self.username
            
            js_code = f"""
            try {{
                addMessage("{sender_escaped}", "{message_escaped}", "{timestamp_escaped}", {str(is_self).lower()});
            }} catch (error) {{
                console.error('Error adding message:', error);
            }}
            """
            self.web_view.page().runJavaScript(js_code)
            
        except Exception as e:
            print(f"Error in update_chat: {e}")
            traceback.print_exc()

    def start_status_timer(self):
        """Start timer to check online status periodically"""
        self.status_timer = QTimer(self)  # Pass self as parent
        self.status_timer.timeout.connect(self.check_members_online)
        self.status_timer.start(5000)  # Check every 5 seconds


    def load_members(self):
        try:
            # Load all members of the group
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            print(f"\n=== DEBUG INFO FOR GROUP {self.group_id} ===")
            # Get all members with their IPs
            cursor.execute("""
                SELECT DISTINCT gmc.username, 
                    CASE 
                        WHEN gmc.username = ? THEN ?
                        ELSE c.connection_ip_address 
                    END as ip_address
                FROM GroupMemberConnections gmc
                LEFT JOIN Connection c ON c.username = gmc.username
                WHERE gmc.group_id = ? AND gmc.username != ?
            """, (self.username, get_ip_address(), self.group_id, self.username))

            # Store all members in a list
            self.members = cursor.fetchall()
            # Add current user to the list
            self.members.append((self.username, get_ip_address()))  

            print(f"\nMembers query result: {self.members}")
            # Clear and re-populate members list
            self.members_list.clear()
            # Add each member to the list
            for username, ip in self.members:
                item = QListWidgetItem()
                is_online = self.check_server_online(ip)
                status = "🟢 Online" if is_online else "🔴 Offline"
                item.setText(f"{username} ({status})")
                self.members_list.addItem(item)

        except sqlite3.Error as e:
            print(f"Database error loading members: {e}")
            traceback.print_exc()
        finally:
            if conn:
                conn.close()



    def check_members_online(self):
        """Check online status of all group members"""
        if not hasattr(self, 'members') or not self.members:
            self.load_members()
            return
            
        try:
            for i in range(self.members_list.count()):
                item = self.members_list.item(i)
                if not item:
                    continue
                    
                username = item.text().split(" (")[0]
                member = next((m for m in self.members if m[0] == username), None)
                
                if member and member[1]:  # Check if we have IP
                    is_online = self.check_server_online(member[1])
                    status = "🟢 Online" if is_online else "🔴 Offline" 
                    item.setText(f"{username} ({status})")
                    
        except Exception as e:
            print(f"Error checking members online: {e}")
            traceback.print_exc()


    def load_html_template(self):
        """Load HTML template with fixed styling"""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    margin: 0;
                    padding: 15px;
                    background: #e5ddd5;
                    color: #333;
                    height: 100vh;
                    overflow-y: auto;
                }
                
                #messages {
                    display: flex;
                    flex-direction: column;
                    gap: 8px;
                    padding-bottom: 20px; /* Add padding at bottom for better scrolling */
                }
                
                .message-container {
                    display: flex;
                    flex-direction: column;
                    max-width: 65%;
                }
                
                .message-container.sent {
                    align-self: flex-end;
                }
                
                .message-container.received {
                    align-self: flex-start;
                }
                
                .message {
                    padding: 8px 12px;
                    border-radius: 12px;
                    position: relative;
                    word-wrap: break-word;
                    box-shadow: 0 1px 1px rgba(0, 0, 0, 0.1);
                }
                
                .message.sent {
                    background: #dcf8c6;
                    margin-left: auto;
                    border-top-right-radius: 4px;
                }
                
                .message.received {
                    background: #ffffff;
                    margin-right: auto;
                    border-top-left-radius: 4px;
                }
                
                .sender {
                    font-size: 0.8em;
                    font-weight: 500;
                    color: #1f7aec;
                    margin-bottom: 2px;
                }
                
                .message-content {
                    line-height: 1.4;
                }
                
                .timestamp {
                    font-size: 0.7em;
                    color: #667781;
                    margin-top: 2px;
                    text-align: right;
                }

                /* Scrollbar styling */
                ::-webkit-scrollbar {
                    width: 8px;
                }
                
                ::-webkit-scrollbar-track {
                    background: rgba(0, 0, 0, 0.1);
                    border-radius: 4px;
                }
                
                ::-webkit-scrollbar-thumb {
                    background: rgba(0, 0, 0, 0.2);
                    border-radius: 4px;
                }
                
                ::-webkit-scrollbar-thumb:hover {
                    background: rgba(0, 0, 0, 0.3);
                }
            </style>
        </head>
        <body>
            <div id="messages"></div>
            
            <script>
                let messageHistory = [];
                
                function addMessage(sender, message, timestamp, isSelf) {
                    const messagesDiv = document.getElementById('messages');
                    if (!messagesDiv) return;
                    
                    const container = document.createElement('div');
                    container.className = `message-container ${isSelf ? 'sent' : 'received'}`;
                    
                    const messageDiv = document.createElement('div');
                    messageDiv.className = `message ${isSelf ? 'sent' : 'received'}`;
                    
                    if (!isSelf) {
                        const senderDiv = document.createElement('div');
                        senderDiv.className = 'sender';
                        senderDiv.textContent = sender;
                        messageDiv.appendChild(senderDiv);
                    }
                    
                    const contentDiv = document.createElement('div');
                    contentDiv.className = 'message-content';
                    contentDiv.textContent = message;
                    messageDiv.appendChild(contentDiv);
                    
                    const timeDiv = document.createElement('div');
                    timeDiv.className = 'timestamp';
                    timeDiv.textContent = timestamp;
                    messageDiv.appendChild(timeDiv);
                    
                    container.appendChild(messageDiv);
                    messagesDiv.appendChild(container);
                    
                    messageHistory.push({sender, message, timestamp, isSelf});
                    
                    // Scroll to bottom after adding message
                    document.body.scrollTo({
                        top: document.body.scrollHeight,
                        behavior: 'smooth'
                    });
                }

                if (typeof QWebChannel !== 'undefined') {
                    new QWebChannel(qt.webChannelTransport, function(channel) {
                        window.handler = channel.objects.handler;
                    });
                }
            </script>
        </body>
        </html>
        """
        self.web_view.setHtml(html_content)


    def send_message_from_input(self):
        """Handle sending message from input field"""
        message = self.message_input.text().strip()
        if message:
            self.send_group_message(message)
            self.message_input.clear()


    # Override closeEvent to clean up timer
    def search_messages(self):
        """Search messages implementation with proper error handling"""
        search_text = self.search_bar.text().strip().lower()
        if not search_text:
            # Reload all messages if search is empty
            self.load_messages()  
            return
                
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Search for messages containing the text
            cursor.execute("""
                SELECT u.username, gm.message_content, gm.timestamp
                FROM GroupMessages gm
                JOIN User u ON gm.sender_id = u.user_id
                WHERE gm.group_id = ? 
                AND LOWER(gm.message_content) LIKE ?
                ORDER BY gm.timestamp
            """, (self.group_id, f"%{search_text}%"))
            
            messages = cursor.fetchall()
            
            # Clear current messages
            self.web_view.page().runJavaScript(
                "document.getElementById('messages').innerHTML = '';"
            )
            
            if not messages:
                # Show "no results" message using JavaScript
                self.web_view.page().runJavaScript(
                    'addMessage("System", "No messages found matching your search.", "' + 
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '", false);'
                )
                return
                
            # Display search results
            for username, content, timestamp in messages:
                self.update_chat(username, content, timestamp)
                
        except sqlite3.Error as e:
            print(f"Database error in search: {e}")
            QMessageBox.warning(
                self, 
                "Search Error",
                "Failed to search messages. Please try again."
            )
        except Exception as e:
            print(f"Unexpected error in search: {e}")
            QMessageBox.warning(
                self, 
                "Search Error",
                f"An unexpected error occurred: {str(e)}"
            )
        finally:
            if conn:
                conn.close()





    def check_server_online(self, ip):
        """Check if a server is running at the given IP and port"""
        if ip == '127.0.0.1' and self.username == self.username:
            return True
            
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)  # Shorter timeout
                print(f"Checking {ip}:{self.base_port}")
                result = s.connect_ex((ip, self.base_port))
                is_online = result == 0
                print(f"Server check result for {ip}: {is_online}")
                return is_online
        except Exception as e:
            print(f"Error checking server {ip}: {e}")
            return False





    def check_all_members_online(self):
        """Check if all members are online"""
        offline_members = []
        for username, user_id, ip in self.members:
            if not self.check_server_online(ip, user_id):
                offline_members.append(username)
        return offline_members



    def send_group_message(self, message_text):
        """Modified to work with new UI"""
        try:
            if not message_text:
                return

            # Check if all members are online before sending
            offline_members = []
            for username, ip_address in self.members:
                if username != self.username:
                    if not self.messages_window.check_server_online(ip_address, None):
                        offline_members.append(username)

            if offline_members:
                self.web_view.page().runJavaScript(
                    f'alert("Cannot send message. The following members are offline: {", ".join(offline_members)}")'
                )
                return

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Encrypt message
            encrypted = self.symmetric.encrypt(self.group_key, message_text.encode())

            # Create notification
            notification = {
                'type': 'group_message',
                'group_id': self.group_id,
                'sender': self.username,
                'message': encrypted.hex(),
                'timestamp': timestamp
            }

            # Send to all other members
            send_failures = []
            for username, ip_address in self.members:
                if username != self.username:
                    try:
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                            s.settimeout(2)
                            s.connect((ip_address, self.base_port))
                            s.send(json.dumps(notification).encode())
                    except Exception as e:
                        print(f"Failed to send to {username}: {e}")
                        send_failures.append(username)

            if send_failures:
                self.web_view.page().runJavaScript(
                    f'alert("Failed to deliver message to: {", ".join(send_failures)}")'
                )
                return

            # Save and display own message
            self.save_message(message_text, self.username, timestamp)
            self.update_chat(self.username, message_text, timestamp)

        except Exception as e:
            print(f"Error sending message: {e}")
            self.web_view.page().runJavaScript(
                f'alert("Failed to send message: {str(e)}")'
            )



    def send_via_parent(self, ip, notification):
        """Send message through parent window's server connection"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2)
                s.connect((ip, self.base_port))
                s.send(json.dumps(notification).encode())
            return True
        except Exception as e:
            print(f"Failed to send via parent: {e}")
            return False



    def send_to_member(self, ip, message_data):
        """Send message to a specific member"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2)
                s.connect((ip, self.base_port))
                s.send(json.dumps(message_data).encode())
            return True
        except Exception as e:
            print(f"Failed to send to {ip}: {e}")
            return False




    def save_message(self, content, sender=None, timestamp=None):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            if sender is None:
                sender = self.username
            if timestamp is None:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
            cursor.execute("""
                INSERT INTO GroupMessages 
                (group_id, message_content, timestamp, sender_id, encryption_type)
                VALUES (?, ?, ?, 
                    (SELECT user_id FROM User WHERE username = ?),
                    'AES'
                )
            """, (self.group_id, content, timestamp, sender))
            
            conn.commit()
        except Exception as e:
            print(f"Failed to save message: {e}")
        finally:
            if conn:
                conn.close()



    def load_messages(self):
        """Load message history from database"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # First clear existing messages
            self.web_view.page().runJavaScript("document.getElementById('messages').innerHTML = '';")
            
            cursor.execute("""
                SELECT u.username, gm.message_content, gm.timestamp
                FROM GroupMessages gm
                JOIN User u ON gm.sender_id = u.user_id 
                WHERE gm.group_id = ?
                ORDER BY gm.timestamp
            """, (self.group_id,))
            
            messages = cursor.fetchall()
            
            # Use JavaScript to display messages
            for username, content, timestamp in messages:
                self.update_chat(username, content, timestamp)
                
        except Exception as e:
            print(f"Failed to load messages: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load messages: {str(e)}")
        finally:
            if conn:
                conn.close()



    def display_message(self, sender, message, timestamp=None):
        """Thread-safe message display"""
        try:
            # Use current timestamp if not provided
            if timestamp is None:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # Format message for display   
            formatted_message = f"[{timestamp}] {sender}: {message}\n"
            
            # Ensure we're in the main thread
            if QThread.currentThread() == QApplication.instance().thread():
                self.web_view.append(formatted_message)
                self.web_view.verticalScrollBar().setValue(
                    self.web_view.verticalScrollBar().maximum()
                )
            else:
                QMetaObject.invokeMethod(self.web_view,
                                    "append",
                                    Qt.QueuedConnection,
                                    Q_ARG(str, formatted_message))
        except Exception as e:
            print(f"Error displaying message: {e}")
            traceback.print_exc()





    def back(self):
        """Return to group chat list"""
        self.messages_window.show()
        self.close()




    def closeEvent(self, event):
        """Clean up resources when window is closed"""
        self.server_running = False
        if hasattr(self, 'status_timer'):
            self.status_timer.stop()
        super().closeEvent(event)
