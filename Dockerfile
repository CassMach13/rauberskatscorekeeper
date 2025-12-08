# Usar uma imagem oficial do Python como base
FROM python:3.9-slim

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia o arquivo de dependências e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todos os arquivos do projeto para o contêiner
COPY . .

# Define o comando para iniciar a aplicação usando Gunicorn (servidor de produção)
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "8", "app:app"]