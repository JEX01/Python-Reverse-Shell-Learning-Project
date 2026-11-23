import json


def encode_message(message):
    return (json.dumps(message) + "\n").encode("utf-8")


def decode_message(data):
    try:
        message = json.loads(data.decode("utf-8"))

        if not isinstance(message, dict):
            return None

        if not isinstance(message.get("type"), str):
            return None

        msg_id = message.get("id")
        if not isinstance(msg_id, int) or isinstance(msg_id, bool):
            return None

        return message

    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


class MessageReader:
    """Buffers TCP stream data and yields complete newline-delimited messages."""

    def __init__(self):
        self.buffer = b""

    def feed(self, chunk):
        self.buffer += chunk
        messages = []

        while b"\n" in self.buffer:
            raw, self.buffer = self.buffer.split(b"\n", 1)
            if raw.strip():
                messages.append(decode_message(raw))

        return messages