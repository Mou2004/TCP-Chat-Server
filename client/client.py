import socket
import threading
import sys

class ChatClient:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = True

    def connect(self):
        """Establish a TCP connection to the server and spawn receive/send threads."""
        try:
            self.client_socket.connect((self.host, self.port))
            print(f"Connected to chat server at {self.host}:{self.port}")
            print("Type '/nick <name>' to change your name, or '/quit' to exit.")
            
            # Start a thread to listen for incoming messages
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()

            # The main thread handles sending user input
            self.send_messages()
            
        except ConnectionRefusedError:
            print(f"Connection refused by the server at {self.host}:{self.port}.")
        except Exception as e:
            print(f"Error connecting to server: {e}")

    def receive_messages(self):
        """Background thread loop: continuously listen for and display incoming messages."""
        try:
            while self.running:
                data = self.client_socket.recv(1024)
                if not data:
                    print("\nConnection closed by the server.")
                    self.running = False
                    break
                print(f"\r{data.decode('utf-8', errors='ignore').strip()}\n> ", end='', flush=True)
        except Exception as e:
            if self.running:
                print(f"\nError receiving message: {e}")
                
    def send_messages(self):
        """Main thread loop: capture user input from stdin and route it to the server."""
        try:
            while self.running:
                message = input("> ")
                if not message:
                    continue
                    
                self.client_socket.sendall(message.encode('utf-8'))
                
                if message.strip() == '/quit':
                    self.running = False
                    break
        except KeyboardInterrupt:
            self.running = False
        finally:
            self.disconnect()

    def disconnect(self):
        """Cleanly close the socket connection and exit the application."""
        self.running = False
        try:
            self.client_socket.close()
        except:
            pass
        print("Disconnected from server.")

if __name__ == "__main__":
    client = ChatClient('127.0.0.1', 12345)
    client.connect()
