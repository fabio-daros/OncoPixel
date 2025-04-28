# Dockerfile
FROM python:3.12-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Criar e mover para o diretório da aplicação
WORKDIR /app

# Copiar apenas os arquivos de dependências primeiro (para usar cache)
COPY requirements.txt .
COPY package.json .
COPY package-lock.json .

# Instalar dependências do Python
RUN pip install --upgrade pip
RUN pip config set global.extra-index-url https://download.pytorch.org/whl/cpu
RUN pip install -r requirements.txt

# Instalar dependências do Node.js
RUN npm install

# Copiar o restante do projeto
COPY . .

# Gerar os estilos com Tailwind
RUN npm run build

# Rodar o Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

