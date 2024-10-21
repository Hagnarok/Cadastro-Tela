import tkinter as tk
from tkinter import messagebox
import smtplib
from email.message import EmailMessage
from datetime import datetime
import threading
from PIL import Image, ImageTk
import re
import os
import shutil
import sys
import sqlite3
import requests
from packaging import version
import psutil
import time
import subprocess
import hashlib
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64

# Caminho para a pasta "Cadastro Telas" dentro de "Documentos"
pasta_documentos = os.path.join(os.path.expanduser("~"), "Documents", "Cadastro Telas")

# Certifica-se de que a pasta "Cadastro Telas" existe
if not os.path.exists(pasta_documentos):
    os.makedirs(pasta_documentos)

# Caminho completo para o arquivo 'versao.txt' local
arquivo_versao_local = os.path.join(pasta_documentos, 'versao.txt')

# Caminho completo para o arquivo 'atualizado.py' local
caminho_atualizado = os.path.join(pasta_documentos, 'atualizado.py')

# Caminho do executável
caminho_exe_atualizado = os.path.join(pasta_documentos, 'atualizado.exe')

# URL do repositório no GitHub (ajustado)
URL_REPOSITORIO = 'https://raw.githubusercontent.com/Hagnarok/Cadastro-Tela/main/'


# Função para fechar o EXE se estiver em execução
def fechar_exe_se_em_execucao(nome_exe):
    for proc in psutil.process_iter():
        try:
            if nome_exe.lower() in proc.name().lower():
                print(f"Fechando o processo {nome_exe}...")
                proc.terminate()  # Fechar o processo
                proc.wait()  # Esperar até o processo ser fechado
                print(f"{nome_exe} fechado.")
                time.sleep(2)  # Pausa de 2 segundos para garantir que o processo foi encerrado
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

# Função para calcular o hash MD5 de um arquivo
def calcular_hash_arquivo(caminho_arquivo):
    hash_md5 = hashlib.md5()
    try:
        with open(caminho_arquivo, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except FileNotFoundError:
        return None

# Função para substituir o EXE corretamente na Área de Trabalho
def substituir_exe():
    try:
        nome_exe_novo = "Cadastro de Telas Novo.exe"
        caminho_exe_novo = os.path.join(os.path.expanduser("~"), "Documents", "Cadastro Telas", nome_exe_novo)

        # URL do EXE no GitHub Releases (link direto)
        URL_EXE = "https://github.com/Hagnarok/Cadastro-Tela/releases/download/v1.0.0/Cadastro.de.Telas.exe"

        # Fazer o download do novo EXE
        resposta = requests.get(URL_EXE, stream=True)

        if resposta.status_code == 200:
            # Salvar o novo EXE na pasta Documentos
            with open(caminho_exe_novo, 'wb') as f:
                for chunk in resposta.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Novo EXE baixado e salvo como {caminho_exe_novo}")

            # Definir o caminho do EXE original na Área de Trabalho
            caminho_exe_atual = os.path.join(os.path.expanduser("~"), "Desktop", "Cadastro de Telas.exe")

            # Localizando o arquivo 'atualizado.exe' empacotado
            if getattr(sys, 'frozen', False):
                # Diretório temporário onde o PyInstaller extrai os arquivos
                bundle_dir = sys._MEIPASS
            else:
                # Diretório onde o script Python está rodando (se não estiver congelado)
                bundle_dir = os.path.dirname(os.path.abspath(__file__))

            # Caminho completo do 'atualizado.exe' empacotado
            caminho_atualizador_exe = os.path.join(bundle_dir, 'atualizado.exe')

            # Chamar o atualizador para substituir o EXE e passar os caminhos necessários
            subprocess.Popen([caminho_atualizador_exe, caminho_exe_novo, caminho_exe_atual])

            # Encerrar o programa principal para permitir a substituição
            print("Encerrando o programa principal para permitir a substituição do EXE...")
            sys.exit()

        else:
            messagebox.showinfo('Erro', f"Erro ao baixar o EXE. Status: {resposta.status_code}")
            print(f"Erro ao baixar o EXE. Status: {resposta.status_code}")

    except Exception as e:
        messagebox.showinfo('Erro', f"Erro ao substituir o EXE: {e}")
        print(f"Erro ao substituir o EXE: {e}")

# Função para verificar se há uma nova versão disponível
def verificar_atualizacao():
    try:
        url_versao_remota = URL_REPOSITORIO + 'versao.txt'
        print(f"Verificando a URL: {url_versao_remota}")

        resposta = requests.get(url_versao_remota)
        print(f"Status da requisição: {resposta.status_code}")

        if resposta.status_code == 200:
            versao_remota = resposta.text.strip()
            print(f"Versão remota: {versao_remota}")
        else:
            raise Exception(f"Erro ao acessar a URL {url_versao_remota}. Status: {resposta.status_code}")

        if not os.path.exists(arquivo_versao_local):
            print(f"Arquivo local {arquivo_versao_local} não existe. Criando arquivo com a versão '0.0.0'.")
            with open(arquivo_versao_local, 'w') as f:
                f.write('0.0.0')

        with open(arquivo_versao_local, 'r') as f:
            versao_local = f.read().strip()
            print(f"Versão local: {versao_local}")

        if version.parse(versao_remota) > version.parse(versao_local):
            messagebox.showinfo('Informação', f"Nova versão disponível: {versao_remota}")
            return True
        else:
            messagebox.showinfo('Informação', "Você já está usando a versão mais recente.")
            return False

    except Exception as e:
        messagebox.showerror('Erro', f"Erro ao verificar atualizações: {e}")
        return False

# Função para realizar a atualização
def atualizar_programa():
    if verificar_atualizacao():
        try:
            versao_remota = requests.get(URL_REPOSITORIO + 'versao.txt').text.strip()
            with open(arquivo_versao_local, 'w') as f:
                f.write(versao_remota)
            messagebox.showinfo('Informação', "Arquivo 'versao.txt' atualizado com sucesso!")
        except Exception as e:
            messagebox.showerror('Erro', f"Erro ao atualizar o arquivo 'versao.txt': {e}")

        substituir_exe()
        sys.exit()

def conectar_banco():
    # Conectar ao banco de dados (ou criar se não existir)
    conn = sqlite3.connect('cadastro.db')
    cursor = conn.cursor()
    
    # Cria a tabela se ela não existir
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cadastro (
            id INTEGER PRIMARY KEY,
            modelo TEXT,
            quantidade INTEGER,
            preco REAL,
            condicao TEXT,
            data_cadastro TEXT
        )
    ''')
    
    # Retorna a conexão e o cursor
    conn.commit()
    return conn, cursor

data_hora_atual = datetime.now()
data_hora_formatada = data_hora_atual.strftime("Hora: %H:%M - Dia: %d/%m/%Y")
# Dados de login e configurações do e-mail
EMAIL_ADDRESS = 'relatorioslojas2024@gmail.com'
EMAIL_PASSWORD = 'e l c h w h x o a l p q t i s r'

# Dicionário para armazenar os cadastros
cadastrado = {}
id_counter = 1  # Contador global para gerar IDs únicos

# Variável global para armazenar o tempo e o timer
tempo = 60
timer_envio = None
atualizando_contador = False  # Flag para evitar múltiplas atualizações do contador
relatorio_enviado = False  # Flag para saber se o relatório já foi enviado

# Função para centralizar a root
def centralizar_root(root):
    root.update_idletasks()
    largura = root.winfo_width()
    altura = root.winfo_height()
    largura_tela = root.winfo_screenwidth()
    altura_tela = root.winfo_screenheight()
    x = (largura_tela // 2) - (largura // 2)
    y = (altura_tela // 2) - (altura // 2) 
    root.geometry(f'{largura}x{altura}+{x}+{y}')

# Função para enviar o e-mail com o relatório
def enviar_relatorio():
    def enviar():
        # Obtendo a data e hora atual para o título do e-mail
        data_hora_formatada = datetime.now().strftime("%d/%m/%Y %H:%M")

        msg = EmailMessage()
        msg['Subject'] = f'Relatório de Telas - {data_hora_formatada}'
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = 'microcellourinhosrelato@gmail.com'

        # Criando o conteúdo do relatório
        relatorio = """\
        <html>
        <head>
        <style>
            body {
                font-family: "Arial", sans-serif;
                margin: 0;
                padding: 0;
                font-size: 14px;
            }
            table {
                width: 100%;
                border-collapse: collapse;
            }
            th, td {
                padding: 8px;
                text-align: left;
                border-bottom: 1px solid #ddd;
                word-wrap: break-word;  /* Permite quebra de linha */
            }
            th {
                background-color: #f2f2f2;
            }
            h2 {
                font-size: 20px;
                text-align: left;
                padding-left: 10px;
            }
            /* Ajustes para telas pequenas */
            @media screen and (max-width: 600px) {
                h2 {
                    font-size: 18px;
                    padding-left: 5px;
                }
                table {
                    display: none; /* Ocultar a tabela em telas pequenas */
                }
            }
            @media screen and (min-width: 601px) {
                .mobile-view {
                    display: none; /* Ocultar a visualização em blocos para desktop */
                }
            }
            .block-item {
                display: block;
                background-color: #f9f9f9;
                padding: 10px;
                margin-bottom: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            .block-item div {
                margin-bottom: 8px;
            }
            .block-item div span {
                font-weight: bold;
            }
            .block-item:not(:last-child) {
                border-bottom: 2px solid #ddd;
                margin-bottom: 15px;
            }
        </style>
        </head>
        <body>
            <h2>Relatório de Telas Cadastradas</h2>
            <!-- Tabela para desktop -->
            <table>
                <tr>
                    <th>ID</th>
                    <th>Modelo</th>
                    <th>Quantidade</th>
                    <th>Preço (R$)</th>
                    <th>Condição</th>
                    <th>Data</th>
                </tr>
        """

        # Adicionando as linhas da tabela para desktop
        for modelo_com_id, dados in cadastrado.items():
            modelo = modelo_com_id.split('_')[0]
            relatorio += f"""
                <tr>
                    <td>{dados['id']}</td>
                    <td>{modelo}</td>
                    <td>{dados['quantidade']}</td>
                    <td>{dados['preco']:.2f}</td>
                    <td>{dados['condicao']}</td>
                    <td>{dados['data_cadastro']}</td>
                </tr>
            """

        # Fechando a tabela
        relatorio += """\
            </table>
            <!-- Exibição em blocos para dispositivos móveis -->
            <div class="mobile-view">
        """

        # Adicionando os itens em blocos para celular
        for modelo_com_id, dados in cadastrado.items():
            modelo = modelo_com_id.split('_')[0]
            relatorio += f"""
                <div class="block-item">
                    <div><span>ID:</span> {dados['id']}</div>
                    <div><span>Modelo:</span> {modelo}</div>
                    <div><span>Quantidade:</span> {dados['quantidade']}</div>
                    <div><span>Preço (R$):</span> {dados['preco']:.2f}</div>
                    <div><span>Condição:</span> {dados['condicao']}</div>
                    <div><span>Data:</span> {dados['data_cadastro']}</div>
                </div>
            """

        relatorio += """\
            </div>
        </body>
        </html>
        """

        # Definindo o conteúdo da mensagem com formatação HTML
        msg.set_content(relatorio, subtype='html')

        # Enviando o e-mail
        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                smtp.send_message(msg)
            messagebox.showinfo("Sucesso", "E-mail enviado com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao enviar o e-mail: {e}")

    threading.Thread(target=enviar).start()  # Enviar em uma thread separada


# Função para reiniciar o contador
def reiniciar_timer():
    global tempo, timer_envio, atualizando_contador, relatorio_enviado
    if timer_envio is not None:
        timer_envio.cancel()  # Cancela o timer anterior, se houver

    relatorio_enviado = False  # Reseta o estado de envio do relatório
    tempo = 60
    label.config(text=f'Tempo restante: {tempo} segundos')

    # Cria um novo timer de 10 segundos
    timer_envio = threading.Timer(tempo, enviar_relatorio)
    timer_envio.start()

    # Inicia o contador
    atualizar_contador()

condicao = "Novo"
def mostrar_selecao(selecao):
    global condicao
    condicao = selecao
# Função para adicionar o cadastro ao arquivo e ao dicionário
# Inicialização global do dicionário cadastrado e contador
def cadastrar_tela():
    global id_counter
    tela = entrada_tela.get().lower().strip()  # Remove espaços em branco e converte para minúsculas
    quantidade = entrada_qnt.get().strip()  # Remove espaços em branco
    preco = entrada_preco.get().strip()  # Remove espaços em branco

    # Verificar se uma condição foi selecionada
    if condicao not in ["Novo", "Usado"]:
        messagebox.showerror("Erro", "Selecione se a tela é 'Novo' ou 'Usado'.")
        return

    # Validar o modelo da tela
    identificado = identificar_marca(tela)

    if identificado and quantidade and preco:
        try:
            quantidade = int(quantidade)  # Converte quantidade para inteiro
            preco = float(preco)  # Converte preço para float
        except ValueError:
            messagebox.showerror("Erro", "A quantidade deve ser um número inteiro e o preço deve ser um número válido.")
            return
        
        # Capturar a data do cadastro
        data_cadastro = datetime.now().strftime("%d/%m/%Y")  # Formato dia/mês/ano

        # Verificar se a tela já foi cadastrada com o mesmo preço e condição
        tela_ja_cadastrada = False
        for modelo, dados in cadastrado.items():
            if modelo == identificado and dados['preco'] == preco and dados['condicao'] == condicao:
                # Se o modelo, preço e condição já existem, atualiza a quantidade
                dados['quantidade'] += quantidade
                tela_ja_cadastrada = True
                break

        if not tela_ja_cadastrada:
            # Se o modelo existe mas o preço ou a condição é diferente, criar uma nova entrada com novo ID
            cadastrado[f"{identificado}_{id_counter}"] = {
                'id': id_counter,
                'quantidade': quantidade,
                'preco': preco,
                'data_cadastro': data_cadastro,  # Adiciona a data do cadastro
                'condicao': condicao  # Adiciona a condição da tela (Novo ou Usado)
            }
            id_counter += 1

        salvar_cadastro_criptografado()  # Salvar os dados no arquivo
        messagebox.showinfo("Sucesso", f"Tela '{identificado}' com quantidade {quantidade}, preço R${preco:.2f} e condição '{condicao}' cadastrada ou atualizada.")
        # Limpar os campos de entrada
        entrada_tela.delete(0, tk.END)
        entrada_qnt.delete(0, tk.END)
        entrada_preco.delete(0, tk.END)
        # Atualizar a lista automaticamente após o cadastro
        listar_telas()  # Presumindo que essa função está implementada para mostrar os dados
        reiniciar_timer()  # Reiniciar o timer
    else:
        messagebox.showerror("Erro", "Preencha todos os campos.")

def abrir_root_remocao():
    # Criar nova root para remover tela
    remocao_window = tk.Toplevel(root)
    remocao_window.title("Remover Tela")
    remocao_window.resizable(False, False)
    # Labels e entradas para o ID e quantidade
    tk.Label(remocao_window, text="ID da Tela:").grid(row=0, column=0, padx=5, pady=5)
    entrada_id_remover = tk.Entry(remocao_window)
    entrada_id_remover.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(remocao_window, text="Quantidade a Remover:").grid(row=1, column=0, padx=5, pady=5)
    entrada_qnt_remover = tk.Entry(remocao_window)
    entrada_qnt_remover.grid(row=1, column=1, padx=5, pady=5)

    # Função para realizar a remoção
    def remover_tela_por_id():
        tela_id = entrada_id_remover.get().strip()
        quantidade = entrada_qnt_remover.get().strip()

        if not tela_id or not quantidade:
            messagebox.showerror("Erro", "Preencha o ID e a quantidade.")
            return

        try:
            tela_id = int(tela_id)
            quantidade = int(quantidade)
        except ValueError:
            messagebox.showerror("Erro", "O ID e a quantidade devem ser números.")
            return

        # Procurar tela no dicionário cadastrado
        for modelo_com_id, dados in list(cadastrado.items()):  # Iterar sobre os itens do dicionário
            if dados['id'] == tela_id:
                if dados['quantidade'] >= quantidade:
                    # Se a quantidade a remover for menor ou igual à disponível
                    dados['quantidade'] -= quantidade

                    # Se a quantidade chegar a zero, remover a tela do cadastro
                    if dados['quantidade'] == 0:
                        del cadastrado[modelo_com_id]
                        messagebox.showinfo("Sucesso", f"Tela ID {tela_id} removida.")
                    else:
                        messagebox.showinfo("Sucesso", f"Quantidade {quantidade} removida da tela ID {tela_id}.")
                else:
                    messagebox.showerror("Erro", "Quantidade a remover é maior que a disponível.")
                break
        else:
            messagebox.showerror("Erro", "ID não encontrado.")

        # Salvar os dados atualizados
        salvar_cadastro_criptografado()
        listar_telas()  # Atualizar a lista
        reiniciar_timer()  # Reiniciar o timer
        remocao_window.destroy()  # Fechar a janela de remoção

    # Botão para confirmar a remoção
    btn_confirmar_remocao = tk.Button(remocao_window, text="Remover", command=remover_tela_por_id, bg="#ed3737", fg="white", font=("Times New Roman", 14))
    btn_confirmar_remocao.grid(row=2, column=0, columnspan=2, padx=5, pady=10)


def ajustar_modelo(modelo):
    # Mantém os modelos intactos como "a01 core", "mi9t" sem adicionar espaço
    return modelo.strip()

def capitalizar_modelo(modelo):
    # Capitaliza apenas a primeira letra de cada palavra no modelo
    return modelo.title()

def identificar_marca(modelo):
    # Dicionário que mapeia prefixos a marcas
    prefixos_para_marcas = {
        'mi': 'Xiaomi',  
        'g': 'Motorola',
        'e': 'Motorola',
        's': 'Samsung',
        'a': 'Samsung',
        'iphone': 'Iphone',
        'samsung': 'Samsung',
        'nokia': 'Nokia',
        'moto': 'Motorola',
        'f': 'Xiaomi',
        'lg': 'LG',
        'm': 'Samsung',
        'j': 'Samsung',
        'k': 'LG',
        'q': 'LG',
        'zb': 'Asus',
        'zd': 'Asus',
        'z': 'Motorola',
        'note': 'Xiaomi',
        'poco': 'Xiaomi',
        'hot': 'Infinix',
        'Infinix': 'Infinix',
        'one': 'Motorola',
        'smart': 'Infinix'
    }
    
    # Ajusta o modelo para remover espaços desnecessários e capitaliza
    modelo_ajustado = ajustar_modelo(modelo)
    
    # Itera sobre os prefixos no dicionário
    for prefixo, marca in prefixos_para_marcas.items():
        if modelo_ajustado.lower().startswith(prefixo):
            return f"{marca} {capitalizar_modelo(modelo_ajustado)}"
    
    return capitalizar_modelo(modelo_ajustado)   # Retorna o modelo ajustado capitalizado se nenhum prefixo coincidir

# Função para validar o preço
def validar_preco(preco):
    """Verifica se o preço é um número decimal ou inteiro válido."""
    return re.match(r'^\d+(\.\d{1,2})?$', preco)

aceitar_todos_erros_lista_atual = False

def formatar_lista(entrada):
    global aceitar_todos_erros_lista_atual  # Acessa a variável global

    # Lista para armazenar as saídas formatadas
    saida_formatada = []

    for tela in entrada:
        # Remove espaços em branco e quebras de linha
        tela = tela.strip()

        # Tenta separar quantidade, modelo e preço usando múltiplos delimitadores
        partes = re.split(r'[\s,-,_,*,;]+', tela)

        # Verifica se existem pelo menos 3 partes
        if len(partes) >= 3:
            try:
                # A quantidade é o primeiro elemento e deve ser um número inteiro
                quantidade = partes[0].strip()
                if not quantidade.isdigit():
                    raise ValueError("Quantidade deve ser um número inteiro válido.")
                
                # O preço é o último elemento e deve ser um número decimal ou inteiro
                preco = partes[-1].strip()
                if not validar_preco(preco):
                    raise ValueError("Preço deve ser um número válido (ex: 34.50).")

                # O modelo é composto pelos elementos do meio
                modelo = ' '.join(partes[1:-1]).strip()
                modelo = identificar_marca(modelo)  # Identifica a marca

                # Formata a saída
                saida = f"{modelo};{quantidade};{preco}"
                saida_formatada.append(saida)

            except ValueError as e:
                if not aceitar_todos_erros_lista_atual:  # Se "aceitar todos" não foi acionado
                    if not mostrar_erro(tela, str(e)):
                        break  # Se o usuário cancelar, interrompe o processamento
                else:
                    # Se "aceitar todos os erros" foi ativado, apenas registra o erro
                    print(f"Erro ignorado: {tela}. Motivo: {e}")
        else:
            if not aceitar_todos_erros_lista_atual:  # Se "aceitar todos" não foi acionado
                if not mostrar_erro(tela, "Número de partes inválido"):
                    break  # Se o usuário cancelar, interrompe o processamento
            else:
                # Se "aceitar todos os erros" foi ativado, apenas registra o erro
                print(f"Erro ignorado: {tela}. Motivo: Número de partes inválido")

    return saida_formatada

def mostrar_erro(tela, mensagem_erro):
    global aceitar_todos_erros_lista_atual

    # Pergunta se o usuário quer ignorar todos os erros para a lista atual
    resposta = messagebox.askyesnocancel("Erro", f"Erro na entrada: {tela}\n{mensagem_erro}\n\nDeseja aceitar todos os erros para esta lista?")

    if resposta is None:
        # Se o usuário clicar em "Cancelar"
        return False
    elif resposta:
        # Se o usuário clicar em "Sim" (aceitar todos os erros para esta lista)
        aceitar_todos_erros_lista_atual = True

    # Se o usuário clicar em "Não", continua a exibir erros
    return True

def abrir_root_formato():
    formatacao_window = tk.Toplevel(root)
    formatacao_window.title("Cadastro por lista")
    formatacao_window.resizable(False, False)

    def salvar_cadastro():
        # Lê a lista do campo de texto
        entrada = text_area.get("1.0", "end-1c").splitlines()

        # Formata a lista
        resultados = formatar_lista(entrada)

        if not resultados:  # Se não houver resultados válidos, não faça nada
            messagebox.showwarning("Atenção", "Nenhuma entrada válida foi fornecida.")
            return

        global id_counter  # Acesso ao id_counter global
        cadastro_existente = {}

        # Conectar ao banco de dados
        conn, cursor = conectar_banco()

        try:
            # Busca todos os cadastros existentes no banco
            cursor.execute('SELECT * FROM cadastro')
            rows = cursor.fetchall()
            
            # Monta o cadastro existente com os dados do banco
            for row in rows:
                id_tela, modelo, quantidade, preco, condicao, data_cadastro = row
                chave = (modelo, preco)  # Usar tupla (modelo, preço) como chave
                cadastro_existente[chave] = {
                    'id': id_tela,
                    'quantidade': quantidade,
                    'preco': preco,
                    'data_cadastro': data_cadastro
                }
                id_counter = max(id_counter, id_tela + 1)  # Atualiza o id_counter

        except Exception as e:
            print(f"Erro ao carregar do banco de dados: {e}")
            return

        # Processa as novas entradas
        for resultado in resultados:
            try:
                modelo, quantidade, preco = resultado.split(';')
                quantidade = int(quantidade)

                # Verificar se a tela já foi cadastrada com o mesmo preço
                tela_ja_cadastrada = False
                for (modelo_existente, preco_existente), dados in cadastro_existente.items():
                    if modelo_existente == modelo and preco_existente == preco:
                        # Se o modelo e o preço já existem, atualiza a quantidade
                        dados['quantidade'] += quantidade
                        cursor.execute('''
                            UPDATE cadastro
                            SET quantidade = ?
                            WHERE id = ?
                        ''', (dados['quantidade'], dados['id']))
                        tela_ja_cadastrada = True
                        break

                if not tela_ja_cadastrada:
                    # Se o modelo existe mas o preço é diferente, criar uma nova entrada com novo ID
                    chave = (modelo, preco)  # Usar tupla (modelo, preço) como chave
                    data_cadastro = datetime.now().strftime("%d/%m/%Y")  # Formato de data
                    cursor.execute('''
                        INSERT INTO cadastro (id, modelo, quantidade, preco, condicao, data_cadastro)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (id_counter, modelo, quantidade, float(preco), "Novo", data_cadastro))  # Colocar a condição que você preferir

                    id_counter += 1  # Incrementa o ID para o próximo cadastro

            except ValueError as e:
                print(f"Erro ao processar resultado: {resultado}. Detalhes: {e}")
                continue  # Ignorar a entrada mal formatada

        # Salva as mudanças e fecha a conexão com o banco
        conn.commit()
        conn.close()

        # Limpa a área de texto após salvar
        text_area.delete("1.0", tk.END)
        # Atualizar a interface
        carregar_cadastro_criptografado()
        atualizar_label()
        listar_telas()
        fazer_backup_banco()

        messagebox.showinfo("Sucesso", "Cadastro atualizado com sucesso!")
        formatacao_window.destroy()

    # Criação da label de exemplo
    label = tk.Label(formatacao_window, text="Modelo de cadastro: 2, g34, 34", font=("Times New Roman", 14))
    label.grid(row=0, column=0, padx=(5, 2), pady=5, sticky='w')

    # Criação da área de texto
    text_area = tk.Text(formatacao_window, height=15, width=50)
    text_area.grid(row=1, column=0, padx=10, pady=10)

    # Criação do botão de formatar
    btn_formatar = tk.Button(formatacao_window, text="Formatar e Salvar", command=salvar_cadastro)
    btn_formatar.grid(row=2, column=0, pady=10)


def abrir_root_edicao():
    # Criar nova root para edição
    edicao_window = tk.Toplevel(root)
    edicao_window.title("Editar Tela")
    edicao_window.resizable(False, False)

    # Labels e entradas para o ID, modelo, quantidade e preço
    tk.Label(edicao_window, text="ID da Tela:").grid(row=0, column=0, padx=5, pady=5)
    entrada_id = tk.Entry(edicao_window)
    entrada_id.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(edicao_window, text="Novo Modelo:").grid(row=1, column=0, padx=5, pady=5)
    entrada_modelo = tk.Entry(edicao_window)
    entrada_modelo.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(edicao_window, text="Nova Quantidade:").grid(row=2, column=0, padx=5, pady=5)
    entrada_qnt_editar = tk.Entry(edicao_window)
    entrada_qnt_editar.grid(row=2, column=1, padx=5, pady=5)

    tk.Label(edicao_window, text="Novo Preço:").grid(row=3, column=0, padx=5, pady=5)
    entrada_preco_editar = tk.Entry(edicao_window)
    entrada_preco_editar.grid(row=3, column=1, padx=5, pady=5)

    tk.Label(edicao_window, text="Nova Condição:").grid(row=4, column=0, padx=5, pady=5)
    opcoes_condicao = ["Novo", "Usado"]
    selecao_condicao = tk.StringVar(value=opcoes_condicao[0])  # Valor inicial ("Novo")
    menu_condicao = tk.OptionMenu(edicao_window, selecao_condicao, *opcoes_condicao)
    menu_condicao.grid(row=4, column=1, padx=5, pady=5)

    # Botão para confirmar a edição
    def confirmar_edicao():
        tela_id = entrada_id.get().strip()  # Pega o ID da tela
        novo_modelo = entrada_modelo.get().strip()  # Pega o novo modelo
        nova_quantidade = entrada_qnt_editar.get().strip()  # Pega a nova quantidade
        novo_preco = entrada_preco_editar.get().strip()  # Pega o novo preço
        nova_condicao = selecao_condicao.get()  # Pega a nova condição

        if tela_id:
            try:
                tela_id = int(tela_id)
            except ValueError:
                messagebox.showerror("Erro", "ID deve ser um número.")
                return

            # Verificar se a tela está cadastrada pelo ID
            for modelo, dados in list(cadastrado.items()):  # Aqui usamos items() para acessar a chave e os dados
                if dados['id'] == tela_id:
                    # Atualiza a quantidade e preço, se fornecidos
                    if nova_quantidade:
                        try:
                            dados['quantidade'] = int(nova_quantidade)  # Atualiza a quantidade
                        except ValueError:
                            messagebox.showerror("Erro", "Quantidade deve ser um número.")
                            return

                    if novo_preco:
                        try:
                            dados['preco'] = float(novo_preco)  # Atualiza o preço
                        except ValueError:
                            messagebox.showerror("Erro", "Preço deve ser um número.")
                            return

                    # Atualiza o modelo, se fornecido e diferente
                    if novo_modelo and novo_modelo != modelo:
                        novo_modelo = identificar_marca(novo_modelo)  # Ajusta a marca do novo modelo
                        # Remover a entrada antiga
                        del cadastrado[modelo]
                        # Adicionar nova entrada com o novo modelo
                        cadastrado[novo_modelo] = dados  # Reutiliza os dados já atualizados

                    # Atualiza a condição
                    dados['condicao'] = nova_condicao

                    # Salvar as alterações no arquivo
                    salvar_cadastro_criptografado()  
                    messagebox.showinfo("Sucesso", f"Tela ID {tela_id} atualizada com sucesso.")
                    edicao_window.destroy()  # Fecha a janela de edição
                    listar_telas()  # Atualiza a listagem
                    reiniciar_timer()  # Reinicia o timer
                    return

            messagebox.showerror("Erro", "ID não encontrado.")
        else:
            messagebox.showerror("Erro", "Preencha o ID da tela.")

    btn_confirmar = tk.Button(edicao_window, text="Confirmar Edição", command=confirmar_edicao)
    btn_confirmar.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

def print_selection():
    if var_opcao.get() == 1:  # Usado
        listar_telas(condicao='usado')
    elif var_opcao.get() == 2:  # Novo
        listar_telas(condicao='novo')
    else:  # Nenhum selecionado (mostrar todos)
        listar_telas(condicao=None)

# Função para listar os dados na interface
def listar_telas(condicao=None):
    carregar_cadastro_criptografado()  # Carregar o cadastro a partir do arquivo
    texto_listagem.delete(1.0, tk.END)  # Limpar a área de texto antes de exibir
    
    if not cadastrado:
        texto_listagem.insert(tk.END, "Nenhum cadastro encontrado.")
    else:
        # Cabeçalho da tabela com um estilo mais bonito
        texto_listagem.insert(tk.END, f"{'ID':<10} {'Modelo':<48} {'Quantidade':<20} {'Condição':<25} {'Data de Cadastro':<20}\n", 'header')
        texto_listagem.insert(tk.END, "-" * 80 + "\n", 'line')  # Linha de separação

        # Dicionário temporário para armazenar os modelos únicos
        modelos_unicos = {}

        # Itera sobre o dicionário cadastrado
        for modelo_com_id, dados in cadastrado.items():
            modelo = modelo_com_id.split('_')[0]  # Pegar apenas o nome do modelo (ignorando o ID)
            condicao_item = dados.get('condicao', 'Não informado').capitalize()  # Obtém a condição ou usa 'Não informado'
            
            # Se uma condição foi selecionada (usado ou novo), filtra os itens
            if condicao and condicao_item != condicao.capitalize():
                continue  # Pula este item se a condição não corresponde à selecionada
            
            if modelo in modelos_unicos:
                modelos_unicos[modelo]['quantidade'] += dados['quantidade']  # Soma as quantidades
            else:
                # Se o modelo não existe no dicionário, adicionamos ele
                modelos_unicos[modelo] = {
                    'id': dados['id'],
                    'quantidade': dados['quantidade'],
                    'condicao': condicao_item,  # Armazena a condição da tela
                    'data_cadastro': dados['data_cadastro']  # Incluindo a data de cadastro
                }

        # Agora, exibe as telas únicas com cores alternadas
        linha_alternada = False
        for modelo, dados in modelos_unicos.items():
            # Alterna a cor de fundo para cada linha
            tag = 'evenrow' if linha_alternada else 'oddrow'
            texto_listagem.insert(
                tk.END, 
                f"{dados['id']:<5} {modelo:<30} {dados['quantidade']:<12} {dados['condicao']:<15} {dados['data_cadastro']:<15}\n", 
                tag
            )
            linha_alternada = not linha_alternada  # Alterna a cor para a próxima linha

# Função para salvar o cadastro no banco criptografado
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
import sqlite3

# Funções de Criptografia e Descriptografia
def encrypt_data(data, key):
    cipher = AES.new(key, AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(data.encode('utf-8'))
    return base64.b64encode(nonce + ciphertext).decode('utf-8')

def decrypt_data(enc_data, key):
    enc_data = base64.b64decode(enc_data.encode('utf-8'))
    nonce = enc_data[:16]
    ciphertext = enc_data[16:]
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    return cipher.decrypt(ciphertext).decode('utf-8')

# Gera uma chave de 16 bytes (128 bits)
key = get_random_bytes(16)

# Função para salvar no banco de dados com criptografia
def salvar_cadastro_criptografado(modelo, quantidade, preco, condicao, data_cadastro):
    try:
        conn = sqlite3.connect('cadastro.db')
        cursor = conn.cursor()

        # Cria a tabela se não existir
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cadastro (
                id INTEGER PRIMARY KEY,
                modelo TEXT,
                quantidade TEXT,
                preco TEXT,
                condicao TEXT,
                data_cadastro TEXT
            )
        ''')

        # Criptografa os dados
        modelo_enc = encrypt_data(modelo, key)
        quantidade_enc = encrypt_data(str(quantidade), key)
        preco_enc = encrypt_data(str(preco), key)
        condicao_enc = encrypt_data(condicao, key)
        data_cadastro_enc = encrypt_data(data_cadastro, key)

        # Insere os dados criptografados no banco de dados
        cursor.execute('''
            INSERT INTO cadastro (modelo, quantidade, preco, condicao, data_cadastro)
            VALUES (?, ?, ?, ?, ?)
        ''', (modelo_enc, quantidade_enc, preco_enc, condicao_enc, data_cadastro_enc))

        conn.commit()
        conn.close()
        print("Cadastro salvo com criptografia!")
        
    except Exception as e:
        print(f"Erro ao salvar cadastro: {str(e)}")

# Função para fazer backup do banco de dados
def fazer_backup_banco():
    try:
        # Caminho para o banco de dados
        caminho_banco = 'cadastro.db'
        
        # Caminho para a pasta onde as imagens são salvas
        pasta_imagens = os.path.join(os.path.expanduser("~"), "Documents", "Cadastro Telas")
        
        # Caminho de destino para o backup
        caminho_backup = os.path.join(pasta_imagens, 'backup_cadastro.db')
        
        # Copiar o arquivo do banco de dados para a pasta de backup
        shutil.copy(caminho_banco, caminho_backup)
        messagebox.showinfo("Informação","Backup do banco de dados salvo com sucesso!")
        
    except Exception as e:
        print(f"Ocorreu um erro ao fazer o backup do banco de dados: {e}")


# Função para limpar todos os dados com confirmação
def limpar_lista():
    # Exibir caixa de diálogo para confirmar
    resposta = messagebox.askyesno("Confirmação", "Você tem certeza que deseja limpar todos os dados?")
    
    if resposta:  # Se o usuário clicar em "Sim"
        global cadastrado, id_counter
        cadastrado = {}
        id_counter = 1
        
        try:
            # Conectar ao banco de dados
            conn, cursor = conectar_banco()
            
            # Deletar todos os registros da tabela 'cadastro'
            cursor.execute('DELETE FROM cadastro')
            
            # Commit para salvar as mudanças no banco de dados
            conn.commit()
            conn.close()
            
            # Atualizar a interface e mostrar mensagem de sucesso
            listar_telas()
            messagebox.showinfo("Sucesso", "Todos os dados foram limpos do banco de dados e da interface.")
        
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao limpar os dados: {e}")

# Função para pesquisar telas
def pesquisar_tela(event=None):  # Aceita um argumento opcional
    pesquisa = entrada_pesquisa.get().lower()  # Obtém o termo de pesquisa
    texto_listagem.delete(1.0, tk.END)  # Limpa a área de texto antes de exibir resultados
    
    if not pesquisa:
        listar_telas()  # Se não há pesquisa, listar todas as telas
        return
    
    # Filtra os resultados para mostrar os modelos que correspondem à pesquisa
    resultado = [modelo_com_id for modelo_com_id, dados in cadastrado.items() if pesquisa in modelo_com_id.split('_')[0].lower()]
    
    if not resultado:
        texto_listagem.insert(tk.END, "Nenhum resultado encontrado.")
    else:
        # Ao pesquisar, exibe ID, Modelo, Quantidade, Preço, Condição e Data
        texto_listagem.insert(tk.END, f"{'ID':<10} {'Modelo':<47} {'Quantidade':<22} {'Preço (R$)':<20} {'Condição':<20} {'Data':<12}\n", 'header')
        texto_listagem.insert(tk.END, "-" * 85 + "\n", 'line')  # Linha de separação

        linha_alternada = False
        for modelo_com_id in resultado:
            dados = cadastrado[modelo_com_id]  # Acesse os dados do dicionário usando o modelo encontrado
            modelo = modelo_com_id.split('_')[0]  # Exibir apenas o nome do modelo sem o ID
            condicao = dados.get('condicao', 'Não informado')  # Obtém a condição ou usa 'Não informado'

            # Alterna a cor de fundo para cada linha
            tag = 'evenrow' if linha_alternada else 'oddrow'
            texto_listagem.insert(
                tk.END, 
                f"{dados['id']:<5} {modelo:<30} {dados['quantidade']:<12} {dados['preco']:<12.2f} {condicao:<10} {dados['data_cadastro']:<12}\n", 
                tag
            )
            linha_alternada = not linha_alternada  # Alterna a cor para a próxima linha

# Função para carregar os cadastros do arquivo
def carregar_cadastro_criptografado():
    try:
        conn = sqlite3.connect('cadastro.db')
        cursor = conn.cursor()

        # Busca todos os cadastros
        cursor.execute('SELECT * FROM cadastro')
        rows = cursor.fetchall()

        for row in rows:
            id_tela, modelo_enc, quantidade_enc, preco_enc, condicao_enc, data_cadastro_enc = row

            # Descriptografa os dados
            modelo = decrypt_data(modelo_enc, key)
            quantidade = decrypt_data(quantidade_enc, key)
            preco = decrypt_data(preco_enc, key)
            condicao = decrypt_data(condicao_enc, key)
            data_cadastro = decrypt_data(data_cadastro_enc, key)

            print(f"ID: {id_tela}, Modelo: {modelo}, Quantidade: {quantidade}, Preço: {preco}, Condição: {condicao}, Data: {data_cadastro}")

        conn.close()

    except Exception as e:
        print(f"Erro ao carregar cadastro: {str(e)}")


cor_atual = 'white'
fundo_label = '#ffffff'
# Função para alternar entre o tema claro e escuro
def toggle_tema():
    global tema_escuro, cor_fonte, fundo_label, cor_atual
    if tema_escuro:
        cor_fonte = "black"
        # Mudar para tema claro
        desvanecer_fundo("white")
        cor_atual='white'
        canvas.itemconfig(botao_imagem, image=imagem_escura_tk)  # Mudar para imagem clara
        canvas_banco.config(bg=cor_atual)
        r1.config(fg=cor_fonte, bg=cor_atual)
        r2.config(fg=cor_fonte, bg=cor_atual)
        r3.config(fg=cor_fonte, bg=cor_atual)
        tema_escuro = False
        fundo_label = "white"  # Definir a cor do fundo dos labels para branco
    else:
        # Mudar para tema escuro
        desvanecer_fundo("#2E2E2E")
        cor_fonte = "white"
        cor_atual= '#2E2E2E'
        print(cor_atual)
        canvas.itemconfig(botao_imagem, image=imagem_clara_tk)  # Mudar para imagem escura
        canvas_banco.config(bg=cor_atual)
        r1.config(fg=cor_fonte, bg=cor_atual)
        r2.config(fg=cor_fonte, bg=cor_atual)
        r3.config(fg=cor_fonte, bg=cor_atual)
        tema_escuro = True
        fundo_label = "#2E2E2E"  # Definir a cor do fundo dos labels para cinza escuro

    # Atualiza a cor da fonte e fundo em todos os widgets, exceto botões
    label.config(fg=cor_fonte, bg=fundo_label)  # Atualiza também o fundo do label
    for widget in root.winfo_children():
        if isinstance(widget, tk.Label) or isinstance(widget, tk.Entry):
            widget.config(fg=cor_fonte, bg=fundo_label)  # Atualiza o fundo

# Função de desvanecimento da cor de fundo
# Função para desvanecer a cor de fundo
def desvanecer_fundo(cor_destino, passo=10):
    cor_atual = root.cget("bg")
    r1, g1, b1 = root.winfo_rgb(cor_atual)
    r2, g2, b2 = root.winfo_rgb(cor_destino)
    
    # Normalizando os valores RGB de 0-65535 para 0-255
    r1, g1, b1 = r1 // 256, g1 // 256, b1 // 256
    r2, g2, b2 = r2 // 256, g2 // 256, b2 // 256

    # Calculando os passos de mudança
    r_step = (r2 - r1) / passo
    g_step = (g2 - g1) / passo
    b_step = (b2 - b1) / passo

    # Função interna para atualizar a cor gradualmente
    def atualizar_cor(i):
        if i <= passo:
            # Atualizando a cor atual
            nova_cor = f'#{int(r1 + r_step * i):02x}{int(g1 + g_step * i):02x}{int(b1 + b_step * i):02x}'
            root.configure(bg=nova_cor)
            canvas.configure(bg=nova_cor)
            root.after(30, atualizar_cor, i + 1)  # Chama a próxima atualização

    atualizar_cor(0)  # Iniciar a animação


def atualizar_contador():
    global tempo, atualizando_contador
    if not atualizando_contador:  # Verifica se já está atualizando
        atualizando_contador = True  # Marca que está atualizando

        def contagem_regressiva():
            global tempo, atualizando_contador
            if tempo > 0:
                tempo -= 1  # Subtrai 1 segundo
            else:
                # Se o tempo acabou, envia o relatório
                enviar_relatorio()
                atualizando_contador = False  # Reseta a flag após o envio do relatório

            # Atualiza o texto da label
            label.config(text=f'Tempo restante: {tempo} segundos')

            if tempo > 0:
                # Chama esta função novamente após 1 segundo (1000 ms)
                root.after(1000, contagem_regressiva)
            else:
                atualizando_contador = False  # Permite nova contagem após o término

        contagem_regressiva()  # Inicia a contagem

def atualizar_contagem_telas():
    """Counts the number of records in the SQLite database and returns the count."""
    try:
        conn, cursor = conectar_banco()  # Chama a função para conectar ao banco
        cursor.execute('SELECT COUNT(*) FROM cadastro')  # Conta o número de registros
        qnt_telas_cadastradas = cursor.fetchone()[0]  # Obtém o resultado
        conn.close()
    except Exception as e:
        print(f"Ocorreu um erro ao contar as telas: {e}")
        qnt_telas_cadastradas = 0  # Retorna 0 em caso de erro
    return qnt_telas_cadastradas

def atualizar_label():
    """Updates the label with the current count of registered screens."""
    qnt_telas_cadastradas = atualizar_contagem_telas()
    label_qnt_telas.config(text=f'Telas Cadastradas: {qnt_telas_cadastradas}')


# Função para redimensionar as imagens


# Importar as bibliotecas necessárias no início do arquivo
def encontrar_arquivo_no_executavel(nome_arquivo):
    """Retorna o caminho correto para arquivos, seja no executável ou no ambiente de desenvolvimento."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, nome_arquivo)
    else:
        return nome_arquivo

def redimensionar_imagem(caminho, largura, altura):
    """Redimensiona a imagem localizada no caminho especificado e mantém a transparência se houver."""
    try:
        # Abre a imagem original
        imagem = Image.open(caminho)

        # Converte a imagem para RGBA se não estiver nesse formato
        if imagem.mode != 'RGBA':
            imagem = imagem.convert('RGBA')

        # Redimensiona a imagem
        imagem_redimensionada = imagem.resize((largura, altura), Image.Resampling.LANCZOS)

        # Para garantir que o fundo transparente seja mantido, podemos criar um novo objeto de imagem
        # Com um fundo transparente e desenhar a imagem redimensionada nele
        fundo_transparente = Image.new("RGBA", (largura, altura), (0, 0, 0, 0))  # Criar uma nova imagem transparente
        fundo_transparente.paste(imagem_redimensionada, (0, 0), imagem_redimensionada)  # Adicionar a imagem redimensionada

        return fundo_transparente
    except FileNotFoundError:
        print(f"Imagem {caminho} não encontrada.")
        return None


# Caminhos das imagens
caminho_imagem_clara = encontrar_arquivo_no_executavel("sol.png")
caminho_imagem_escura = encontrar_arquivo_no_executavel("lua.png")
caminho_imagem_banco = encontrar_arquivo_no_executavel("banco.png")

# Redimensionar as imagens
imagem_clara = redimensionar_imagem(caminho_imagem_clara, 30, 30)
imagem_escura = redimensionar_imagem(caminho_imagem_escura, 30, 30)
imagem_banco = redimensionar_imagem(caminho_imagem_banco, 40, 40)

# Caminho para a pasta Documentos e Cadastro Telas
pasta_documentos = os.path.join(os.path.expanduser("~"), "Documents", "Cadastro Telas")

# Criar a pasta "Cadastro Telas" se não existir
if not os.path.exists(pasta_documentos):
    os.makedirs(pasta_documentos)
    print(f"Pasta '{pasta_documentos}' criada.")

# Salvar as imagens redimensionadas, se estiverem disponíveis
if imagem_clara:
    caminho_claro_destino = os.path.join(pasta_documentos, "sol_redimensionado.png")
    imagem_clara.save(caminho_claro_destino)
    print(f"Imagem 'sol.png' redimensionada salva em: {caminho_claro_destino}")

if imagem_escura:
    caminho_escuro_destino = os.path.join(pasta_documentos, "lua_redimensionada.png")
    imagem_escura.save(caminho_escuro_destino)
    print(f"Imagem 'lua.png' redimensionada salva em: {caminho_escuro_destino}")

if imagem_banco:
    caminho_banco_destino = os.path.join(pasta_documentos, "banco_redimensionado.png")
    imagem_banco.save(caminho_banco_destino, format='PNG')  # Salvar como PNG
    print(f"Imagem 'banco.png' redimensionada salva em: {caminho_banco_destino}")


# Criar a root principal
root = tk.Tk()
root.title("Cadastro de Telas - Programa desenvolvido por Gustavo Henrique de Araujo Alves - Suporte:gustavolambor@gmail.com")
root.configure(bg="blue")

tema_escuro = False
cor_fonte = "black"

# Convertendo as imagens redimensionadas para o formato Tkinter
imagem_clara_tk = ImageTk.PhotoImage(imagem_clara)
imagem_escura_tk = ImageTk.PhotoImage(imagem_escura)
imagem_banco_tk = ImageTk.PhotoImage(imagem_banco)  # Converter imagem do banco

# Centralizar a root
root.geometry("940x800")
root.update_idletasks()
centralizar_root(root)
root.resizable(False, False)

# Ajustar os campos de entrada e labels
tk.Label(root, text="Modelo da Tela:", font=("Times New Roman", 14)).grid(row=0, column=0, padx=(5, 2), pady=5, sticky='e')
entrada_tela = tk.Entry(root, width=30)  
entrada_tela.grid(row=0, column=1, padx=(2, 5), pady=5)

tk.Label(root, text="Quantidade:", font=("Times New Roman", 14)).grid(row=1, column=0, padx=(5, 2), pady=5, sticky='e')
entrada_qnt = tk.Entry(root, width=30)
entrada_qnt.grid(row=1, column=1, padx=(2, 5), pady=5)

tk.Label(root, text="Preço:", font=("Times New Roman", 14)).grid(row=2, column=0, padx=(5, 2), pady=5, sticky='e')
entrada_preco = tk.Entry(root, width=30)
entrada_preco.grid(row=2, column=1, padx=(2, 5), pady=5)

# Label para tempo restante
label = tk.Label(root, text=f'Tempo restante: {tempo} segundos', font=("Times New Roman", 12), fg=cor_fonte, bg=fundo_label)
label.grid(row=0, column=2, padx=(5, 10), pady=5, sticky='e')  

label_qnt_telas = tk.Label(root, text="", font=("Times New Roman", 12), fg=cor_fonte, bg=fundo_label)
label_qnt_telas.grid(row=7, column=2, padx=(0,70), pady=5, sticky='e')  

# Informações do desenvolvedor
label2 = tk.Label(root, text='Desenvolvido por Gustavo Henrique de Araujo Alves', font=("Times New Roman", 12))
label2.grid(row=8, column=1, padx=(5, 10), pady=5, sticky='e')  

# Botões de ação
label3 = tk.Label(root, text="Condição:", font=("Times New Roman", 14))
label3.grid(row=3, column=1, padx=(0,200), pady=5)

opcoes = ["Novo", "Usado"]
selecao_var = tk.StringVar(value=opcoes[0])  

menu = tk.OptionMenu(root, selecao_var, *opcoes, command=mostrar_selecao)
menu.grid(row=3, column=1, padx=0, pady=5)

btn_cadastrar = tk.Button(root, text="Cadastrar", command=cadastrar_tela, bg="#07ba28", fg="white", font=("Times New Roman", 14))
btn_cadastrar.grid(row=4, column=1, padx=0, pady=10)

btn_remover = tk.Button(root, text="Remover", command=abrir_root_remocao, bg="#ed3737", fg="white", font=("Times New Roman", 14))
btn_remover.grid(row=3, column=0, padx=10, pady=10)

btn_editar = tk.Button(root, text="Editar", command=abrir_root_edicao, bg="#2196F3", fg="white", font=("Times New Roman", 14))
btn_editar.grid(row=3, column=2, padx=10, pady=10)

btn_formato = tk.Button(root, text="Cadastrar lista", command=abrir_root_formato, bg="#db5704", fg="white", font=("Times New Roman", 14))
btn_formato.grid(row=4, column=2, padx=10, pady=10)

btn_limpar = tk.Button(root, text="Limpar todos os dados", command=limpar_lista, bg="#b80202", fg="white", font=("Times New Roman", 14))
btn_limpar.grid(row=5, column=1, padx=10, pady=10)

var_opcao = tk.IntVar()
var_opcao.set(0)  # Nenhuma opção selecionada inicialmente

# Radiobuttons para selecionar a condição
r1 = tk.Radiobutton(root, text='Usado', fg=f'{cor_fonte}', variable=var_opcao, value=1, command=print_selection, bg=f'{cor_atual}')
r1.grid(row=7, column=1, padx=(0,300), pady=5, sticky='e')

r2 = tk.Radiobutton(root, text='Novo', fg=f'{cor_fonte}', variable=var_opcao, value=2, command=print_selection, bg=f'{cor_atual}')
r2.grid(row=7, column=1, padx=100, pady=5, sticky='e')

r3 = tk.Radiobutton(root, text='Todos', fg=f'{cor_fonte}', variable=var_opcao, value=0, command=print_selection, bg=f'{cor_atual}')
r3.grid(row=7, column=1, padx=200, pady=5, sticky='e')

botao_enviar = tk.Button(root, text="Enviar Relatório", command=enviar_relatorio, bg="#1d0f96", fg="white", font=("Times New Roman", 14))
botao_enviar.grid(row=4, column=0, padx=10, pady=10)

# Criando um Canvas para "simular" um botão com transparência
canvas = tk.Canvas(root, width=30, height=30, bg="white", highlightthickness=0)
canvas.grid(row=0, column=1, padx=(5, 10), pady=5, sticky='e')

# Adicionando uma imagem ao Canvas que será usada como o "botão"
botao_imagem = canvas.create_image(15, 15, image=imagem_escura_tk)

# Mantém a referência às imagens para evitar que sejam coletadas pelo garbage collector
canvas.imagem_clara = imagem_clara_tk
canvas.imagem_escura = imagem_escura_tk

# Ligando a função de alternar tema ao clique no Canvas
canvas.bind("<Button-1>", lambda event: toggle_tema())

# Criando um segundo Canvas para o botão do banco
canvas_banco = tk.Canvas(root, width=50, height=50,bg=f'{cor_atual}' , highlightthickness=0)
canvas_banco.grid(row=0, column=0, padx=(5, 200), pady=5, sticky='e')

# Adicionando a imagem do banco ao Canvas que será usada como o "botão"
botao_imagem_banco = canvas_banco.create_image(25, 25, image=imagem_banco_tk)  # Usando a versão convertida

# Mantém a referência às imagens para evitar que sejam coletadas pelo garbage collector
canvas_banco.imagem_banco = imagem_banco_tk  # Salvar a referência da imagem

# Ligando a função de backup ao clique no Canvas
canvas_banco.bind("<Button-1>", lambda event: fazer_backup_banco())

# Campo de pesquisa
tk.Label(root, text="Pesquisar Modelo:", font=("Times New Roman", 14)).grid(row=6, column=0, padx=(5, 2), pady=5, sticky='e')
entrada_pesquisa = tk.Entry(root, width=30)
entrada_pesquisa.grid(row=6, column=1, padx=(2, 5), pady=5)

# Adiciona o evento de tecla para pesquisar automaticamente
entrada_pesquisa.bind("<KeyRelease>", pesquisar_tela)


# Frame para encapsular o texto e a scrollbar
frame_texto = tk.Frame(root)
frame_texto.grid(row=8, column=0, columnspan=3, padx=10, pady=10)

# Barra de rolagem (scrollbar)
scrollbar = tk.Scrollbar(frame_texto)
scrollbar.pack(side="right", fill="y")

# Área de listagem com a barra de rolagem integrada
texto_listagem = tk.Text(frame_texto, height=18, width=92, yscrollcommand=scrollbar.set)
texto_listagem.pack(side="left", fill="both", expand=True)

# Configurando a barra de rolagem para rolar o conteúdo do texto
scrollbar.config(command=texto_listagem.yview)

# Adicionando cores e estilos para o widget Text
texto_listagem.tag_configure('header', font=('Arial', 10, 'bold'), foreground='white', background='#333333')
texto_listagem.tag_configure('line', foreground='#999999')
texto_listagem.tag_configure('oddrow', background='#f9f9f9')  # Cor para linhas ímpares
texto_listagem.tag_configure('evenrow', background='#e0e0e0')  # Cor para linhas pares

# Carregar dados do arquivo na inicialização
try:
    with open("cadastro.txt", "r") as f:
        for linha in f:
            if linha.strip():
                partes = linha.strip().split(",")
                if len(partes) == 4:
                    id_tela, modelo, quantidade, preco = partes
                    cadastrado[modelo] = {'id': int(id_tela), 'quantidade': int(quantidade), 'preco': float(preco)}
                    id_counter = max(id_counter, int(id_tela) + 1)
except FileNotFoundError:
    pass

label.config(fg=cor_fonte, bg=fundo_label)  # Atualiza também o fundo do label
for widget in root.winfo_children():
    if isinstance(widget, tk.Label) or isinstance(widget, tk.Entry):
        widget.config(fg=cor_fonte, bg=fundo_label)  # Atualiza o fundo

carregar_cadastro_criptografado()
atualizar_label()
fazer_backup_banco()
listar_telas()
atualizar_programa()
# Iniciar o loop principal
root.mainloop()
