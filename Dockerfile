# Usa a imagem oficial do Python como base
FROM python:3.11-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo de dependências primeiro (para aproveitar o cache de camadas)
COPY pyproject.toml .
COPY uv.lock .

# Instala o UV
RUN pip install uv

# Instala as dependências
RUN uv sync

# Copia o código da aplicação para o container
COPY . .


# Expõe a porta que o FastAPI usa (normalmente 8000)
EXPOSE 8000

# Comando para rodar a aplicação
CMD ["uv", "run",  "fastapi", "run",  "./src/api/app.py", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--proxy-headers"]
