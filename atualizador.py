import os
import time
import shutil

def log(mensagem):
    with open(os.path.join(os.path.expanduser("~"), "Desktop", "atualizador_log.txt"), "a") as f:
        f.write(mensagem + "\n")

log("Atualizador iniciado")

# Espera até que o programa principal seja fechado
time.sleep(5)  # Pausa de 5 segundos para garantir que o programa foi encerrado

# Caminho do EXE na Área de Trabalho
caminho_exe_area_trabalho = os.path.join(os.path.expanduser("~"), "Desktop", "Cadastro de Telas.exe")
caminho_exe_novo = os.path.join(os.path.expanduser("~"), "Desktop", "Cadastro de Telas Novo.exe")

# Verificar se o EXE novo existe
if os.path.exists(caminho_exe_novo):
    log(f"Novo EXE encontrado: {caminho_exe_novo}")

    # Remover o EXE antigo, se existir
    if os.path.exists(caminho_exe_area_trabalho):
        log(f"Removendo o EXE antigo: {caminho_exe_area_trabalho}")
        os.remove(caminho_exe_area_trabalho)
    
    # Renomear o novo EXE
    log(f"Renomeando {caminho_exe_novo} para {caminho_exe_area_trabalho}")
    shutil.move(caminho_exe_novo, caminho_exe_area_trabalho)

    # Reiniciar o programa atualizado
    log(f"Reiniciando o programa: {caminho_exe_area_trabalho}")
    os.startfile(caminho_exe_area_trabalho)
else:
    log(f"Erro: {caminho_exe_novo} não foi encontrado.")
