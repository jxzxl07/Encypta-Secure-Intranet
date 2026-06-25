import json
import socket
import threading
from datetime import datetime

from PyQt5 import QtCore
from PyQt5.QtCore import QThread, pyqtSignal

from ..config import SERVER_IP, STATUS_SERVER_PORT


server_ip = SERVER_IP


class StatusServer:
    # Initialise the class for the server used by admin
    def __init__(self, host=server_ip, port=STATUS_SERVER_PORT):
        self.host = host
        self.port = port
        self.server_socket = None
        self.is_running = False
        self.clients = {}
        self.callback = None

    # Method called when start button is pressed    
    def start(self, status_callback):
        # Start the server and store callback for UI updates
        if self.is_running:
            return False   
        try:
            # Creating a server and listening for incoming requests
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.server_socket.settimeout(1)
            self.is_running = True
            self.callback = lambda: QtCore.QTimer.singleShot(0, status_callback)
            # Start listener thread
            self.listener_thread = threading.Thread(target=self._listen_for_connections)
            self.listener_thread.daemon = True
            self.listener_thread.start()
            return True
        except Exception as e:
            print(f"Server start failed: {e}")
            self.is_running = False
            return False

    # Method called when stop server button is pressed
    def stop(self):
         # Stop the server
        if not self.is_running:
            return False    
        try:
            self.is_running = False
            if self.server_socket:
                self.server_socket.close()
            return True
        except Exception as e:
            print(f"Server stop failed: {e}")
            return False

    # Method for listening to connections
    def _listen_for_connections(self):
        while self.is_running:
            # Accept new incoming connection request
            try:
                client_socket, address = self.server_socket.accept()
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()   
            except socket.timeout:
                continue
            except Exception as e:
                if self.is_running:  # Only log if not stopped intentionally
                    print(f"Connection accept failed: {e}")

    # Method for client request handling
    def _handle_client(self, client_socket, address):
        try:
            while self.is_running:
                data = client_socket.recv(1024)
                if not data:
                    break
                # Unpack the JSON message 
                message = json.loads(data.decode())
                if message['type'] == 'login':
                    self.clients[message['username']] = {
                        'ip': message['ip'],
                        'status': 'online',
                        'last_seen': datetime.now()
                    }
                elif message['type'] == 'logout':
                    if message['username'] in self.clients:
                        self.clients[message['username']]['status'] = 'offline'
                # Call UI callback to refresh display
                if self.callback:
                    self.callback()
        except Exception as e:
            print(f"Client handler error: {e}")
        finally:
            client_socket.close()

    def get_client_status(self):
        # Return current client status for UI display
        return self.clients
 

class CallServer(QThread):
    """TCP server to handle call signaling"""
    call_received = pyqtSignal(str, str)  # username, ip
    
    def __init__(self, call_port, audio_port):
        super().__init__()
        self.call_port = call_port
        self.audio_port = audio_port
        self.running = True
        
    def run(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind(('', self.call_port))
            server.listen(5)
            server.settimeout(1)
        except OSError as e:
            print(f"Call server bind error: {e}")
            server.close()
            return
        
        while self.running:
            try:
                client, addr = server.accept()
                data = client.recv(1024).decode()
                if data:
                    msg = json.loads(data)
                    if msg['type'] == 'call_request':
                        self.call_received.emit(msg['username'], addr[0])
                client.close()
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Call server error: {e}")
                
        server.close()


class VideoServer(QThread):
    video_call_received = pyqtSignal(str, str)  # username, ip
    error_signal = pyqtSignal(str)
    
    def __init__(self, port):
        super().__init__()
        self.port = port
        self.running = True
        
        # Setup TCP socket for signaling
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(('', port))
            self.socket.listen(5)
            self.socket.settimeout(1.0)  # Add timeout for checking running status
        except Exception as e:
            self.error_signal.emit(f"Failed to start video server: {e}")
            self.running = False
            
    def handle_client(self, client_socket, addr):
        """Handle individual client connections"""
        try:
            # Receive the request
            data = client_socket.recv(1024).decode()
            if data:
                request = json.loads(data)
                
                if request['type'] == 'video_call_request':
                    # Emit signal for incoming call
                    self.video_call_received.emit(request['username'], addr[0])
                    
                elif request['type'] == 'video_call_accepted':
                    # Handle call acceptance
                    response = {'type': 'video_call_started'}
                    client_socket.send(json.dumps(response).encode())
                    
                elif request['type'] == 'video_call_rejected':
                    # Handle call rejection
                    response = {'type': 'video_call_ended', 'reason': 'rejected'}
                    client_socket.send(json.dumps(response).encode())
                    
                elif request['type'] == 'end_call':
                    # Handle call ending
                    response = {'type': 'video_call_ended', 'reason': 'ended'}
                    client_socket.send(json.dumps(response).encode())
                    
        except Exception as e:
            print(f"Error handling client {addr}: {e}")
        finally:
            client_socket.close()
            
    def run(self):
        while self.running:
            try:
                # Accept new connections
                client_socket, addr = self.socket.accept()
                
                # Handle client in a new thread
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, addr)
                )
                client_thread.daemon = True
                client_thread.start()
                
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:  # Only show error if we're still supposed to be running
                    print(f"Server error: {e}")
                    self.error_signal.emit(f"Video server error: {e}")
                continue
                
    def stop(self):
        """Stop the server"""
        self.running = False
        try:
            # Create dummy connection to unblock accept()
            temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            temp_socket.connect(('localhost', self.port))
            temp_socket.close()
        except:
            pass
        
        self.socket.close()
        self.wait()
