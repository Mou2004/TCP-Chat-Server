import threading
import socket
import json
import logging

class ClientHandler(threading.Thread):
    def __init__(self, client_socket: socket.socket, address: tuple, server):
        super().__init__()
        self.client_socket = client_socket
        self.address = address
        self.server = server
        self.nickname = f"Guest_{address[1]}"

    def run(self):
        """Main listening loop for this specific client's TCP socket."""
        try:
            while True:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                
                # Log and process the client's message
                try:
                    message = data.decode('utf-8').strip()
                    if message:
                        if message.startswith('/nick '):
                            old_nick = self.nickname
                            self.nickname = message.split(' ', 1)[1].strip()
                            self.server.broadcast(f"*** {old_nick} is now known as {self.nickname} ***\n")
                            logging.info(f"[{self.address}] {old_nick} changed nickname to {self.nickname}")
                        elif message == '/quit':
                            break  # Will close connection cleanly in the finally block
                        else:
                            logging.info(f"[{self.address}] {self.nickname}: {message}")
                            self.server.broadcast(f"{self.nickname}: {message}\n", sender=self)
                except UnicodeDecodeError:
                    logging.info(f"[{self.address}] {self.nickname} sent non-utf8 data.")
                    
        except ConnectionResetError:
            pass  # Client disconnected abruptly
        except Exception as e:
            logging.error(f"Error handling client {self.address}: {e}")
        finally:
            self.disconnect()

    def handle_command(self, payload: dict):
        """Process explicit slash commands (e.g., /nick, /list, /quit)."""
        pass

    def handle_message(self, payload: dict):
        """Process and broadcast a standard chat message from this client."""
        pass

    def send_json(self, message_type: str, payload: dict):
        """Format and send a structured JSON packet to this client."""
        pass

    def disconnect(self):
        """Close this client's socket and remove them from the server."""
        logging.info(f"Client disconnected from {self.address}")
        self.server.remove_client(self)
        self.client_socket.close()
