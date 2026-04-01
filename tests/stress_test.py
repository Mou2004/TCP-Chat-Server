import socket
import json
import threading
import time
import random

# Configuration
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 12345
NUM_CLIENTS = 50
TEST_DURATION = 30  # seconds
MESSAGES_PER_SECOND_AVG = 0.5  # average messages per second per client

# Sample messages
RANDOM_MESSAGES = [
    "Hello everyone!",
    "How is the server holding up?",
    "Nice chat app!",
    "Is anyone here?",
    "The weather is nice today.",
    "Testing message latency.",
    "Python is great for this.",
    "Broadcasting to 50 clients!",
    "Stress test in progress...",
    "Random message #%d"
]

# Metrics
class Metrics:
    def __init__(self):
        self.total_sent = 0
        self.total_errors = 0
        self.latencies = []
        self.lock = threading.Lock()

    def add_latency(self, latency):
        with self.lock:
            self.latencies.append(latency)
            self.total_sent += 1

    def add_error(self):
        with self.lock:
            self.total_errors += 1

metrics = Metrics()

def simulate_client(index, stop_event):
    """A single simulated client."""
    client_id = f"Bot_{index:02d}"
    try:
        # Create socket and connect
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        sock.connect((SERVER_HOST, SERVER_PORT))

        # 1. Set Nickname
        nick_cmd = {
            "type": "command",
            "payload": {"command": "nick", "args": [client_id]}
        }
        sock.sendall((json.dumps(nick_cmd) + "\n").encode('utf-8'))
        time.sleep(0.5)  # Let server process nick

        while not stop_event.is_set():
            # Create a random message
            msg_text = random.choice(RANDOM_MESSAGES)
            if "%d" in msg_text:
                msg_text = msg_text % random.randint(1, 1000)
            
            payload = {
                "type": "message",
                "payload": {"text": msg_text}
            }
            
            # Send message and measure latency (time to send)
            start_time = time.time()
            try:
                sock.sendall((json.dumps(payload) + "\n").encode('utf-8'))
                metrics.add_latency(time.time() - start_time)
            except Exception:
                metrics.add_error()
                break
            
            # Randomized sleep to vary the load
            time.sleep(random.uniform(0.5, 2.0))

        # Close cleanly
        quit_cmd = {"type": "command", "payload": {"command": "quit"}}
        sock.sendall((json.dumps(quit_cmd) + "\n").encode('utf-8'))
        sock.close()

    except Exception as e:
        metrics.add_error()

def run_stress_test():
    """Spawns and monitors simulated clients."""
    print(f"Starting Stress Test: {NUM_CLIENTS} clients for {TEST_DURATION} seconds...")
    stop_event = threading.Event()
    threads = []

    for i in range(NUM_CLIENTS):
        t = threading.Thread(target=simulate_client, args=(i, stop_event))
        t.start()
        threads.append(t)
        # Small delay to avoid overwhelming the server during initial connection
        time.sleep(0.1)

    try:
        # Run the test for the configured duration
        time.sleep(TEST_DURATION)
    finally:
        # Signal threads to stop and join
        print("Stopping clients...")
        stop_event.is_set() # Wait, this should be set() 
        # Actually, let's just use stop_event.set()
        stop_event.set()
        for t in threads:
            t.join(timeout=2.0)

    # FINAL REPORT
    total_sent = metrics.total_sent
    total_errors = metrics.total_errors
    avg_latency = (sum(metrics.latencies) / len(metrics.latencies) * 1000) if metrics.latencies else 0
    
    print("\n" + "="*30)
    print("Stress Test Final Report")
    print("="*30)
    print(f"Total Clients Simulates:  {NUM_CLIENTS}")
    print(f"Test Duration:           {TEST_DURATION}s")
    print(f"Total Messages Sent:     {total_sent}")
    print(f"Total Errors Recorded:   {total_errors}")
    print(f"Average 'Send' Latency:  {avg_latency:.2f} ms")
    if metrics.latencies:
        print(f"Max 'Send' Latency:      {max(metrics.latencies)*1000:.2f} ms")
    print("="*30)

if __name__ == "__main__":
    run_stress_test()
