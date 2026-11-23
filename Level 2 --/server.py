
import socket
import threading

HOST = "0.0.0.0"
PORT = 4444


def handle_client(conn, address):
    print(f"\n[+] Connected: {address}")

    buffer = b""

    try:
        while True:
            data = conn.recv(4096)

            if not data:
                break

            buffer += data

            while b"\n" in buffer:
                message, buffer = buffer.split(b"\n", 1)
                message = message.decode("utf-8", errors="replace")

                print(f"[CLIENT] {message}")

                if message == "PING":
                    response = "PONG"
                else:
                    response = f"ACK: {message}"

                conn.sendall((response + "\n").encode())

    except (ConnectionError, OSError) as e:
        print(f"[-] Connection error: {e}")

    finally:
        conn.close()
        print(f"[-] Disconnected: {address}")


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server.bind((HOST, PORT))
    server.listen(5)

    print(f"[*] Listening on {HOST}:{PORT}")

    try:
        while True:
            conn, address = server.accept()

            thread = threading.Thread(
                target=handle_client,
                args=(conn, address),
                daemon=True
            )
            thread.start()

    except KeyboardInterrupt:
        print("\n[*] Server shutting down")

    finally:
        server.close()


if __name__ == "__main__":
    start_server()
