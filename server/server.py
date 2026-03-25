import socket
import logging
from handler import ClientHandler

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class ChatServer:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.clients = []  # List to track active ClientHandlers

    def start(self):
        """Bind the socket to host/port and start listening."""
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        logging.info(f"Server listening on {self.host}:{self.port}")
        self.accept_clients()

    def accept_clients(self):
        """Continuously loop to accept incoming client connections."""
        try:
            while True:
                client_socket, client_address = self.server_socket.accept()
                logging.info(f"Client connected from {client_address}")
                
                # Spawn a new thread for the client
                handler = ClientHandler(client_socket, client_address, self)
                self.clients.append(handler)
                handler.start()

        except KeyboardInterrupt:
            logging.info("Server shutting down.")
            self.stop()

    def broadcast(self, message: str, sender=None):
        """Send a message to all connected clients."""
        logging.info(f"Broadcasting: {message.strip()}")
        for client in self.clients:
            if client != sender:
                try:
                    client.client_socket.sendall(message.encode('utf-8'))
                except Exception as e:
                    logging.error(f"Error broadcasting to {client.address}: {e}")
                    self.remove_client(client)

    def remove_client(self, client_handler):
        """Safely clean up and remove a disconnected client."""
        if client_handler in self.clients:
            self.clients.remove(client_handler)
            logging.info(f"Removed client {client_handler.address}. Total clients: {len(self.clients)}")

    def stop(self):
        """Gracefully shut down the server."""
        self.server_socket.close()

if __name__ == "__main__":
    server = ChatServer('127.0.0.1', 12345)
    server.start()
