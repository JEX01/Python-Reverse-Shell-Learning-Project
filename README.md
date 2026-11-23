# Python Reverse Shell — Three-Level Learning Project

A progressive Python cybersecurity learning project exploring the building blocks behind reverse connections and remote command interfaces.

The project is organized into three levels, moving from a basic reverse TCP connection to persistent communication and finally to a structured, **allowlisted remote command simulator**.

> **Scope:** This repository documents a controlled learning implementation. Level 3 does not provide an unrestricted operating-system shell: it accepts only the predefined commands listed below. Use the code only in systems and networks you own or are explicitly authorized to test.

## Project progression

| Level | Stage | What it demonstrates |
|---|---|---|
| 1 | Basic Reverse TCP Connection | A client initiates a connection back to a listening server and sends an initial message. |
| 2 | Persistent Reverse Connection | The client maintains a connection, exchanges messages, sends heartbeats and attempts to reconnect after a disconnect. |
| 3 | Interactive Remote Command Simulator | A controller sends structured command requests; the server processes an allowlist and returns output and exit codes. |

## Repository structure

Keep each level in a separate directory. The same filenames can be reused without overwriting another level's implementation.

```text
python-reverse-shell-learning/
├── README.md
├── level-1/
│   ├── client.py
│   └── server.py
├── level-2/
│   ├── client.py
│   └── server.py
└── level-3/
    ├── controller.py
    ├── server.py
    └── protocol.py
```

---

## Level 1 — Basic Reverse TCP Connection

**Objective:** Understand the basic reverse-connection pattern: the listening program waits for an incoming TCP connection, while the client initiates the connection to the listener.

### How it works

1. The server creates a TCP socket and binds to a listening interface and port.
2. The server waits for an incoming connection.
3. The client connects to the server's IP address and port.
4. The client sends a short confirmation message.
5. The server receives and displays the message.

### Concepts covered

- TCP socket creation
- `bind()`, `listen()` and `accept()`
- Client-side `connect()`
- Sending and receiving bytes with `sendall()` and `recv()`
- Basic connection error handling
- Closing sockets cleanly

### Run

On the listener/server machine:

```bash
python server.py
```

On the client machine, configure the listener address in `client.py`, then run:

```bash
python client.py
```

**Expected result:** The server reports the connecting client's address and displays the initial message.

---

## Level 2 — Persistent Reverse Connection

**Objective:** Extend the basic reverse connection so it can remain open and carry multiple messages.

### How it works

1. The server listens for incoming TCP connections.
2. The client connects to the server.
3. Both sides exchange newline-delimited messages over the established connection.
4. The client sends a periodic `PING` heartbeat.
5. The server responds with `PONG`.
6. If the connection is lost, the client detects the failure and attempts to reconnect after a delay.

### Concepts covered

- Persistent TCP sessions
- Newline-delimited message framing
- Bidirectional message exchange
- Heartbeat messages (`PING` / `PONG`)
- Reconnection logic
- Socket timeouts and disconnect handling
- Background input thread
- `queue.Queue` for passing input to the networking loop
- Server-side client-handling threads

### Run

Start the server:

```bash
python server.py
```

Start the client in another terminal:

```bash
python client.py
```

Type messages in the client terminal and observe the server's output and acknowledgements. Use `/quit` to stop the client input loop. Stop the server with `Ctrl+C`.

---

## Level 3 — Interactive Remote Command Simulator

**Objective:** Introduce a structured request/response protocol and demonstrate how a remote command interface can be built with strict command restrictions.

**Important:** This level is an allowlisted command simulator, not a general-purpose reverse shell. It does not pass user input to an operating-system shell or execute arbitrary commands.

### Allowed commands

| Command | Behaviour |
|---|---|
| `help` | Lists the available commands. |
| `pwd` | Displays the server process's current working directory. |
| `ls` | Lists entries in the server process's current directory. |
| `sysinfo` | Displays basic operating-system information. |
| `echo <text>` | Returns the supplied text. |
| `exit` | Ends the controller session. |

Commands outside the allowlist are rejected.

### How it works

1. The server listens for an incoming TCP connection.
2. The controller connects to the server.
3. The controller reads a command from the `shell>` prompt.
4. The command is sent as a JSON request with a message ID.
5. The server parses the request and checks the command against its allowlist.
6. The server runs the matching predefined handler.
7. The server returns a JSON response containing output, error text and an exit code.
8. The controller displays the response.

The `shell>` text is only a user-interface prompt; it does not mean arbitrary shell commands are supported.

### Files

- `controller.py` — connects to the server, sends requests and displays responses.
- `server.py` — accepts requests, enforces the command allowlist and returns results.
- `protocol.py` — encodes, decodes and buffers newline-delimited JSON messages.

### Example request

```json
{
  "type": "COMMAND",
  "id": 1,
  "payload": "sysinfo"
}
```

### Example response

```json
{
  "type": "RESULT",
  "id": 1,
  "payload": {
    "stdout": "Operating-system information",
    "stderr": "",
    "exit_code": 0
  }
}
```

The output shown above is illustrative; actual system information depends on the machine running the server.

### Run

Start the server on the machine that will process the allowlisted commands:

```bash
python server.py
```

In a second terminal, start the controller and provide the server's reachable IP address and port:

```bash
python controller.py <SERVER_IP> 4444
```

Example for a private lab network:

```bash
python controller.py 192.168.176.132 4444
```

At the prompt, try:

```text
shell> help
shell> pwd
shell> ls
shell> sysinfo
shell> echo hello
shell> exit
```

---

## Configuration

- The server binds to `0.0.0.0`, meaning it listens on all available IPv4 interfaces.
- The controller must connect to the server's reachable IP address. `0.0.0.0` is a bind address, not the address to use as the remote destination.
- A private address such as `192.168.x.x` is specific to a local network and will not work for other users cloning the repository.
- Prefer passing the server address as a command-line argument or using an environment variable rather than committing a machine-specific IP address.
- Never commit passwords, tokens, private keys or other secrets.

## Requirements

- Python 3
- No third-party packages are required by the code described here.

## Learning outcomes

By completing the three levels, you practise:

1. Building a TCP listener and a client-initiated reverse connection.
2. Exchanging data over a TCP stream.
3. Maintaining a connection for repeated communication.
4. Implementing heartbeats and reconnect handling.
5. Using threads and queues for input handling.
6. Designing a newline-delimited JSON protocol.
7. Handling request IDs, structured responses and exit codes.
8. Validating requests and restricting server-side functionality.

## Security and responsible use

This project is for educational use in a controlled lab. Run it only on systems and networks you own or have explicit permission to test.

The Level 3 server deliberately implements a fixed allowlist and does not execute arbitrary operating-system commands. Do not expose a learning listener to untrusted networks or treat this project as a secure remote-administration product.

For legitimate remote administration, use an established, authenticated and encrypted solution such as SSH.

## Technical note: TCP message boundaries

TCP provides a byte stream; a single `send()` does not necessarily correspond to a single `recv()`. Level 2 uses newline-delimited messages, and Level 3's `MessageReader` buffers incoming bytes until it has a complete newline-terminated JSON message.
