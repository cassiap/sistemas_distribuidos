import threading
import time
from dataclasses import dataclass, field
from typing import Dict

@dataclass
class ServerInfo:
    server_id: str
    host: str
    port: int
    last_seen: float = field(default_factory=time.time)
    status: str = "ALIVE"  # or "TIMEOUT"

class HeartbeatRegistry:
    def __init__(self, timeout_seconds: float = 10.0):
        self._lock = threading.Lock()
        self._servers: Dict[str, ServerInfo] = {}
        self._timeout = timeout_seconds

    def upsert(self, server_id: str, host: str, port: int):
        with self._lock:
            info = self._servers.get(server_id)
            if info is None:
                self._servers[server_id] = ServerInfo(server_id, host, port, time.time(), "ALIVE")
            else:
                info.last_seen = time.time()
                info.status = "ALIVE"

    def mark_timeouts(self):
        now = time.time()
        with self._lock:
            for info in self._servers.values():
                if now - info.last_seen > self._timeout:
                    info.status = "TIMEOUT"

    def snapshot(self):
        with self._lock:
            # return a shallow copy for display
            return {sid: vars(info).copy() for sid, info in self._servers.items()}