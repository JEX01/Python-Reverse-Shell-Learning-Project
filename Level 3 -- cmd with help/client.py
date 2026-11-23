import socket
import sys

from protocol import MessageReader, encode_message

DEFAULT_HOST = "*"
DEFAULT_PORT = 4444


def receive_one_message(sock, reader):
    while True:
        # Check if an already-buffered chunk contains a full message
        for msg in reader.feed(b""):
            return msg

        data = sock.recv(4096)
        if not data:
            raise ConnectionError("Server closed the connection")

        messages = reader.feed(data)
        if messages:
            return messages[0]


def start_controller(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10.0)
    reader = MessageReader()

    try:
        print(f"[*] Connecting to {host}:{port}...")
        sock.connect((host, port))
        sock.settimeout(None)  # Wait as long as needed for command output
        print("[+] Connected")
        print("[*] Type 'help' to see available commands, or 'exit' to quit")

        message_id = 0

        while True:
            try:
                command = input("shell> ").strip()
            except EOFError:
                command = "exit"

            if not command:
                continue

            message_id += 1

            if command == "exit":
                sock.sendall(
                    encode_message(
                        {"type": "EXIT", "id": message_id, "payload": None}
                    )
                )
                break

            request = {
                "type": "COMMAND",
                "id": message_id,
                "payload": command,
            }
            sock.sendall(encode_message(request))

            response = receive_one_message(sock, reader)
            if response is None:
                print("[!] Received invalid response payload")
                continue

            payload = response.get("payload") or {}
            stdout = payload.get("stdout", "")
            stderr = payload.get("stderr", "")
            exit_code = payload.get("exit_code", 0)

            print("\n--- COMMAND OUTPUT ---")
            if stdout:
                print(stdout)
            if stderr:
                print(f"[ERROR] {stderr}")
            print(f"[EXIT CODE] {exit_code}")
            print("----------------------\n")

    except (ConnectionError, TimeoutError, OSError) as error:
        print(f"[-] {error}")
    finally:
        sock.close()


if __name__ == "__main__":
    target_host = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HOST
    target_port = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_PORT
    start_controller(target_host, target_port)