import socket
import threading
from simple_db import InMemoryDB

HOST = "127.0.0.1"
PORT = 9009
THRESHOLD = 10  # limiar de filas/pedidos pendentes (simulado)

db = InMemoryDB()

# Pré-carrega o usuário do exercício
db.inserir_usuario("JOAO DA SILVA", "11111111111")
db.set_saldo("11111111111", 25000)

def handle_worker(conn, addr):

    with conn:
        try:
            raw = conn.recv(2048).decode().strip()
            # Espera a flag <WORKER:ALIVE; NAME:...>
            if not raw.startswith("<WORKER:ALIVE"):
                conn.sendall(b"ERR: expected <WORKER:ALIVE; NAME:...>")
                return

            # (Opcional) extrair nome do worker
            name = "unknown"
            for part in raw.strip("<> ").split(";"):
                part = part.strip()
                if part.startswith("NAME:"):
                    name = part.split(":", 1)[1].strip()

            # Envia a "task": consultar saldo do Joao
            task = "<USER:11111111111; TASK:QUERY>"
            conn.sendall(task.encode())

            # Aguarda resposta do worker
            data = conn.recv(4096).decode().strip()

            # (Opcional) valida formato e loga
            print(f"[COORD] From {addr} -> {data}")

            # Fecha com ACK
            conn.sendall(b"<COORD:ACK>")
        except Exception as e:
            conn.sendall(f"ERR: {e}".encode())

def start_server():
    print(f"[COORD] Listening on {HOST}:{PORT}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()

        while True:
            conn, addr = s.accept()
            t = threading.Thread(target=handle_worker, args=(conn, addr), daemon=True)
            t.start()

if __name__ == "__main__":
    start_server()
