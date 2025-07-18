# Imagem base otimizada para Python e libs nativas
FROM python:3.10-slim

# Define diretório de trabalho
WORKDIR /app

# Instala bibliotecas de sistema necessárias para pandas, numpy, scikit-learn, etc.
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia os requisitos
COPY requirements.txt .

# Instala dependências Python
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copia todo o código da aplicação
COPY . .

# Expondo a porta que o uvicorn vai usar
EXPOSE 8000

# Comando para rodar FastAPI com hot-reload desativado (modo produção)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
