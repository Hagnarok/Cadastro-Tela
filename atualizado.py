# -*- coding: utf-8 -*-
import os
import shutil
import time
import psutil
import tkinter as tk
from tkinter import ttk

# Função para fechar o EXE se ele estiver em execução
def fechar_exe_se_em_execucao(nome_exe):
    for proc in psutil.process_iter():
        try:
            if nome_exe.lower() in proc.name().lower():
                proc.terminate()
                proc.wait()
                time.sleep(2)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

# Função para substituir o EXE
def substituir_exe(progress):
    nome_exe = "Cadastro de Telas.exe"
    caminho_exe_area_trabalho = os.path.join(os.path.expanduser("~"), "Desktop", nome_exe)
    caminho_exe_novo = os.path.join(os.path.expanduser("~"), "Documents", "Cadastro Telas", "Cadastro de Telas Novo.exe")

    if os.path.exists(caminho_exe_novo):
        progress['value'] = 20
        root.update_idletasks()

        fechar_exe_se_em_execucao(nome_exe)
        
        progress['value'] = 50
        root.update_idletasks()

        shutil.move(caminho_exe_novo, caminho_exe_area_trabalho)
        progress['value'] = 90
        root.update_idletasks()

        time.sleep(2)
        os.startfile(caminho_exe_area_trabalho)

        time.sleep(1)
        root.destroy()  # Fechar a janela após a conclusão
    else:
        print("O novo EXE nao foi encontrado em Documentos.")
        root.destroy()

# Interface gráfica com barra de progresso
def iniciar_interface_atualizacao():
    global root
    root = tk.Tk()
    root.title("Atualizando Programa")
    root.geometry("400x100")
    root.resizable(False, False)

    label = tk.Label(root, text="Programa atualizando, aguarde...", font=("Arial", 12))
    label.pack(pady=10)

    progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
    progress.pack(pady=10)

    root.after(100, lambda: substituir_exe(progress))

    root.mainloop()

if __name__ == "__main__":
    iniciar_interface_atualizacao()
