import socket

LHOST = "*"
LPORT = 4444

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client.connect((LHOST, LPORT))
    print("[+] Connected to listener")

    client.sendall(b"Python client connected successfully\n")

except ConnectionRefusedError:
    print("[-] Listener is not running")

except Exception as e:
    print(f"[-] Error: {e}")

finally:
    client.close()