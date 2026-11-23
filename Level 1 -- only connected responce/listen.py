import socket

HOST = "0.0.0.0"
PORT = 4444

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind((HOST, PORT))
server.listen(1)

print(f"[*] Listening on {HOST}:{PORT}")

conn, addr = server.accept()

print(f"[+] Connection received from {addr}")

with conn:
    while True:
        data = conn.recv(4096)

        if not data:
            break

        print(data.decode(errors="replace"), end="")

server.close()
