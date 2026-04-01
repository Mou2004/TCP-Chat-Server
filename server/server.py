import socket
import os
import utils
from handler import ClientHandler

logger = utils.setup_logger()

class ChatServer:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.clients = []  # List to track active ClientHandlers
        self.history_file = "server/chat_history.jsonl"

    def save_to_history(self, sender: str, text: str):
        """Save a chat message with a timestamp to a JSONL file."""
        import json
        from datetime import datetime
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "sender": sender,
            "text": text
        }
        
        try:
            with open(self.history_file, "a", encoding='utf-8') as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            logger.error(f"Error saving message to history: {e}")

    def get_history(self, count: int = 10):
        """Retrieve the last N messages from the history file."""
        import json
        history = []
        if not os.path.exists(self.history_file):
            return []
            
        try:
            with open(self.history_file, "r", encoding='utf-8') as f:
                lines = f.readlines()
                start_index = max(0, len(lines) - count)
                for line in lines[start_index:]:
                    if line.strip():
                        history.append(json.loads(line))
        except Exception as e:
            logger.error(f"Error reading history: {e}")
            
        return history

    def start(self):
        """Bind the socket to host/port and start listening."""
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        logger.info(f"Server listening on {self.host}:{self.port}")
        self.accept_clients()

    def accept_clients(self):
        """Continuously loop to accept incoming client connections."""
        try:
            while True:
                client_socket, client_address = self.server_socket.accept()
                logger.info(f"Client connected from {client_address}")
                
                # Spawn a new thread for the client
                handler = ClientHandler(client_socket, client_address, self)
                self.clients.append(handler)
                handler.start()

        except KeyboardInterrupt:
            logger.info("Server shutting down.")
            self.stop()

    def broadcast(self, message: str, sender=None, message_type: str = "message"):
        """Send a message to all connected clients using the JSON protocol."""
        logger.info(f"Broadcasting {message_type}: {message.strip()}")
        import json
        inner_payload = {"text": message}
        payload = {
            "type": message_type,
            "payload": inner_payload
        }
        if message_type == "message" and sender:
            inner_payload["sender"] = sender.nickname

        raw_json_str = json.dumps(payload)

        data_to_send = (raw_json_str + "\n").encode('utf-8')
        for client in self.clients:
            if client != sender:
                try:
                    client.client_socket.sendall(data_to_send)
                except Exception as e:
                    logger.error(f"Error broadcasting to {client.address}: {e}")
                    self.remove_client(client)

    def is_nickname_taken(self, nickname: str) -> bool:
        """Check if a nickname is already in use by another client."""
        return any(client.nickname.lower() == nickname.lower() for client in self.clients)

    def remove_client(self, client_handler):
        """Safely clean up and remove a disconnected client."""
        if client_handler in self.clients:
            self.clients.remove(client_handler)
            logger.info(f"Removed client {client_handler.address}. Total clients: {len(self.clients)}")

    def stop(self):
        """Gracefully shut down the server."""
        self.server_socket.close()

if __name__ == "__main__":
    server = ChatServer('127.0.0.1', 12345)
    server.start()
