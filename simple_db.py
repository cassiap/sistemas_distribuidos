import threading
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class User:
    nome: str
    cpf: str
    saldo: int = 0
    updated_at: datetime = field(default_factory=datetime.utcnow)

class InMemoryDB:

    def __init__(self):
        self._lock = threading.Lock()
        self._users = {}

    # 1) INSERIR O USUARIO
    def inserir_usuario(self, nome: str, cpf: str) -> None:
        with self._lock:
            if cpf not in self._users:
                self._users[cpf] = User(nome=nome, cpf=cpf)
            else:
                # Atualiza apenas o nome se já existir (opcional)
                self._users[cpf].nome = nome
                self._users[cpf].updated_at = datetime.utcnow()

    # 2) INSERIR/ATUALIZAR O SALDO DO USUÁRIO
    def set_saldo(self, cpf: str, saldo: int) -> bool:
        with self._lock:
            u = self._users.get(cpf)
            if not u:
                return False
            u.saldo = int(saldo)
            u.updated_at = datetime.utcnow()
            return True

    # 3) DEF QUE BUSCA O SALDO DO USUÁRIO
    # Recebe cpf e retorna tupla (nome, cpf, saldo, updated_at) ou None se não existir
    def get_saldo(self, cpf: str):
        with self._lock:
            u = self._users.get(cpf)
            if not u:
                return None
            return (u.nome, u.cpf, u.saldo, u.updated_at.isoformat() + "Z")

    # Utilitário p/ debug
    def count(self) -> int:
        with self._lock:
            return len(self._users)
