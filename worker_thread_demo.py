import threading
import queue
import time

# Fila compartilhada
task_queue = queue.Queue()

def worker_thread(name: str):
    while True:
        try:
            item = task_queue.get(timeout=1.0)
        except queue.Empty:
            # Sai quando não tiver mais nada por um tempo (apenas para demo)
            print(f"[{name}] nenhuma tarefa, encerrando.")
            break
        try:
            print(f"[{name}] processando {item}...")
            time.sleep(0.5)  # simula trabalho
            print(f"[{name}] OK -> {item}")
        finally:
            task_queue.task_done()

if __name__ == "__main__":
    # Enfileira tarefas
    for i in range(10):
        task_queue.put(f"TASK-{i}")

    # Inicia 3 workers
    threads = [threading.Thread(target=worker_thread, args=(f"worker-{i}",)) for i in range(3)]
    for t in threads:
        t.start()

    # Espera fila esvaziar
    task_queue.join()
    # Aguarda threads finalizarem
    for t in threads:
        t.join()

    print("Fim da demo de worker thread.")
