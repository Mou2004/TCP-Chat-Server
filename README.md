# TCP Chat Server

A multi-client TCP Chat Server made with Python to understand OS concepts, multi-threading, socket programming, and cryptography.

## Features
- **Multi-Client Support**: Handles multiple concurrent connections using Python's `threading` module.
- **JSON Protocol**: All messages and commands are structured as JSON for reliable parsing.
- **Command System**:
  - `/nick <name>`: Change your display name.
  - `/list`: See all connected users.
  - `/history <n>`: Retrieve the last `n` messages from the server logs.
  - `/quit`: Disconnect gracefully.
- **Persistent History**: All messages are logged to a `.jsonl` file with timestamps.

## To-Do
### Encryption 
- [ ] Step 16: RSA + AES Setup
- [ ] Step 17: Encrypt Messages

## Concepts Learnt
- **Sockets**: Using `socket` for low-level TCP/IP communication.
- **Threading**: Managing independent client sessions simultaneously.
- **Serialization**: Converting Python dictionaries to JSON strings for network transport.
- **Concurrency**: Handling race conditions and shared resources (like the client list).

## Usage
1. **Start the Server**: 
   ```bash
   python server/server.py
   ```
2. **Connect Clients**:
   ```bash
   python client/client.py
   ```



