import threading
import socket
import utils

class ClientHandler(threading.Thread):
    def __init__(self, client_socket: socket.socket, address: tuple, server):
        super().__init__()
        self.client_socket = client_socket
        self.address = address
        self.server = server
        self.nickname = f"Guest_{address[1]}"
        from server import logger
        self.logger = logger

    def run(self):
        """Main listening loop for this specific client's TCP socket."""
        import traceback
        try:
            while True:
                data = self.client_socket.recv(4096)
                if not data:
                    break
                
                self.logger.info(f"[{self.address}] Received raw data: {data}")
                
                try:
                    # Message parsing using utils
                    message_data = utils.decode_json(data)
                    if not message_data:
                        continue

                    msg_type = message_data.get("type")
                    payload = message_data.get("payload", {})

                    if msg_type == "command":
                        if not self.handle_command(payload):
                            return # /quit returns False
                    elif msg_type == "message":
                        text = payload.get("text", "")
                        # Use utils.format_message for logging/broadcasting
                        formatted = utils.format_message(self.nickname, text)
                        self.logger.info(f"[{self.address}] {formatted}")
                        self.server.save_to_history(self.nickname, text)
                        self.server.broadcast(text, sender=self)
                        
                except Exception as e:
                    self.logger.error(f"[{self.address}] Error processing: {e}")
        except ConnectionResetError:
            pass
        except Exception as e:
            self.logger.error(f"Error handling client {self.address}: {e}")
        finally:
            # Broadcast user leaving before disconnecting
            self.server.broadcast(f"*** {self.nickname} has left the chat ***", message_type="event")
            self.disconnect()

    def handle_command(self, payload: dict) -> bool:
        """Process explicit slash commands (e.g., /nick, /list, /quit)."""
        command = payload.get("command")
        args = payload.get("args", [])

        if command == "nick":
            if not args:
                self.send_json("event", {"message": "Usage: /nick <name>"})
                return True
            
            new_nick = args[0].strip()
            # Use utils.validate_nickname
            if not utils.validate_nickname(new_nick):
                self.send_json("event", {"message": "Invalid nickname. Use 2-16 alphanumeric characters."})
            elif self.server.is_nickname_taken(new_nick):
                self.send_json("event", {"message": f"Error: Nickname '{new_nick}' is already taken."})
            else:
                old_nick = self.nickname
                self.nickname = new_nick
                self.server.broadcast(f"*** {old_nick} is now known as {self.nickname} ***", message_type="event")
                self.logger.info(f"[{self.address}] {old_nick} changed nickname to {self.nickname}")
        
        elif command == "list":
            nicks = [c.nickname for c in self.server.clients]
            self.send_json("event", {"message": f"Connected users: {', '.join(nicks)}"})
        
        elif command == "history":
            count = 10
            if args:
                try:
                    count = int(args[0])
                except ValueError:
                    pass
            
            history = self.server.get_history(count)
            if not history:
                self.send_json("event", {"message": "No chat history found."})
            else:
                history_str = "\n".join([f"[{h['timestamp'][:19]}] {h['sender']}: {h['text']}" for h in history])
                self.send_json("event", {"message": f"--- Last {len(history)} messages ---\n{history_str}"})

        elif command == "quit":
            return False # Break the loop
            
        else:
            self.send_json("event", {"message": f"Unknown command: /{command}"})
            
        return True

    def send_json(self, message_type: str, payload: dict):
        """Format and send a structured JSON packet to this client."""
        try:
            data = {
                "type": message_type,
                "payload": payload
            }
            # Use utils.encode_json
            self.client_socket.sendall(utils.encode_json(data))
        except Exception as e:
            self.logger.error(f"Error sending JSON to {self.address}: {e}")

    def disconnect(self):
        """Close this client's socket and remove them from the server."""
        self.logger.info(f"Client disconnected from {self.address}")
        self.server.remove_client(self)
        self.client_socket.close()
