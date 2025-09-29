import argparse
import socket
import threading
import time
import uuid
from typing import List, Tuple

from hb_common import send_json, recv_json
from registry import HeartbeatRegistry

# Protocol (Sprint 1)
# A -> B: {"TASK": "HEARTBEAT"}
# B -> A: {"TASK":"HEARTBEAT","RESPONSE":"ALIVE","SERVER_ID":"<UUID_B>"}
#
# Obs.: isso permite descoberta: A não precisa saber o UUID_B; aprende na resposta.

class Node:
    def __init__(self, host: str, port: int, peers: List[Tuple[str,int]], timeout: float = 10.0, interval: float = 2.0):
        self.host = host
        self.port = port
        self.node_id = str(uuid.uuid4())
        self.peers = peers
        self.registry = HeartbeatRegistry(timeout_seconds=timeout)
        self.interval = interval
        self._stop = threading.Event()

    # --- server (listener) ---
    def _client_handler(self, conn: socket.socket, addr):
        with conn:
            msg = recv_json(conn)
            if not msg:
                return
            # Only HEARTBEAT in Sprint 1
            if msg.get("TASK") == "HEARTBEAT":
                # responde com ALIVE e nosso UUID
                send_json(conn, {"TASK":"HEARTBEAT", "RESPONSE":"ALIVE", "SERVER_ID": self.node_id})
            # Nada além de heartbeat nesta sprint

    def _server_loop(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            s.listen()
            print(f"[{self.node_id[:8]}] Listening on {self.host}:{self.port}")
            while not self._stop.is_set():
                try:
                    s.settimeout(1.0)
                    conn, addr = s.accept()
                except socket.timeout:
                    continue
                t = threading.Thread(target=self._client_handler, args=(conn, addr), daemon=True)
                t.start()

    # --- client (pinger) ---
    def _ping_once(self, peer_host: str, peer_port: int):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as c:
                c.settimeout(2.0)
                c.connect((peer_host, peer_port))
                send_json(c, {"TASK":"HEARTBEAT"})
                resp = recv_json(c)
                if resp and resp.get("TASK") == "HEARTBEAT" and resp.get("RESPONSE") == "ALIVE":
                    sid = resp.get("SERVER_ID", f"{peer_host}:{peer_port}")
                    self.registry.upsert(sid, peer_host, peer_port)
        except OSError:
            # peer offline: vai marcar timeout naturalmente na varredura
            pass

    def _pinger_loop(self):
        while not self._stop.is_set():
            for (h,p) in self.peers:
                self._ping_once(h,p)
            self.registry.mark_timeouts()
            snap = self.registry.snapshot()
            if snap:
                print(f"[{self.node_id[:8]}] registry:", snap)
            time.sleep(self.interval)

    def start(self):
        self._stop.clear()
        threading.Thread(target=self._server_loop, daemon=True).start()
        threading.Thread(target=self._pinger_loop, daemon=True).start()

    def run_forever(self):
        self.start()
        try:
            while True:
                time.sleep(0.5)
        except KeyboardInterrupt:
            self._stop.set()

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Sprint1: HEARTBEAT contínuo com timeout")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, required=True)
    ap.add_argument("--peer", action="append", default=[], help="peer no formato host:port (pode repetir)")
    ap.add_argument("--timeout", type=float, default=10.0, help="segundos sem ver ALIVE para marcar TIMEOUT")
    ap.add_argument("--interval", type=float, default=2.0, help="intervalo entre batidas de HEARTBEAT")
    args = ap.parse_args()

    peers: List[Tuple[str,int]] = []
    for p in args.peer:
        host, port = p.split(":")
        peers.append((host, int(port)))

    node = Node(args.host, args.port, peers, timeout=args.timeout, interval=args.interval)
    node.run_forever()