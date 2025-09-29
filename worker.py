import socket
from simple_db import InMemoryDB

db = InMemoryDB()
db.inserir_usuario("JOAO DA SILVA", "11111111111")
db.set_saldo("11111111111", 25000)

COORD_HOST = "127.0.0.1"
COORD_PORT = 9009
WORKER_NAME = "worker-1"

def run_worker():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((COORD_HOST, COORD_PORT))
        s.sendall(f"<WORKER:ALIVE; NAME:{WORKER_NAME}>".encode())

        # Espera a task: "<USER:cpf; TASK:QUERY>"
        task = s.recv(2048).decode().strip()
        # Parse simples
        cpf = None
        if task.startswith("<") and task.endswith(">"):
            parts = [p.strip() for p in task[1:-1].split(";")]
            for p in parts:
                if p.startswith("USER:"):
                    cpf = p.split(":", 1)[1].strip()

        if not cpf:
            s.sendall(f"<WORKER:{WORKER_NAME}; TASK:QUERY; STATUS:NOK; ERR:invalid_task>".encode())
        else:
            # 3) CRIAR DEF QUE BUSQUE O SALDO DO USUARIO
            tupla = db.get_saldo(cpf)
            if not tupla:
                resp = f"<WORKER:{WORKER_NAME}; CPF:{cpf}; TASK:QUERY; STATUS:NOK>"
            else:
                nome, cpf, saldo, updated_at = tupla
                resp = f"<WORKER:{WORKER_NAME}; CPF:{cpf}; SALDO:{saldo}; UPDATED_AT:{updated_at}; TASK:QUERY; STATUS:OK>"
            s.sendall(resp.encode())

        # Recebe ACK final
        _ = s.recv(2048)

if __name__ == "__main__":
    run_worker()
