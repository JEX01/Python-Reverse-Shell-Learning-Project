import os
import platform
import shlex
import socket

from protocol import MessageReader, encode_message

HOST = "0.0.0.0"
PORT = 4444

ALLOWED_COMMANDS = {"help", "pwd", "ls", "sysinfo", "echo"}


def execute_command(command):
    try:
        parts = shlex.split(command)

        if not parts:
            return {"stdout": "", "stderr": "", "exit_code": 0}

        name = parts[0]

        if name not in ALLOWED_COMMANDS:
            return {
                "stdout": "",
                "stderr": f"Command not allowed: {name}",
                "exit_code": 1,
            }

        if name == "help":
            output = "Available commands:\n" + "\n".join(
                f"  - {cmd}" for cmd in sorted(ALLOWED_COMMANDS)
            )
        elif name == "pwd":
            output = os.getcwd()
        elif name == "ls":
            output = "\n".join(sorted(os.listdir(".")))
        elif name == "sysinfo":
            output = (
                f"OS: {platform.system()}\n"
                f"Release: {platform.release()}\n"
                f"Version: {platform.version()}\n"
                f"Machine: {platform.machine()}"
            )
        elif name == "echo":
            output = " ".join(parts[1:])
        else:
            output = ""

        return {"stdout": output, "stderr": "", "exit_code": 0}

    except Exception as error:
        return {"stdout": "", "stderr": str(error), "exit_code": 1}


def handle_client(conn, address):
    print(f"\n[+] Client connected: {address}")
    reader = MessageReader()

    try:
        while True:
            data = conn.recv(4096)
            if not data:
                print("[-] Client disconnected")
                break

            for request in reader.feed(data):
                if request is None:
                    print("[!] Invalid JSON request received")
                    continue

                req_type = request["type"]
                req_id = request["id"]

                if req_type == "COMMAND":
                    command = request.get("payload", "")
                    if not isinstance(command, str):
                        result = {
                            "stdout": "",
                            "stderr": "Invalid command format",
                            "exit_code": 1,
                        }
                    else:
                        result = execute_command(command)

                    response = {
                        "type": "RESULT",
                        "id": req_id,
                        "payload": result,
                    }
                    conn.sendall(encode_message(response))

                elif req_type == "EXIT":
                    print("[*] Exit request received")
                    return

                else:
                    response = {
                        "type": "ERROR",
                        "id": req_id,
                        "payload": {
                            "stdout": "",
                            "stderr": f"Unknown request type: {req_type}",
                            "exit_code": 1,
                        },
                    }
                    conn.sendall(encode_message(response))

    except (ConnectionError, OSError) as error:
        print(f"[-] Connection error: {error}")
    finally:
        conn.close()
        print(f"[-] Connection closed: {address}")


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)

    print(f"[*] Listening on {HOST}:{PORT}")

    try:
        while True:
            conn, address = server.accept()
            handle_client(conn, address)
    except KeyboardInterrupt:
        print("\n[*] Server shutting down")
    finally:
        server.close()


if __name__ == "__main__":
    start_server()