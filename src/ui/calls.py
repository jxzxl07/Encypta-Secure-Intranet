from .common import *
from .base import GUI_Window
from ..network.media import AudioReceiver, AudioSender, AudioStream, VideoReceiver, VideoSender
from ..network.servers import CallServer, VideoServer


class Calls_Window(GUI_Window):
    def __init__(self, username):
        super().__init__("Encrypta - Calls")

        self.username = username
        self.call_port = CALL_SIGNAL_PORT
        self.audio_port = CALL_AUDIO_PORT
        self.video_port = VIDEO_SIGNAL_PORT
        self.current_call = None
        self.call_server = None
        self.video_server = None
        
        # Setup UI
        self.setup_ui()
        
        # Start call server
        self.start_call_server()
        self.start_video_server()
        
        # Load connections
        self.load_connections()

        self.showMaximized()
        



    def setup_ui(self):
        # Create main layout container
        self.calls_container = QWidget()
        self.layout.addWidget(self.calls_container)
        self.calls_layout = QHBoxLayout(self.calls_container)
        
        # Set consistent styling for the entire container
        self.calls_container.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                font-size: 16px;
            }
            QLabel {
                font-size: 30px;
                font-weight: bold;
                color: #212529;
                padding: 10px 0;
            }
            QListWidget {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 10px;
                font-size: 24px;
                min-width: 300px;
            }
            QListWidget::item {
                padding: 18px;
                border-bottom: 1px solid #e9ecef;
            }
            QListWidget::item:selected {
                background-color: #007bff;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #e9ecef;
            }
        """)
        
        # Create splitter for voice/video sections
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.calls_layout.addWidget(self.splitter)
        
        # Voice calls section
        self.voice_widget = QWidget()
        self.voice_layout = QVBoxLayout(self.voice_widget)
        self.voice_label = QLabel("Voice Calls")
        self.call_list = QListWidget()
        self.voice_layout.addWidget(self.voice_label)
        self.voice_layout.addWidget(self.call_list)
        
        # Add spacing between sections
        self.voice_layout.setContentsMargins(20, 20, 20, 20)
        self.voice_layout.setSpacing(15)
        
        # Video calls section  
        self.video_widget = QWidget()
        self.video_layout = QVBoxLayout(self.video_widget)
        self.video_label = QLabel("Video Calls")
        self.video_list = QListWidget()
        self.video_layout.addWidget(self.video_label)
        self.video_layout.addWidget(self.video_list)
        
        # Add spacing between sections
        self.video_layout.setContentsMargins(20, 20, 20, 20)
        self.video_layout.setSpacing(15)
        
        # Add both sections to splitter
        self.splitter.addWidget(self.voice_widget)
        self.splitter.addWidget(self.video_widget)
        
        # Connect double click event to video call request too
        self.call_list.itemDoubleClicked.connect(self.handle_call_request)
        self.video_list.itemDoubleClicked.connect(self.handle_video_call_request)
        
        # Style the back button
        self.back_button = QPushButton("Back")
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 15px 20px;
                font-size: 18px;
                font-weight: bold;
                min-width: 10px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
        """)
        
        # Move back button to top left, above the calls container
        self.layout.insertWidget(0, self.back_button, 0, Qt.AlignLeft)
        self.back_button.clicked.connect(self.back)
        
        
    def back(self):
        from .dashboard import Main_Menu_Window

        self.redirect = Main_Menu_Window(self.username)
        self.redirect.show()
        self.close()
        



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
            self.call_list.clear()

            # Add items to the list
            for connection in connections:
                username = connection[0]
                item = QListWidgetItem(username)
                item.setToolTip(f"Double click to chat with {username}")
                self.call_list.addItem(item)

            # Add placeholder if no connections    
            if self.call_list.count() == 0:
                placeholder = QListWidgetItem("No connections yet")
                placeholder.setFlags(placeholder.flags() & ~Qt.ItemIsEnabled)
                self.call_list.addItem(placeholder)

            # Add items to video container too
            self.video_list.clear()
            for connection in connections:
                username = connection[0]
                item = QListWidgetItem(username)
                item.setToolTip(f"Double click to chat with {username}")
                self.video_list.addItem(item)
            # Add a placeholder if the list is empty
            if self.video_list.count() == 0:
                placeholder = QListWidgetItem("No connections yet")
                placeholder.setFlags(placeholder.flags() & ~Qt.ItemIsEnabled)
                self.video_list.addItem(placeholder)

            

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






    def check_server_online(self, ip):
        """Check if a server is running at the given IP and port"""
        if ip == '127.0.0.1' and self.username == self.username:
            return True
            
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)  # Shorter timeout
                print(f"Checking {ip}:{self.call_port}")
                result = s.connect_ex((ip, self.call_port))
                is_online = result == 0
                print(f"Server check result for {ip}: {is_online}")
                return is_online
        except Exception as e:
            print(f"Error checking server {ip}: {e}")
            return False



    def start_call_server(self):
        """Start TCP server to handle incoming calls"""
        self.call_server = CallServer(self.call_port, self.audio_port)
        self.call_server.call_received.connect(self.handle_incoming_call)
        self.call_server.start()
        

    def start_video_server(self):
        """Start TCP server to handle incoming video calls"""
        self.video_server = VideoServer(self.video_port)
        self.video_server.video_call_received.connect(self.handle_incoming_video_call)
        self.video_server.start()





    def handle_call_request(self, item):
        """Handle outgoing call request"""
        username = item.text().strip()

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT connection_ip_address FROM Connection WHERE username = ?", (username,))
        ip = cursor.fetchone()[0]

        # Check user is online
        if not self.check_server_online(ip):
            QMessageBox.critical(self, "Error", f"{username} is not online")
            return
        
        try:
            # Send call request
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((ip, self.call_port))
                s.send(json.dumps({
                    'type': 'call_request',
                    'username': self.username
                }).encode())
            
            # Create call window
            self.current_call = ActiveCallWindow(username, ip, self.audio_port)
            self.current_call.call_ended.connect(self.handle_call_ended)
            self.current_call.show()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start call: {str(e)}")

    # Handle incoming call request
    def handle_incoming_call(self, username, ip):
        # Ask user to accept or reject call
        response = QMessageBox.question(self, "Incoming Call",
                                      f"Incoming voice call from {username}. Accept?",
                                      QMessageBox.StandardButton.Yes | 
                                      QMessageBox.StandardButton.No)                        
        try:
            # Connect to the caller
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((ip, self.call_port))

                # Send response
                if response == QMessageBox.StandardButton.Yes:
                    s.send(json.dumps({'type': 'call_accepted'}).encode())
                    
                    # Create call window
                    self.current_call = ActiveCallWindow(username, ip, self.audio_port)
                    self.current_call.call_ended.connect(self.handle_call_ended)
                    self.current_call.show()
                else:
                    # Send rejection
                    s.send(json.dumps({'type': 'call_rejected'}).encode())
                    
        except Exception as e:
            # Handle errors
            QMessageBox.critical(self, "Error", f"Failed to handle call: {str(e)}")



    def handle_video_call_request(self, item):
        """Handle outgoing video call request"""
        username = item.text().strip()

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT connection_ip_address FROM Connection WHERE username = ?", (username,))
        ip = cursor.fetchone()[0]

        # Check user is online
        if not self.check_server_online(ip):
            QMessageBox.critical(self, "Error", f"{username} is not online")
            return
        
        try:
            # Send video call request
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((ip, self.video_port))
                s.send(json.dumps({
                    'type': 'video_call_request',
                    'username': self.username
                }).encode())
            
            # Create video call window
            self.current_call = VideoCallWindow(username, ip, self.video_port)
            self.current_call.call_ended.connect(self.handle_call_ended)
            self.current_call.show()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start video call: {str(e)}")


    

    def handle_incoming_video_call(self, username, ip):
        """Handle incoming video call request"""
        response = QMessageBox.question(self, "Incoming Video Call",
                                    f"Incoming video call from {username}. Accept?",
                                    QMessageBox.StandardButton.Yes | 
                                    QMessageBox.StandardButton.No)
                                    
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((ip, self.video_port))
                
                if response == QMessageBox.StandardButton.Yes:
                    s.send(json.dumps({'type': 'video_call_accepted'}).encode())
                    
                    # Create video call window
                    self.current_call = VideoCallWindow(username, ip, self.video_port)
                    self.current_call.call_ended.connect(self.handle_call_ended)
                    self.current_call.show()
                else:
                    s.send(json.dumps({'type': 'video_call_rejected'}).encode())
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to handle video call: {str(e)}")



    def handle_call_ended(self):
        """Clean up after call ends"""
        if self.current_call:
            self.current_call.close()
            self.current_call = None




    def closeEvent(self, event):
        """Clean up on window close"""
        if self.call_server:
            self.call_server.running = False
            self.call_server.wait()
        if self.video_server:
            self.video_server.stop()
        if self.current_call:
            self.current_call.close()
        super().closeEvent(event)







class VideoCallWindow(QWidget):
    call_ended = pyqtSignal()
    
    def __init__(self, username, ip, video_port, audio_port=CALL_AUDIO_PORT):
        super().__init__()
        self.username = username
        self.ip = ip
        self.video_port = video_port
        self.audio_port = audio_port
        self.running = True
        
        # Add control socket for call termination signals
        self.control_port = video_port + 2  # Use a different port for control signals
        self.control_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.control_socket.bind(('', self.control_port))

        # Start control message listener thread
        self.control_thread = threading.Thread(target=self.listen_for_control_messages)
        self.control_thread.daemon = True
        self.control_thread.start()

        # Initialize audio stream
        self.audio_input = pyaudio.PyAudio()
        self.audio_output = pyaudio.PyAudio()
        self.setup_audio()


        self.setup_ui()
        self.setup_video()




    def listen_for_control_messages(self):
        """Listen for control messages from the other user"""
        while self.running:
            try:
                data, addr = self.control_socket.recvfrom(1024)
                message = data.decode()
                if message == "CALL_TERMINATED":
                    # Use invokeMethod to safely call GUI-related code from another thread
                    QMetaObject.invokeMethod(self, "handle_remote_termination",
                                           Qt.ConnectionType.QueuedConnection)
            except:
                if not self.running:
                    break
                continue



    @pyqtSlot()
    def handle_remote_termination(self):
        """Handle call termination from the other user"""
        self.status_label.setText(f"{self.username} has ended the call")
        self.status_label.setStyleSheet("color: #dc3545; font-size: 12px;")
        
        # Show a notification dialog
        QMessageBox.information(self, "Call Ended",
                              f"{self.username} has ended the call",
                              QMessageBox.StandardButton.Ok)
        
        # Close the window
        self.close()




    def send_termination_signal(self):
        """Send termination signal to the other user"""
        try:
            self.control_socket.sendto("CALL_TERMINATED".encode(),
                                     (self.ip, self.control_port))
        except:
            pass  # Handle any network errors silently




        
    def setup_ui(self):
        # Window setup
        self.setWindowTitle(f"Video Call with {self.username}")
        self.setMinimumWidth(1000)  # Wider window
        self.setMinimumHeight(600)  # Taller window
        
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(20)  # Add spacing between elements
        
        # Video feeds container
        self.video_container = QHBoxLayout()
        self.video_container.setSpacing(30)  # Add spacing between videos
        
        # Local video widget
        self.local_widget = QWidget()
        self.local_layout = QVBoxLayout(self.local_widget)
        self.local_label = QLabel("Your Video")
        self.local_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.local_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 5px;")
        
        # Video frame container with fixed aspect ratio
        self.local_video_container = QWidget()
        self.local_video_container.setFixedSize(480, 360)  # 4:3 aspect ratio
        self.local_video_container.setStyleSheet("background-color: #f0f0f0; border: 2px solid #ddd; border-radius: 10px;")
        self.local_video = QLabel(self.local_video_container)
        self.local_video.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.local_video.setFixedSize(480, 360)
        
        self.local_layout.addWidget(self.local_label)
        self.local_layout.addWidget(self.local_video_container)
        
        # Remote video widget
        self.remote_widget = QWidget()
        self.remote_layout = QVBoxLayout(self.remote_widget)
        self.remote_label = QLabel(f"{self.username}'s Video")
        self.remote_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.remote_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 5px;")
        
        # Remote video container with fixed aspect ratio
        self.remote_video_container = QWidget()
        self.remote_video_container.setFixedSize(480, 360)  # 4:3 aspect ratio
        self.remote_video_container.setStyleSheet("background-color: #f0f0f0; border: 2px solid #ddd; border-radius: 10px;")
        self.remote_video = QLabel(self.remote_video_container)
        self.remote_video.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.remote_video.setFixedSize(480, 360)
        
        self.remote_layout.addWidget(self.remote_label)
        self.remote_layout.addWidget(self.remote_video_container)
        
        # Add video widgets to container
        self.video_container.addWidget(self.local_widget)
        self.video_container.addWidget(self.remote_widget)
        
        # Controls container
        self.controls_container = QWidget()
        self.controls_layout = QHBoxLayout(self.controls_container)
        self.controls_layout.setSpacing(20)  # Add spacing between buttons
        
        # Camera button
        self.camera_button = QPushButton("Turn Off Camera")
        self.camera_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 15px 30px;
                font-size: 14px;
                font-weight: bold;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        self.camera_button.clicked.connect(self.toggle_video)
        
        # Microphone button
        self.mic_button = QPushButton("Mute Microphone")
        self.mic_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 15px 30px;
                font-size: 14px;
                font-weight: bold;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.mic_button.clicked.connect(self.toggle_audio)
        
        # End call button
        self.end_call_button = QPushButton("End Call")
        self.end_call_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 15px 30px;
                font-size: 14px;
                font-weight: bold;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        self.end_call_button.clicked.connect(self.end_call)
        
        # Mute video button
        self.mute_video_button = QPushButton("Turn Off Camera")
        self.mute_video_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        self.mute_video_button.clicked.connect(self.toggle_video)
                                             
        # Add buttons to controls
        self.controls_layout.addStretch()
        self.controls_layout.addWidget(self.mic_button)
        self.controls_layout.addWidget(self.end_call_button)
        self.controls_layout.addWidget(self.mute_video_button)
        self.controls_layout.addStretch()
        
        # Status bar
        self.status_label = QLabel("Connected")
        self.status_label.setStyleSheet("color: #28a745; font-size: 12px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Add everything to main layout
        self.main_layout.addLayout(self.video_container)
        self.main_layout.addWidget(self.controls_container)
        self.main_layout.addWidget(self.status_label)




    def setup_audio(self):
        # Audio settings
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.audio_muted = False
        
        # Setup audio stream
        self.audio_stream = self.audio_input.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )
        
        # Setup audio socket
        self.audio_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Start audio threads
        self.audio_sender = AudioSender(
            self.audio_stream,
            self.audio_socket,
            self.ip,
            self.audio_port,
            self.CHUNK
        )
        self.audio_receiver = AudioReceiver(
            self.audio_output,
            self.audio_port,
            self.FORMAT,
            self.CHANNELS,
            self.RATE,
            self.CHUNK
        )
        
        self.audio_sender.start()
        self.audio_receiver.start()



    def toggle_audio(self):
        self.audio_muted = not self.audio_muted
        if self.audio_muted:
            self.mic_button.setText("Unmute Microphone")
            self.mic_button.setStyleSheet("""
                QPushButton {
                    background-color: #6c757d;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 15px 30px;
                    font-size: 14px;
                    font-weight: bold;
                    min-width: 150px;
                }
                QPushButton:hover {
                    background-color: #5a6268;
                }
            """)
            self.audio_sender.mute()
        else:
            self.mic_button.setText("Mute Microphone")
            self.mic_button.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 15px 30px;
                    font-size: 14px;
                    font-weight: bold;
                    min-width: 150px;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
            """)
            self.audio_sender.unmute()


        
    def setup_video(self):
        # Initialize video capture
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.status_label.setText("Failed to open camera!")
            self.status_label.setStyleSheet("color: red;")
            return
            
        # Start video threads
        self.video_muted = False
        self.start_video_stream()
        
    def start_video_stream(self):
        # Start sender thread
        self.sender = VideoSender(self.cap, self.ip, self.video_port, self.local_video)
        self.sender.start()
        
        # Start receiver thread
        self.receiver = VideoReceiver(self.video_port, self.remote_video)
        self.receiver.start()
        
    def toggle_video(self):
        self.video_muted = not self.video_muted
        if self.video_muted:
            self.mute_video_button.setText("Turn On Camera")
            self.local_video.clear()
            self.local_video.setText("Camera Off")
            self.sender.mute()
        else:
            self.mute_video_button.setText("Turn Off Camera")
            self.sender.unmute()

     
            
    def end_call(self):
        """Handle the end call button click"""
        # Send termination signal before closing
        self.send_termination_signal()
        
        # Update status and close window
        self.status_label.setText("Call ended")
        self.status_label.setStyleSheet("color: #dc3545; font-size: 12px;")
        self.call_ended.emit()
        self.close()

    def closeEvent(self, event):
        """Clean up on window close"""
        # Send termination signal if window is closed directly
        if self.running:
            self.send_termination_signal()
        
        self.running = False
        
        # Close control socket
        if hasattr(self, 'control_socket'):
            self.control_socket.close()
        
        # Stop video
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
        if hasattr(self, 'sender'):
            self.sender.stop()
        if hasattr(self, 'receiver'):
            self.receiver.stop()
            
        # Stop audio
        if hasattr(self, 'audio_sender'):
            self.audio_sender.stop()
        if hasattr(self, 'audio_receiver'):
            self.audio_receiver.stop()
            
        # Close audio streams
        if hasattr(self, 'audio_stream'):
            self.audio_stream.stop_stream()
            self.audio_stream.close()
        if hasattr(self, 'audio_input'):
            self.audio_input.terminate()
        if hasattr(self, 'audio_output'):
            self.audio_output.terminate()
            
        self.call_ended.emit()
        event.accept()



class ActiveCallWindow(QWidget):
    """Active call window with enhanced controls"""
    call_ended = pyqtSignal()
    
    def __init__(self, peer_username, peer_ip, audio_port):
        super().__init__()
        self.peer_username = peer_username
        self.peer_ip = peer_ip
        self.audio_port = audio_port
        
        # Call duration tracking
        self.call_start_time = QDateTime.currentDateTime()
        self.duration_timer = None
        
        self.setup_ui()
        self.setup_duration_timer()
        
        # Start audio streaming
        self.audio_stream = AudioStream(peer_ip, audio_port)
        self.audio_stream.audio_level.connect(self.update_audio_level)
        self.audio_stream.call_ended_by_peer.connect(self.handle_peer_ended_call)
        self.audio_stream.start()



    def handle_peer_ended_call(self):
        """Handle peer ending the call"""
        QMessageBox.information(self, "Call Ended", f"{self.peer_username} has ended the call")
        self.end_call(notify_peer=False)


        
    def setup_ui(self):
        """Setup enhanced call window UI"""
        self.setWindowTitle(f"Call with {self.peer_username}")
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Status section
        status_layout = QVBoxLayout()
        
        self.status_label = QLabel(f"In call with {self.peer_username}")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        status_layout.addWidget(self.status_label)
        
        self.duration_label = QLabel("00:00:00")
        self.duration_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.duration_label.setStyleSheet("color: #666;")
        status_layout.addWidget(self.duration_label)
        
        layout.addLayout(status_layout)
        
        # Audio levels section
        levels_layout = QHBoxLayout()
        
        # Local audio level
        local_level_layout = QVBoxLayout()
        local_level_layout.addWidget(QLabel("Your Audio:"))
        self.local_level_bar = QProgressBar()
        self.local_level_bar.setMaximum(100)
        self.local_level_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                width: 10px;
            }
        """)
        local_level_layout.addWidget(self.local_level_bar)
        levels_layout.addLayout(local_level_layout)
        
    
        layout.addLayout(levels_layout)
        
        # Controls section
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        
        # Mute button
        self.mute_button = QPushButton()
        self.mute_button.setCheckable(True)
        self.mute_button.setFixedSize(50, 50)
        self.mute_button.setStyleSheet("""
            QPushButton {
                border: 2px solid #666;
                border-radius: 25px;
                background-color: #fff;
            }
            QPushButton:checked {
                background-color: #ff9800;
            }
        """)
        self.mute_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume))
        self.mute_button.toggled.connect(self.handle_mute)
        controls_layout.addWidget(self.mute_button)
        
        # End call button
        self.end_button = QPushButton("End Call")
        self.end_button.setStyleSheet("""
            QPushButton {
                background-color: #ff4444;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff0000;
            }
        """)
        self.end_button.clicked.connect(self.handle_end_button)
        controls_layout.addWidget(self.end_button)
        
        layout.addLayout(controls_layout)
        


    def handle_end_button(self):
        """Handle end call button click"""
        self.end_call(notify_peer=True)
        self.close()




    def setup_duration_timer(self):
        """Setup timer for call duration"""
        self.duration_timer = QTimer(self)
        self.duration_timer.timeout.connect(self.update_duration)
        self.duration_timer.start(1000)  # Update every second
        

    def update_duration(self):
        """Update call duration display"""
        duration = self.call_start_time.secsTo(QDateTime.currentDateTime())
        hours = duration // 3600
        minutes = (duration % 3600) // 60
        seconds = duration % 60
        self.duration_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        

    def update_audio_level(self, level):
        """Update audio level indicators"""
        self.local_level_bar.setValue(int(level * 100))
        # Remote level is updated via the AudioStream class
        

    
    def handle_mute(self, muted):
        """Handle mute button toggle safely"""
        if hasattr(self, 'audio_stream'):
            self.audio_stream.set_muted(muted)
            if muted:
                self.mute_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolumeMuted))
                self.local_level_bar.setValue(0)
            else:
                self.mute_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume))


                
    def listen_for_end_call(self):
        """Listen for end call signal from peer"""
        self.end_call_socket.settimeout(1)
        while hasattr(self, 'audio_stream') and self.audio_stream.running:
            try:
                data, _ = self.end_call_socket.recvfrom(1024)
                if data.decode() == "END_CALL":
                    self.peer_ended_call()
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Error in end call listener: {e}")
                


    def peer_ended_call(self):
        """Handle peer ending the call"""
        QMessageBox.information(self, "Call Ended", f"Call has been ended by other user")
        self.end_call(notify_peer=False)
                
    
    def end_call(self, notify_peer=True):
        """End the call and notify peer if specified"""
        if notify_peer and hasattr(self, 'audio_stream'):
            try:
                self.audio_stream.send_end_call(self.peer_username)
            except Exception as e:
                print(f"Error in end_call notification: {e}")
        # Stop the audio stream
        if hasattr(self, 'audio_stream'):
            self.audio_stream.running = False
            self.audio_stream.wait()
        # Stop the timer    
        if self.duration_timer:
            self.duration_timer.stop()
        # Emit the end call signal
        self.call_ended.emit()



    def closeEvent(self, event):
        """Handle window close event (X button)"""
        self.end_call(notify_peer=True)  # Always notify peer when closing window
        super().closeEvent(event)
