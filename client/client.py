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
        import json
        try:
            while self.running:
                data = self.client_socket.recv(4096)
                if not data:
                    if self.running:
                        print("\nConnection closed by the server.")
                    self.running = False
                    break
                
                try:
                    # Messages are JSON-encoded and newline-terminated
                    raw_messages = data.decode('utf-8').split('\n')
                    for raw_msg in raw_messages:
                        if not raw_msg.strip():
                            continue
                        
                        message_data = json.loads(raw_msg)
                        msg_type = message_data.get("type")
                        payload = message_data.get("payload", {})

                        if msg_type == "message":
                            sender = payload.get("sender", "Server")
                            text = payload.get("text", "")
                            print(f"\r{sender}: {text}\n> ", end='', flush=True)
                        elif msg_type == "event":
                            message = payload.get("message", "")
                            print(f"\r{message}\n> ", end='', flush=True)
                            
                except json.JSONDecodeError:
                    # Fallback for plain text (to avoid crashing if server sends something unexpected)
                    pass

        except Exception as e:
            if self.running:
                print(f"\nError receiving message: {e}")
                
    def send_messages(self):
        """Main thread loop: capture user input from stdin and route it to the server."""
        import json
        try:
            while self.running:
                message = input("> ")
                if not message:
                    continue
                
                payload = {}
                if message.startswith('/'):
                    parts = message.split(' ', 1)
                    command = parts[0][1:] # Remove /
                    args = parts[1].split(' ') if len(parts) > 1 else []
                    payload = {
                        "type": "command",
                        "payload": {
                            "command": command,
                            "args": args
                        }
                    }
                    if command == 'quit':
                        self.running = False
                else:
                    payload = {
                        "type": "message",
                        "payload": {
                            "text": message
                        }
                    }
                    
                data_to_send = (json.dumps(payload) + "\n").encode('utf-8')
                self.client_socket.sendall(data_to_send)

                if not self.running:
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
