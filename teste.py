import sqlite3
import os
import pyminizip
import pyzipper
import shutil

# Caminho para a pasta "Documents"
pasta_documentos = os.path.join(os.path.expanduser("~"), "Documents")

# Definir o caminho completo para o arquivo zip
caminho_zip = os.path.join(pasta_documentos, 'teste.zip')

# Definir uma pasta temporária para descompactar o banco de dados
pasta_temp = os.path.join(pasta_documentos, 'temp_banco')

# Definir o nome do arquivo banco de dados dentro da pasta temporária
caminho_banco = os.path.join(pasta_temp, 'teste.db')

# Definir a senha para o arquivo zip
senha_zip = b"minha_senha_23"  # Senha deve ser um byte string

def descompactar_banco():
    # Verifica se o arquivo ZIP existe
    if os.path.exists(caminho_zip):
        with pyzipper.AESZipFile(caminho_zip, 'r') as zf:
            # Extrai o arquivo fornecendo a senha
            zf.extractall(pasta_temp, pwd=senha_zip)
        print(f"Arquivo descompactado para {pasta_temp}.")
    else:
        print("Nenhum arquivo ZIP encontrado. Criando novo banco de dados.")

def conectar_banco():
    # Garante que a pasta temporária existe
    if not os.path.exists(pasta_temp):
        os.makedirs(pasta_temp)
    
    # Descompacta o banco de dados se o ZIP existir
    descompactar_banco()
    
    # Conecta ao banco de dados SQLite
    conn = sqlite3.connect(caminho_banco)
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

    conn.commit()
    return conn, cursor

def zipar_arquivo(caminho_arquivo, caminho_zip, senha):
    # Compacta o arquivo banco de dados com senha
    compressao = 5  # Nível de compressão
    pyminizip.compress(caminho_arquivo, None, caminho_zip, senha, compressao)
    print(f"Arquivo {caminho_arquivo} compactado como {caminho_zip} com senha.")

def cadastrar_dados(cursor, modelo, quantidade, preco, condicao, data_cadastro):
    # Insere um novo cadastro na tabela
    cursor.execute('''
        INSERT INTO cadastro (modelo, quantidade, preco, condicao, data_cadastro)
        VALUES (?, ?, ?, ?, ?)
    ''', (modelo, quantidade, preco, condicao, data_cadastro))

def atualizar_zip():
    # Compacta o banco de dados atualizado e remove o arquivo temporário
    zipar_arquivo(caminho_banco, caminho_zip, senha_zip.decode())
    
    # Limpa a pasta temporária para remover o arquivo .db após zipar
    if os.path.exists(pasta_temp):
        shutil.rmtree(pasta_temp)
        print(f"Pasta temporária {pasta_temp} removida.")

# Conectar ao banco de dados e criar tabela
conn, cursor = conectar_banco()

# Exemplo de inserção de dados
modelo = 'Produto Y'
quantidade = 15
preco = 199.99
condicao = 'Usado'
data_cadastro = '2024-10-21'

# Verificar se todos os valores são válidos antes de inserir
if modelo and quantidade and preco and condicao and data_cadastro:
    cadastrar_dados(cursor, modelo, quantidade, preco, condicao, data_cadastro)
else:
    print("Erro: Valores inválidos ao cadastrar no banco de dados.")

# Commit das mudanças
conn.commit()

# Fechar a conexão com o banco de dados antes de compactar
conn.close()

# Atualiza o arquivo ZIP com o banco de dados atualizado
atualizar_zip()
