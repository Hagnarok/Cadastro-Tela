import os
import shutil
import time
import psutil

# Função para fechar o EXE se ele estiver em execução
def fechar_exe_se_em_execucao(nome_exe):
    for proc in psutil.process_iter():
        try:
            if nome_exe.lower() in proc.name().lower():
                print(f"Fechando o processo {nome_exe}...")
                proc.terminate()
                proc.wait()
                time.sleep(2)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

def substituir_exe():
    nome_exe = "Cadastro de Telas.exe"
    caminho_exe_area_trabalho = os.path.join(os.path.expanduser("~"), "Desktop", nome_exe)
    caminho_exe_novo = os.path.join(os.path.expanduser("~"), "Documents", "Cadastro Telas", "Cadastro de Telas Novo.exe")

    if os.path.exists(caminho_exe_novo):
        # Fechar o EXE se estiver em execução
        fechar_exe_se_em_execucao(nome_exe)

        # Substituir o EXE antigo pelo novo
        shutil.move(caminho_exe_novo, caminho_exe_area_trabalho)
        print(f"{nome_exe} foi substituído com sucesso na área de trabalho.")

        # Apagar o EXE novo da pasta Documentos
        os.remove(caminho_exe_novo)

        # Reiniciar o programa
        time.sleep(2)
        os.startfile(caminho_exe_area_trabalho)

    else:
        print("O novo EXE não foi encontrado em Documentos.")

if __name__ == "__main__":
    substituir_exe()
