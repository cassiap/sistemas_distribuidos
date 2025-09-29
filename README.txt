COMO RODAR (exercícios 1–4 + worker thread)

Requisitos: Python 3.10+

1) Abra dois terminais.

2) No Terminal A (Coordenador):
   python coordinator.py

3) No Terminal B (Worker):
   python worker.py

   Você verá no coordenador o log da mensagem do worker e, no worker,
   o handshake completo:
     - <WORKER:ALIVE; NAME:worker-1>
     - <USER:11111111111; TASK:QUERY>
     - <WORKER:worker-1; CPF:11111111111; SALDO:25000; UPDATED_AT:...; TASK:QUERY; STATUS:OK>
     - <COORD:ACK>

4) Para ver a DEMO de WORKER THREAD (fila + threads):
   python worker_thread_demo.py

OBSERVAÇÕES IMPORTANTES
- O "banco" é em memória (simple_db.py). Ele contém:
    inserir_usuario(nome, cpf)
    set_saldo(cpf, saldo)
    get_saldo(cpf) -> (nome, cpf, saldo, updated_at str) ou None
- Isso cumpre os itens: 1) inserir usuário, 2) inserir saldo, 3) def que busca saldo,
  4) simulação do protocolo coordenador/worker.
- Se quiser alterar HOST/PORT, edite em coordinator.py e worker.py.
