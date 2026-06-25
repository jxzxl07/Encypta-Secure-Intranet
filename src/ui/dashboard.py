from .common import *
from .base import GUI_Window, ConnectionHandler
from ..network.servers import StatusServer
from ..utils.helpers import get_ip_address, send_status_update
from .auth import ChangePasswordDialog, Log_In_Window
from .calls import Calls_Window
from .chat import Direct_Messages_Window, Group_Messages_Window

class Main_Menu_Window(GUI_Window):
    server_running = False
    active_connections = []

    # Constructor method initialises the window.
    def __init__(self, username):
        super().__init__(title="Encrypta - Main Menu")
        self.username = username
        self.client_socket = None
        self.server_thread = None
        self.is_listening = False
        self.connection_handler = ConnectionHandler()
        self.init_ui()
        self.showMaximized()
        self.load_existing_connections()

        # Only start the connection listener if no server is running
        if not Main_Menu_Window.server_running:
            self.start_connection_listener()
        else:
            # Update the status label to show we're already listening
            self.status_label.setText("Connection Status: Listening")
            self.status_label.setStyleSheet("color: #28a745; margin-bottom: 10px;")

        self.handle_connection_request

        # Connect signals to their respective handlers
        self.connection_handler.connection_request_received.connect(
            self.handle_connection_request,
            type=Qt.QueuedConnection  # Ensure cross-thread signal haSndling
        )
        self.connection_handler.connection_accepted.connect(
            self.handle_connection_accepted,
            type=Qt.QueuedConnection
        )
        self.connection_handler.connection_rejected.connect(
            self.handle_connection_rejected,
            type=Qt.QueuedConnection
        )
        self.connection_handler.connection_error.connect(
            self.handle_connection_error,
            type=Qt.QueuedConnection
        )


    def init_ui(self):
        main_layout = QHBoxLayout()
        
        # Left Panel (70% width)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Header with logout button
        header = QHBoxLayout()
        self.logout_button = QPushButton("Log Out")
        self.logout_button.setStyleSheet("""
            QPushButton { background-color: #dc3545; color: white; border: none;
                        border-radius: 3px; padding: 13px 10px; font-size: 20px;
                        font-weight: bold;}
            QPushButton:hover { background-color: #c82333; }""")
        self.logout_button.clicked.connect(self.log_out)
        header.addWidget(self.logout_button)
        header.addStretch()
        left_layout.addLayout(header)
        
        # Main Menu Title
        title = QLabel(f"Main Menu - {self.username}")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 50px; font-weight: bold; margin: 20px 0;")
        left_layout.addWidget(title)
        
        # Main Action Buttons
        buttons_layout = QHBoxLayout()
        buttons = [
            ("User Dashboard", "user-dash"),
            ("Direct Messages", "direct-messages"),
            ("Group Chats", "group-chats"),
            ("Calls", "calls")
        ]
        
        # Create buttons and connect them to their respective actions
        for button_text, button_id in buttons:
            button = QPushButton(button_text)
            button.setProperty("id", button_id)
            button.setStyleSheet("""
                QPushButton { background-color: #007BFF; color: white; border: none;
                            border-radius: 10px; padding: 30px 20px; font-size: 24px;
                            font-weight: bold; margin: 10px; }
                QPushButton:hover { background-color: #0056b3; } """)
            if button_id == "user-dash":
                button.clicked.connect(self.redirect_to_dash)
            elif button_id == "direct-messages":
                button.clicked.connect(self.redirect_to_direct_messages)
            elif button_id == "group-chats":
                button.clicked.connect(self.redirect_to_group_chats)
            else:
                button.clicked.connect(self.redirect_to_calls)
            buttons_layout.addWidget(button)
        
        left_layout.addLayout(buttons_layout)
        
        # Activity Feed
        activity_group = QGroupBox("Recent Activity")
        activity_group.setStyleSheet("""
            QGroupBox {font-size: 18px; font-weight: bold; border: 1px solid #ddd;
                border-radius: 5px; margin-top: 20px; padding: 15px;}""")
        activity_layout = QVBoxLayout()

        # Create a list widget to display activity feed
        self.activity_list = QListWidget()
        self.activity_list.setStyleSheet("""
            QListWidget {border: none;font-size: 14px;}
            QListWidget::item {padding: 10px;border-bottom: 1px solid #eee;}""")
        activity_layout.addWidget(self.activity_list)
        activity_group.setLayout(activity_layout)
        left_layout.addWidget(activity_group)
        
        # Right Panel (30% width)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Connections Management
        connections_group = QGroupBox("Connections")
        connections_group.setStyleSheet("""
            QGroupBox { font-size: 24px; font-weight: bold; border: 1px solid #ddd;
                border-radius: 5px; padding: 15px;}""")
        connections_layout = QVBoxLayout()
        
        # Connection status indicator
        self.status_label = QLabel("Connection Status: Not Listening")
        self.status_label.setStyleSheet("color: #dc3545; margin-bottom: 10px;")
        # INcrease font size of status label
        self.status_label.setFont(QFont("Arial", 12))
        connections_layout.addWidget(self.status_label)
        
        # Connections list
        self.connections_list = QTableWidget()
        self.connections_list.setColumnCount(2)
        self.connections_list.setHorizontalHeaderLabels(["Username", "Status"])
        self.connections_list.setStyleSheet("""
            QTableWidget {border: none; font-size: 17px;}
            QHeaderView::section {background-color: #f8f9fa; padding: 8px; border: none;
                                font-weight: bold;}""")
        self.connections_list.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.connections_list.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.connections_list.setColumnWidth(1, 100)
        connections_layout.addWidget(self.connections_list)
        
        # Add connection interface
        add_connection_layout = QHBoxLayout()
        self.connection_input = QLineEdit()
        self.connection_input.setPlaceholderText("Enter IP address")
        self.connection_input.setStyleSheet("""
            QLineEdit { padding: 8px; border: 1px solid #ccc; border-radius: 5px;
                            font-size: 20px;}""")
        add_connection_layout.addWidget(self.connection_input)

        # Add connection button
        self.add_button = QPushButton("Add Connection")
        self.add_button.setStyleSheet("""
            QPushButton {background-color: #28a745; color: white; border: none;
                border-radius: 5px; padding: 8px 15px; font-size: 16px; font-weight: bold;}
            QPushButton:hover { background-color: #218838; }""")
        # Connect the button to the send_connection_request method
        self.add_button.clicked.connect(self.send_connection_request)
        add_connection_layout.addWidget(self.add_button)
        connections_layout.addLayout(add_connection_layout)
        connections_group.setLayout(connections_layout)
        right_layout.addWidget(connections_group)
        
        # Set layouts
        main_layout.addWidget(left_panel, 70)
        main_layout.addWidget(right_panel, 30)
        self.layout.addLayout(main_layout)



    def load_existing_connections(self):
        """Load existing connections from database"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            # Get current user's ID
            cursor.execute("SELECT user_id FROM User WHERE username = ?", (self.username,))
            current_user_id = cursor.fetchone()[0]
            
            # Get all active connections for current user
            cursor.execute("""
                SELECT u.username, c.status
                FROM Connection c
                JOIN User u ON (c.sender_id = u.user_id OR c.receiver_id = u.user_id)
                WHERE (c.sender_id = ? OR c.receiver_id = ?)
                AND u.username != ?
                AND c.status = 'connected'
            """, (current_user_id, current_user_id, self.username))
            
            connections = cursor.fetchall()
            
            # Add each connection to the UI and store in class-level list
            for username, status in connections:
                self.add_connection(username, 'Connected')
                if username not in [conn[0] for conn in Main_Menu_Window.active_connections]:
                    Main_Menu_Window.active_connections.append((username, 'Connected'))
                    
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()



    def start_connection_listener(self):
        if not Main_Menu_Window.server_running:
            self.server_thread = threading.Thread(target=self._run_server)
            self.server_thread.daemon = True
            self.server_thread.start()
            self.is_listening = True
            Main_Menu_Window.server_running = True
            self.status_label.setText("Connection Status: Listening")
            self.status_label.setStyleSheet("color: #28a745; margin-bottom: 10px;")


    def _run_server(self):
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Add this line
            server.bind(('0.0.0.0', CONNECTION_PORT))
            server.listen(5)
            server.settimeout(1)
            
            while self.is_listening:
                try:
                    client, addr = server.accept()
                    threading.Thread(target=self._handle_connection, args=(client,)).start()
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.is_listening:
                        print(f"Error in server thread: {e}")
                        
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            server.close()
            Main_Menu_Window.server_running = False



    def _handle_connection(self, client):
        """Handle incoming connection requests with improved reliability"""
        MAX_RETRIES = 3
        RETRY_DELAY = 0.5  # seconds
        

        def receive_with_timeout(client_socket, buffer_size=1024, timeout=5):
            """Helper function to receive data with timeout and retries"""
            start_time = time.time()
            received_data = ""
            
            while time.time() - start_time < timeout:
                try:
                    chunk = client_socket.recv(buffer_size).decode()
                    if chunk:
                        received_data += chunk
                        if received_data.endswith('}'):  # Basic check for complete JSON
                            return received_data
                    elif received_data:  # If we already have some data but got empty chunk
                        return received_data
                    else:
                        time.sleep(0.1)  # Small delay before retry
                except socket.timeout:
                    if received_data:
                        return received_data
                    continue
            
            raise TimeoutError("Timeout waiting for complete data")

        for attempt in range(MAX_RETRIES):
            try:
                # Set socket timeout for each attempt
                client.settimeout(5)
                
                # Try to receive data with improved handling
                try:
                    data = receive_with_timeout(client)
                    if not data:
                        if attempt < MAX_RETRIES - 1:
                            time.sleep(RETRY_DELAY)
                            continue
                        raise ValueError("Received empty data after retries")
                except TimeoutError as te:
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(RETRY_DELAY)
                        continue
                    raise
                    
                # Log received data for debugging
                print(f"Received data (attempt {attempt + 1}): {data[:100]}...")
                    
                # Parse JSON with validation
                try:
                    request = json.loads(data)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON received: {data[:100]}...")
                    
                if 'type' not in request:
                    raise ValueError("Request missing 'type' field")

                # Handle different types of requests
                if request['type'] == 'check_username':
                    response = {
                        'username': self.username
                    }
                    client.send(json.dumps(response).encode())
                    return
                    
                elif request['type'] == 'connection_request':
                    if 'username' not in request or 'public_key' not in request:
                        raise ValueError("Connection request missing required fields")
                        
                    # Check existing connections
                    for row in range(self.connections_list.rowCount()):
                        username_item = self.connections_list.item(row, 0)
                        status_item = self.connections_list.item(row, 1)
                        if (username_item and status_item and 
                            username_item.text() == request['username'] and 
                            status_item.text() == "Connected"):
                            rejection = {
                                'type': 'connection_rejected',
                                'username': self.username,
                                'message': f"Already connected to {self.username}"
                            }
                            client.send(json.dumps(rejection).encode())
                            return

                    self.connection_handler.connection_request_received.emit(
                        request['username'],
                        request['public_key'],
                        client,
                        request.get('sender_ip', '')
                    )
                    return  # Successful handling
                    
                elif request['type'] == 'connection_accepted':
                    if 'username' not in request or 'public_key' not in request:
                        raise ValueError("Connection acceptance missing required fields")
                        
                    self.connection_handler.connection_accepted.emit(
                        request['username'],
                        request['public_key'],
                        request.get('sender_ip', '')
                    )
                    return  # Successful handling
                    
                elif request['type'] == 'connection_rejected':
                    if 'username' not in request:
                        raise ValueError("Connection rejection missing username")
                        
                    self.connection_handler.connection_rejected.emit(request['username'])
                    return  # Successful handling
                    
                else:
                    raise ValueError(f"Unknown request type: {request['type']}")
                    
            except (json.JSONDecodeError, ValueError, TimeoutError) as e:
                if attempt < MAX_RETRIES - 1:
                    print(f"Attempt {attempt + 1} failed: {str(e)}. Retrying...")
                    time.sleep(RETRY_DELAY)
                    continue
                self.connection_handler.connection_error.emit(str(e))
                break
            except Exception as e:
                self.connection_handler.connection_error.emit(f"Unexpected error: {str(e)}")
                break
            finally:
                if attempt == MAX_RETRIES - 1:  # Only close on last attempt
                    try:
                        client.close()
                    except:
                        pass

    

    
    def handle_connection_request(self, username, public_key, client, sender_ip):
        """Handle incoming connection request from another user"""
        try:
            # Get local IP address first
            local_ip = get_ip_address()  # Make sure this function is imported/defined
            
            # Ask the user to accept or reject the connection
            response = QMessageBox.question(
                self,
                "Connection Request",
                f"Connection request from {username} ({sender_ip}). Accept?",
                QMessageBox.Yes | QMessageBox.No
            )
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # Get current user's data
            cursor.execute("SELECT user_id, public_key FROM User WHERE username = ?", (self.username,))
            current_user_data = cursor.fetchone()
            if not current_user_data:
                raise Exception(f"Current user {self.username} not found in database")
            current_user_id, my_public_key = current_user_data

            # Create new socket to send response back to original sender
            response_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            response_socket.settimeout(5)

            if response == QMessageBox.Yes:
                # Store sender in local database
                cursor.execute("""
                    INSERT OR REPLACE INTO User (username, public_key)
                    VALUES (?, ?)
                """, (username, public_key))
                sender_id = cursor.lastrowid

                # Store connection in local database
                cursor.execute("""
                    INSERT OR REPLACE INTO Connection 
                    (sender_id, receiver_id, username, status, connection_ip_address)
                    VALUES (?, ?, ?, 'connected', ?)
                """, (sender_id, current_user_id, username, sender_ip))

                # Update local UI
                self.add_activity(f"Accepted connection from {username}")
                self.add_connection(username, 'Connected')

                # Send acceptance message back to sender using their IP
                try:
                    response_socket.connect((sender_ip, CONNECTION_PORT))
                    acceptance = {
                        'type': 'connection_accepted',
                        'username': self.username,
                        'public_key': my_public_key,
                        'sender_ip': local_ip,  # Use the local_ip variable instead of self.local_ip
                        'message': f"Connection request accepted by {self.username}"
                    }
                    response_socket.send(json.dumps(acceptance).encode())
                except Exception as e:
                    print(f"Error sending acceptance back to sender: {e}")
                    
                # Show confirmation
                QMessageBox.information(
                    self,
                    "Connection Accepted",
                    f"You have accepted the connection request from {username}"
                )
            else:  # Handle rejection
                # Send rejection message back to sender using their IP
                try:
                    response_socket.connect((sender_ip, CONNECTION_PORT))
                    rejection = {
                        'type': 'connection_rejected',
                        'username': self.username,
                        'message': f"{self.username} has rejected your connection request"
                    }
                    response_socket.send(json.dumps(rejection).encode())
                except Exception as e:
                    print(f"Error sending rejection back to sender: {e}")
                    
                # Update local UI
                self.add_activity(f"Rejected connection request from {username}")
                
                # Show confirmation
                QMessageBox.information(
                    self,
                    "Connection Rejected",
                    f"You have rejected the connection request from {username}"
                )
                
            conn.commit()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to process connection: {str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()
            if 'response_socket' in locals():
                try:
                    response_socket.close()
                except:
                    pass
            if client:
                try:
                    client.close()
                except:
                    pass





    def handle_connection_accepted(self, username, public_key, sender_ip):
        """Handle when another user accepts our connection request"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            print(f"Starting connection acceptance for user: {username}")
            
            # Store the accepting user in our local database
            cursor.execute("""
                INSERT OR REPLACE INTO User (username, public_key)
                VALUES (?, ?)
            """, (username, public_key))
            other_user_id = cursor.lastrowid
            print(f"Other user ID: {other_user_id}")
            
            # Get our user_id
            cursor.execute("SELECT user_id FROM User WHERE username = ?", (self.username,))
            my_user_id_result = cursor.fetchone()
            if not my_user_id_result:
                raise Exception(f"Could not find user_id for {self.username}")
            my_user_id = my_user_id_result[0]
            print(f"My user ID: {my_user_id}")
            
            # Store connection in our local database
            print(f"Inserting connection with values: {username}, {my_user_id}, {other_user_id}, {sender_ip}")
            cursor.execute("""
                INSERT OR REPLACE INTO Connection 
                (username, sender_id, receiver_id, status, connection_ip_address)
                VALUES (?, ?, ?, 'connected', ?)
            """, (username, my_user_id, other_user_id, sender_ip))
            
            # Verify the connection was stored
            cursor.execute("""
                SELECT username, sender_id, receiver_id, status, connection_ip_address 
                FROM Connection 
                WHERE username = ?
            """, (username,))
            stored_connection = cursor.fetchone()
            print(f"Stored connection: {stored_connection}")
            
            if not stored_connection:
                raise Exception("Failed to store connection in database")
            conn.commit()
            
            # Update UI and class-level list
            self.add_activity(f"Connection established with {username}")
            self.add_connection(username, 'Connected')
            
            QMessageBox.information(
                self,
                "Connection Established",
                f"Connection established with {username}"
            )
            
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Database Error", f"Failed to update connection: {str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()




    def handle_connection_rejected(self, username):
        # Handle when our connection request is rejected
        try:
            # Update our local UI only
            self.add_activity(f"Connection request rejected by {username}")
            
            QMessageBox.information(
                self,
                "Connection Rejected",
                f"Your connection request was rejected by {username}"
            )
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to handle rejection: {str(e)}")

             


    # Handle connection error on the main thread         
    def handle_connection_error(self, error_message):
        QMessageBox.warning(
            self,
            "Connection Error",
            f"Connection error: {error_message}"
        )



    def send_connection_request(self):
        target_ip = self.connection_input.text().strip()
        if not target_ip:
            QMessageBox.warning(self, "Error", "Please enter an IP address")
            return
        
        # Check if the target IP is the same as our IP
        if target_ip == get_ip_address():
            QMessageBox.warning(self, "Error", "Cannot connect to self")
            return
        
        # Check if the target IP is already in the connections list via the database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM Connection WHERE connection_ip_address = ?", (target_ip,))
        existing_connection = cursor.fetchone()
        conn.close()
        if existing_connection:
            QMessageBox.warning(self, "Error", "Connection already exists")
            return
        
        
        # Check if the value entered is even an IP address format
        try:
            socket.inet_aton(target_ip)
        except socket.error:
            QMessageBox.warning(self, "Error", "Invalid IP address format")
            return
        
        client = None
        conn = None
        try:
            MAX_RETRIES = 3
            RETRY_DELAY = 1
            last_error = None
            
            for attempt in range(MAX_RETRIES):
                try:
                    # Initialize connection
                    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    client.settimeout(15)  # Increased timeout
                    
                    print(f"Attempt {attempt + 1}: Connecting to {target_ip}:{CONNECTION_PORT}...")
                    client.connect((target_ip, CONNECTION_PORT))
                    
                    # Get our public key
                    if not conn:  # Only get from DB once
                        conn = sqlite3.connect(DB_PATH)
                        cursor = conn.cursor()
                        cursor.execute("SELECT public_key FROM User WHERE username = ?", (self.username,))
                        result = cursor.fetchone()
                        if not result:
                            raise Exception(f"User {self.username} not found in database")
                        my_public_key = result[0]
                        if not my_public_key:
                            raise Exception("Public key not found in database")

                    # Send request
                    my_ip = get_ip_address()
                    request = {
                        'type': 'connection_request',
                        'username': self.username,
                        'public_key': my_public_key,
                        'sender_ip': my_ip
                    }
                    
                    print(f"Sending connection request (attempt {attempt + 1})...")
                    request_data = json.dumps(request).encode()
                    client.sendall(request_data)  # Use sendall instead of send
                    
                    # Wait briefly for potential immediate error response
                    time.sleep(0.5)
                    
                    print("Connection request sent successfully")
                    self.add_activity(f"Sent connection request to {target_ip}")
                    self.connection_input.clear()
                    return  # Success - exit the function
                    
                except socket.timeout as te:
                    last_error = f"Connection attempt {attempt + 1} timed out"
                    print(last_error)
                except Exception as e:
                    last_error = str(e)
                    print(f"Attempt {attempt + 1} failed: {last_error}")
                
                # Clean up before retry
                if client:
                    try:
                        client.close()
                    except:
                        pass
                    client = None
                    
                if attempt < MAX_RETRIES - 1:
                    print(f"Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                    
            # If we get here, all retries failed
            if last_error:
                QMessageBox.warning(self, "Connection Error", 
                                f"Failed to send connection request after {MAX_RETRIES} attempts: {last_error}")
        
        finally:
            if conn:
                conn.close()
            if client:
                try:
                    client.close()
                except:
                    pass


    def add_activity(self, message):
        """Add an activity to the activity feed"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.activity_list.insertItem(0, f"{timestamp} - {message}")



    def add_connection(self, username, status):
        """Add a connection to the connections table"""
        # Check if connection already exists in the table
        for row in range(self.connections_list.rowCount()):
            if self.connections_list.item(row, 0).text() == username:
                return  # Connection already exists, don't add it again
                
        row_position = self.connections_list.rowCount()
        self.connections_list.insertRow(row_position)
        self.connections_list.setItem(row_position, 0, QTableWidgetItem(username))
        status_item = QTableWidgetItem(status)
        status_item.setBackground(QColor("#28a745") if status == "Connected" else QColor("#dc3545"))
        self.connections_list.setItem(row_position, 1, status_item)
        
        # Add to class-level list if not already present
        if username not in [conn[0] for conn in Main_Menu_Window.active_connections]:
            Main_Menu_Window.active_connections.append((username, status))



    def closeEvent(self, event):
        """Clean up when closing the window"""
        self.is_listening = False
        Main_Menu_Window.server_running = False  # Reset the class-level server state
        if self.client_socket:
            self.client_socket.close()
        super().closeEvent(event)



    def redirect_to_dash(self):
        self.redirect = User_Dash_Window(self.username)
        self.redirect.show()
        self.close()


    def redirect_to_direct_messages(self):
        self.redirect = Direct_Messages_Window(self.username)
        self.redirect.show()
        self.close()


    def redirect_to_calls(self):
        self.redirect = Calls_Window(self.username)
        self.redirect.show()
        self.close()

    def redirect_to_group_chats(self):
        self.redirect = Group_Messages_Window(self.username)
        self.redirect.show()
        self.close()



    def log_out(self):
        # Update to offline in the local database
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("UPDATE User SET status = 'offline' WHERE username = ?", 
                        (self.username,))
            cursor.execute("""
                DELETE FROM Session 
                WHERE user_id = (SELECT user_id FROM User WHERE username = ?)
            """, (self.username,))
            conn.commit()
            # Notify admin server
            send_status_update(self.username, 'logout', get_ip_address())
            # Redirect to log in window
            self.redirect = Log_In_Window()
            self.redirect.show()
            self.close()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred during logout: {str(e)}")
        finally:
            if conn:
                conn.close()









   




class User_Dash_Window(GUI_Window):
    # Constructor method initialises the window.
    def __init__(self, username):
        self.username = username
        self.ipaddress = get_ip_address()
        super().__init__(title="Encrypta - User Dashboard")
        self.init_ui()
        self.showMaximized()
        
    def init_ui(self):
        main_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(40, 20, 40, 20)
        
        # Back Button - kept same style as it looks good
        self.back_button = QPushButton("Back")
        self.back_button.setStyleSheet("""
            QPushButton {background-color: #dc3545; color: white; border: none;
            border-radius: 3px;padding: 13px 10px; font-size: 20px;
            font-weight: bold;max-width: 100px;} 
            QPushButton:hover {background-color: #c82333;}""")
        left_layout.addWidget(self.back_button, alignment=Qt.AlignLeft)
        self.back_button.clicked.connect(self.back)
        
        # Title
        title_label = QLabel("User Dashboard")
        title_label.setStyleSheet("""
            QLabel {font-size: 40px;font-weight: bold;color: #2c3e50;margin: 20px 0;}""")
        left_layout.addWidget(title_label, alignment=Qt.AlignCenter)
        
        # Info Container Widget
        info_container = QWidget()
        info_container.setStyleSheet("""
            QWidget {background-color: white;border-radius: 10px;padding: 20px;}""")
        info_layout = QVBoxLayout(info_container)
        info_layout.setSpacing(20)
        
        # Username Box
        username_container = QWidget()
        username_container.setStyleSheet("""
            QWidget {background-color: #f8f9fa;border-radius: 8px;padding: 15px;}""")
        username_layout = QVBoxLayout(username_container)
        
        username_label = QLabel("USERNAME")
        username_label.setStyleSheet("""
            QLabel {color: #6c757d;font-size: 20px;font-weight: bold;letter-spacing: 1px;}""")
        
        username_value = QLabel(self.username)
        username_value.setStyleSheet("""
            QLabel {color: #212529;font-size: 27px;font-weight: 500;margin-top: 5px;}""")
        
        username_layout.addWidget(username_label)
        username_layout.addWidget(username_value)
        info_layout.addWidget(username_container)
        
        # IP Address Box
        ip_container = QWidget()
        ip_container.setStyleSheet("""
            QWidget {background-color: #f8f9fa;border-radius: 8px;padding: 15px;}""")
        ip_layout = QVBoxLayout(ip_container)
        
        ip_label = QLabel("IP ADDRESS")
        ip_label.setStyleSheet("""
            QLabel {color: #6c757d;font-size: 20px;font-weight: bold;letter-spacing: 1px;}""")
        
        ip_value = QLabel(self.ipaddress)
        ip_value.setStyleSheet("""
            QLabel {color: #212529;font-size: 27px;font-weight: 500;margin-top: 5px;}""")
        
        ip_layout.addWidget(ip_label)
        ip_layout.addWidget(ip_value)
        info_layout.addWidget(ip_container)
        left_layout.addWidget(info_container)
        
        # Reset Password Button
        self.reset_password_button = QPushButton("Change Password")
        self.reset_password_button.setStyleSheet("""
            QPushButton {background-color: #007bff;color: white;border: none;
            border-radius: 5px;padding: 15px 30px;font-size: 20px;font-weight: bold;
            margin-top: 30px;margin-bottom: 40px;min-width: 200px;}
            QPushButton:hover {background-color: #0056b3;}""")
        left_layout.addWidget(self.reset_password_button, alignment=Qt.AlignCenter)
        self.reset_password_button.clicked.connect(self.open_change_password_dialogue)
        
        # Dashboard Image
        dashboard_image = QLabel()
        dashboard_pixmap = QPixmap(asset_path("dashboard.png"))
        scaled_pixmap = dashboard_pixmap.scaled(340, 340, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        dashboard_image.setPixmap(scaled_pixmap)
        dashboard_image.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(dashboard_image)
        
        left_layout.addStretch()
        main_layout.addLayout(left_layout)
        self.layout.addLayout(main_layout)
    
    
    def open_change_password_dialogue(self):
        dialog = ChangePasswordDialog(self.username, self)
        if dialog.exec_() == QDialog.Accepted:
            # Password was successfully changed, redirect to login
            self.login_window = Log_In_Window()
            self.login_window.show()
            self.close()


    def back(self):
        self.redirect = Main_Menu_Window(self.username)
        self.redirect.show()
        self.close()


class Admin_Dash_Window(GUI_Window):
    def __init__(self):
        super().__init__(title="Encrypta - Admin Dashboard")
        self.server = StatusServer()
        self.init_ui()
        self.showMaximized()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Server control panel
        server_panel = QHBoxLayout()
        self.server_status_label = QLabel("Server Status: Stopped")
        self.server_status_label.setStyleSheet("""
            QLabel { font-size: 14px; font-weight: bold; color: #dc3545; }""")
        server_panel.addWidget(self.server_status_label)

        # Start server button
        self.start_server_btn = QPushButton("Start Server")
        self.start_server_btn.setStyleSheet("""
            QPushButton {background-color: #28a745; color: white;
            border: none;border-radius: 5px;padding: 8px 15px;font-size: 14px;}
            QPushButton:hover { background-color: #218838; }""")
        self.start_server_btn.clicked.connect(self.start_server)
        server_panel.addWidget(self.start_server_btn)

        # Stop server button
        self.stop_server_btn = QPushButton("Stop Server")
        self.stop_server_btn.setStyleSheet("""
            QPushButton {background-color: #dc3545;color: white;border: none;
            border-radius: 5px;padding: 8px 15px;font-size: 14px;}
            QPushButton:hover { background-color: #c82333; }""")
        self.stop_server_btn.setEnabled(False)
        self.stop_server_btn.clicked.connect(self.stop_server)
        server_panel.addWidget(self.stop_server_btn)
        
        server_panel.addStretch()
        
        # Refresh and logout buttons
        refresh_button = QPushButton("Refresh")
        refresh_button.setStyleSheet("""
            QPushButton {background-color: #17a2b8;color: white;border: none;
            border-radius: 5px;padding: 8px 15px;font-size: 14px;}
            QPushButton:hover { background-color: #138496; }""")
        refresh_button.clicked.connect(self.load_user_data)
        server_panel.addWidget(refresh_button)
        
        logout_button = QPushButton("Log Out")
        logout_button.setStyleSheet("""
            QPushButton {background-color: #6c757d;color: white;border: none;
            border-radius: 5px;padding: 8px 15px;font-size: 14px;}
            QPushButton:hover { background-color: #5a6268; }""")
        logout_button.clicked.connect(self.handle_logout)
        server_panel.addWidget(logout_button)
        
        main_layout.addLayout(server_panel)
        
        # User table
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(3)
        self.table_widget.setHorizontalHeaderLabels(["Username", "IPv4 Address", "Status"])
        self.table_widget.setStyleSheet("""
            QTableWidget {border: 1px solid #ddd;border-radius: 5px;padding: 5px;}
            QHeaderView::section {background-color: #f8f9fa;padding: 5px;
            border: 1px solid #ddd;font-weight: bold;}""")
        
        # Resizing and stretching formatting with containers
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        self.table_widget.setColumnWidth(2, 100)
        main_layout.addWidget(self.table_widget)
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        self.load_user_data()

    def start_server(self):
        if self.server.start(self.load_user_data):
            self.server_status_label.setText("Server Status: Running")
            self.server_status_label.setStyleSheet("""QLabel { font-size: 14px; font-weight: bold; color: #28a745; }""")
            self.start_server_btn.setEnabled(False)
            self.stop_server_btn.setEnabled(True)
            QMessageBox.information(self, "Success", "Server started successfully")
        else:
            QMessageBox.warning(self, "Error", "Failed to start server")

    def stop_server(self):
        if self.server.stop():
            self.server_status_label.setText("Server Status: Stopped")
            self.server_status_label.setStyleSheet("""QLabel { font-size: 14px; font-weight: bold; color: #dc3545; }""")
            self.start_server_btn.setEnabled(True)
            self.stop_server_btn.setEnabled(False)
            QMessageBox.information(self, "Success", "Server stopped successfully")
        else:
            QMessageBox.warning(self, "Error", "Failed to stop server") 

    def load_user_data(self):
        # Load user data into the table widget from the server's dictionary.
        try:
            # Get real-time status from the server
            server_status = self.server.get_client_status()

            if not server_status:
                self.table_widget.setRowCount(1)
                # Placeholder row
                placeholder_item = QTableWidgetItem("No Users Online")
                placeholder_item.setFlags(placeholder_item.flags() & ~Qt.ItemIsEditable)
                self.table_widget.setItem(0, 0, placeholder_item)
                # Empty other columns
                for col in range(1, 3):
                    empty_item = QTableWidgetItem("")
                    empty_item.setFlags(empty_item.flags() & ~Qt.ItemIsEditable)
                    self.table_widget.setItem(0, col, empty_item)

            self.table_widget.setRowCount(len(server_status))

            for row, (username, user_info) in enumerate(server_status.items()):
                # Username
                username_item = QTableWidgetItem(username)
                username_item.setFlags(username_item.flags() & ~Qt.ItemIsEditable)
                self.table_widget.setItem(row, 0, username_item)

                # IP Address
                ip_address = user_info.get("ip", "Not Connected")
                ip_item = QTableWidgetItem(ip_address)
                ip_item.setFlags(ip_item.flags() & ~Qt.ItemIsEditable)
                self.table_widget.setItem(row, 1, ip_item)

                # Status
                status = user_info.get("status", "offline")
                status_item = QTableWidgetItem(status)
                status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)

                if status == "online":
                    status_item.setBackground(QColor("#28a745"))  # Green
                else:
                    status_item.setBackground(QColor("#dc3545"))  # Red
                status_item.setForeground(QColor("white"))
                self.table_widget.setItem(row, 2, status_item)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")


    def handle_logout(self):
        if self.server.is_running:
            self.stop_server()
        self.redirect = Log_In_Window()
        self.redirect.show()
        self.close()

    def closeEvent(self, event):
        if self.server.is_running:
            self.stop_server()
        super().closeEvent(event)
