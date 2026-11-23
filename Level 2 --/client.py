
import socket
import threading
import time
import queue

SERVER = "*"
PORT = 4444

RECONNECT_DELAY = 3
HEARTBEAT_INTERVAL = 15

messages = queue.Queue()
running = True


def input_handler():
    while running:
        try:
            message = input()

            if message == "/quit":
                messages.put(None)
                break

            if message:
                messages.put(message)

        except EOFError:
            messages.put(None)
            break


def run_client():
    global running

    threading.Thread(
        target=input_handler,
        daemon=True
    ).start()

    while running:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            print(f"[*] Connecting to {SERVER}:{PORT}...")
            sock.connect((SERVER, PORT))
            sock.settimeout(1)

            print("[+] Connected successfully")

            buffer = b""
            last_heartbeat = time.monotonic()

            while running:

                # Receive server messages
                try:
                    data = sock.recv(4096)

                    if not data:
                        raise ConnectionError("Server disconnected")

                    buffer += data

                    while b"\n" in buffer:
                        response, buffer = buffer.split(b"\n", 1)
                        print("[SERVER]", response.decode())

                except socket.timeout:
                    pass

                # Send queued messages
                while not messages.empty():
                    message = messages.get()

                    if message is None:
                        running = False
                        break

                    sock.sendall((message + "\n").encode())

                if not running:
                    break

                # Heartbeat
                if time.monotonic() - last_heartbeat >= HEARTBEAT_INTERVAL:
                    sock.sendall(b"PING\n")
                    last_heartbeat = time.monotonic()

        except (ConnectionError, OSError) as e:
            print(f"[-] Disconnected: {e}")

        finally:
            sock.close()

        if running:
            print(f"[*] Reconnecting in {RECONNECT_DELAY} seconds...")
            time.sleep(RECONNECT_DELAY)

    print("[*] Client stopped")


if __name__ == "__main__":
    try:
        run_client()
    except KeyboardInterrupt:
        running = False
        print("\n[*] Client stopped")
