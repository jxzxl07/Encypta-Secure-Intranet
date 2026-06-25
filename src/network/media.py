
import collections
import json
import socket
import struct
import threading
import time

import cv2
import numpy as np
import pyaudio
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap


class AudioStream(QThread):
    """Handles audio streaming over UDP"""
    audio_level = pyqtSignal(float)
    call_ended_by_peer = pyqtSignal(str)  # New signal for call end notification
    

    def __init__(self, peer_ip, audio_port):
        super().__init__()
        self.peer_ip = peer_ip
        self.audio_port = audio_port
        self.running = True
        self.muted = False
        self.socket_closed = False
        
        # Audio settings
        self.chunk_size = 1024
        self.format = pyaudio.paFloat32
        self.channels = 1
        self.rate = 44100
        
        # Setup UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', self.audio_port))
        
        # Setup audio
        self.audio = pyaudio.PyAudio()
        self.setup_streams()

        
    def setup_streams(self):
        """Setup audio input and output streams"""
        self.input_stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )
        
        self.output_stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            output=True,
            frames_per_buffer=self.chunk_size
        )

    def set_muted(self, muted):
        """Safely handle mute state"""
        self.muted = muted
        
    def run(self):
        """Main audio streaming loop"""
        # Start receive thread
        receive_thread = threading.Thread(target=self.receive_audio)
        receive_thread.start()
        
        # Send audio
        while self.running:
            try:
                # Read from microphone
                data = self.input_stream.read(self.chunk_size, exception_on_overflow=False)
                
                # Only send if not muted
                if not self.muted:
                    # Send to peer
                    self.sock.sendto(data, (self.peer_ip, self.audio_port))
                    
                    # Calculate audio level
                    audio_array = np.frombuffer(data, dtype=np.float32)
                    level = float(np.abs(audio_array).mean())
                    self.audio_level.emit(level)
                else:
                    # Emit zero level when muted
                    self.audio_level.emit(0.0)
                    
            except Exception as e:
                print(f"Error sending audio: {e}")
                if not self.running:
                    break
                    
        receive_thread.join()
        self.cleanup()
        


    def receive_audio(self):
        """Receive and play audio from peer"""
        self.sock.settimeout(1)
        
        while self.running:
            try:
                data, addr = self.sock.recvfrom(self.chunk_size * 4)
                
                # Check if this might be a control message (they're typically much smaller than audio chunks)
                if len(data) < 100:  # Control messages are small
                    try:
                        # First character of json will be {
                        if data[0] == ord('{'):
                            message = json.loads(data.decode())
                            if message.get('type') == 'END_CALL':
                                self.running = False
                                self.call_ended_by_peer.emit(message.get('peer_name', 'Unknown user'))
                                break
                        else:
                            # Not JSON, treat as audio
                            self.output_stream.write(data)
                    except Exception as e:
                        # If any error occurs, assume it's audio data
                        self.output_stream.write(data)
                else:
                    # Regular audio data
                    self.output_stream.write(data)
                    
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Error in receive_audio: {e}")
                if not self.running:
                    break



    def send_end_call(self, peer_name):
        """Send end call notification"""
        if self.socket_closed:
            return
            
        try:
            # Create a control message
            end_message = json.dumps({
                'type': 'END_CALL',
                'peer_name': peer_name
            }).encode()
            
            # Send it multiple times to ensure delivery
            for _ in range(5):
                if not self.socket_closed:
                    self.sock.sendto(end_message, (self.peer_ip, self.audio_port))
                    time.sleep(0.1)
        except Exception as e:
            print(f"Error sending end call: {e}")

    def cleanup(self):
        """Clean up audio resources"""
        try:
            self.input_stream.stop_stream()
            self.input_stream.close()
            self.output_stream.stop_stream()
            self.output_stream.close()
            self.audio.terminate()
            self.socket_closed = True
            self.sock.close()
        except Exception as e:
            print(f"Error in cleanup: {e}")



class VideoSender(QThread):
    def __init__(self, cap, ip, port, label):
        super().__init__()
        self.cap = cap
        self.ip = ip
        self.port = port
        self.label = label
        self.running = True
        self.muted = False
        
        # Setup UDP socket with minimal buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Set smaller buffer size
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 32768)
        
    def run(self):
        while self.running:
            if not self.muted:
                ret, frame = self.cap.read()
                if ret:
                    # Reduce frame size even further
                    frame = cv2.resize(frame, (240, 180))
                    
                    # Display local video
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = rgb_frame.shape
                    q_img = QImage(rgb_frame.data, w, h, ch * w, QImage.Format_RGB888)
                    self.label.setPixmap(QPixmap.fromImage(q_img))
                    
                    try:
                        # Maximum compression
                        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 20])
                        data = buffer.tobytes()
                        
                        # Use very small chunks (1KB)
                        chunk_size = 1024
                        chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
                        
                        # Send frame metadata
                        header = struct.pack('!II', len(chunks), len(data))
                        self.socket.sendto(header, (self.ip, self.port))
                        
                        # Send chunks with minimal overhead
                        for i, chunk in enumerate(chunks):
                            # Just 2 bytes for sequence number to reduce overhead
                            header = struct.pack('!H', i)
                            packet = header + chunk
                            self.socket.sendto(packet, (self.ip, self.port))
                            # Larger delay between packets to prevent overwhelming
                            time.sleep(0.002)
                            
                    except Exception as e:
                        print(f"Error sending frame: {e}")
                        continue
                        
            time.sleep(0.05)  # Reduce to 20 FPS
            
    def mute(self):
        self.muted = True
        self.label.clear()
        self.label.setText("Camera Off")
        
    def unmute(self):
        self.muted = False
        
    def stop(self):
        self.running = False
        self.socket.close()
        self.wait()


class VideoReceiver(QThread):
    error_signal = pyqtSignal(str)
    
    def __init__(self, port, label):
        super().__init__()
        self.port = port
        self.label = label
        self.running = True
        
        # Setup UDP socket with minimal buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Set smaller receive buffer
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 32768)
        self.socket.settimeout(0.5)  # Shorter timeout
        
        try:
            self.socket.bind(('', port))
        except Exception as e:
            self.error_signal.emit(f"Failed to bind to port {port}: {e}")
            self.running = False
            
    def run(self):
        while self.running:
            try:
                # Receive frame metadata
                header, _ = self.socket.recvfrom(8)  # 8 bytes for two integers
                if not self.running:
                    break
                    
                num_chunks, total_size = struct.unpack('!II', header)
                
                # Initialize frame data
                chunks = {}
                start_time = time.time()
                
                # Collect chunks with timeout
                while len(chunks) < num_chunks and (time.time() - start_time) < 0.5:
                    try:
                        packet, _ = self.socket.recvfrom(1026)  # 2 bytes seq + 1024 data
                        seq_num = struct.unpack('!H', packet[:2])[0]
                        chunk = packet[2:]
                        chunks[seq_num] = chunk
                        
                    except socket.timeout:
                        continue
                    except Exception as e:
                        if "10040" not in str(e):  # Ignore buffer errors
                            print(f"Error receiving chunk: {e}")
                        break
                
                if not self.running:
                    break
                    
                # Process complete frames only
                if len(chunks) == num_chunks:
                    # Reconstruct frame data
                    ordered_chunks = [chunks[i] for i in range(num_chunks)]
                    data = b''.join(ordered_chunks)
                    
                    # Skip frame if data is incomplete
                    if len(data) != total_size:
                        continue
                        
                    # Decode and display frame
                    frame = cv2.imdecode(
                        np.frombuffer(data, dtype=np.uint8),
                        cv2.IMREAD_COLOR
                    )
                    
                    if frame is not None:
                        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        h, w, ch = rgb_frame.shape
                        q_img = QImage(
                            rgb_frame.data,
                            w, h, ch * w,
                            QImage.Format_RGB888
                        )
                        self.label.setPixmap(QPixmap.fromImage(q_img))
                    
            except socket.timeout:
                continue
            except Exception as e:
                if "10040" not in str(e):  # Only log non-buffer errors
                    print(f"Error in receiver: {e}")
                    self.label.setText("Connection Lost")
                time.sleep(0.1)
                
    def stop(self):
        self.running = False
        try:
            dummy_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            dummy_socket.sendto(b'stop', ('localhost', self.port))
            dummy_socket.close()
        except:
            pass
        self.socket.close()
        self.wait()


class AudioSender(QThread):
    def __init__(self, audio_stream, socket, ip, port, chunk_size):
        super().__init__()
        self.audio_stream = audio_stream
        self.socket = socket
        self.ip = ip
        self.port = port
        self.chunk_size = chunk_size
        self.running = True
        self.muted = False

    def run(self):
        while self.running:
            try:
                if not self.muted:
                    # Read audio data
                    data = self.audio_stream.read(self.chunk_size, exception_on_overflow=False)
                    
                    # Send audio data
                    try:
                        self.socket.sendto(data, (self.ip, self.port))
                    except Exception as e:
                        print(f"Error sending audio data: {e}")
                        
                # Small sleep to prevent CPU overload
                time.sleep(0.001)
                
            except Exception as e:
                print(f"Error in audio sender: {e}")
                time.sleep(0.1)  # Sleep longer on error

    def mute(self):
        self.muted = True

    def unmute(self):
        self.muted = False

    def stop(self):
        self.running = False
        self.wait()


class AudioReceiver(QThread):
    def __init__(self, audio_output, port, format, channels, rate, chunk_size):
        super().__init__()
        self.audio_output = audio_output
        self.port = port
        self.format = format
        self.channels = channels
        self.rate = rate
        self.chunk_size = chunk_size
        self.running = True
        
        # Setup socket for receiving audio
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('', port))
        self.socket.settimeout(0.2)  # Short timeout for responsiveness
        
        # Setup audio output stream
        self.output_stream = self.audio_output.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            output=True,
            frames_per_buffer=self.chunk_size
        )
        
        # Setup jitter buffer
        self.jitter_buffer = collections.deque(maxlen=10)  # Buffer 10 chunks max
        self.buffer_target = 3  # Target number of chunks in buffer

    def run(self):
        while self.running:
            try:
                # Receive audio data
                try:
                    data, _ = self.socket.recvfrom(self.chunk_size * 2)  # Extra space for safety
                    self.jitter_buffer.append(data)
                except socket.timeout:
                    # No data received, check if we need to play from buffer
                    pass
                except Exception as e:
                    print(f"Error receiving audio data: {e}")
                    continue

                # Process buffered audio
                self.process_buffer()
                
                # Small sleep to prevent CPU overload
                time.sleep(0.001)
                
            except Exception as e:
                print(f"Error in audio receiver: {e}")
                time.sleep(0.1)  # Sleep longer on error

    def process_buffer(self):
        """Process audio from jitter buffer"""
        try:
            # Play audio if we have enough data
            if len(self.jitter_buffer) >= self.buffer_target:
                data = self.jitter_buffer.popleft()
                self.output_stream.write(data)
            elif len(self.jitter_buffer) > 0 and self.running:
                # Buffer running low, play anyway to reduce latency
                data = self.jitter_buffer.popleft()
                self.output_stream.write(data)
                
        except Exception as e:
            print(f"Error processing audio buffer: {e}")

    def stop(self):
        self.running = False
        try:
            # Send dummy packet to unblock recvfrom
            temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            temp_socket.sendto(b'', ('localhost', self.port))
            temp_socket.close()
        except:
            pass
            
        # Clean up audio stream
        if hasattr(self, 'output_stream'):
            try:
                self.output_stream.stop_stream()
                self.output_stream.close()
            except:
                pass
                
        self.socket.close()
        self.wait()
