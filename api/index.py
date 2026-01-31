import os
import sys

# Adiciona o diretório pai ao path para importar o app.py da raiz
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from app import app

# Vercel precisa que a variável 'app' seja exposta
# O Vercel busca por uma variável chamada 'app' ou 'handler' no entrypoint
