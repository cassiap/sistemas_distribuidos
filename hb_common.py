import json
import socket

def send_json(sock: socket.socket, obj: dict):
    data = (json.dumps(obj, ensure_ascii=False) + "\n").encode("utf-8")
    sock.sendall(data)

def recv_json(sock: socket.socket, bufsize: int = 8192) -> dict | None:

    chunks = []
    while True:
        b = sock.recv(bufsize)
        if not b:
            break
        chunks.append(b)
        if b.endswith(b"\n") or b"\n" in b:
            break
    if not chunks:
        return None
    raw = b"".join(chunks).split(b"\n", 1)[0]
    try:
        return json.loads(raw.decode("utf-8"))
    except Exception:
        return None