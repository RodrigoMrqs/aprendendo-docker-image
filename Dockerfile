# Imagem base oficial do Python
FROM python:3.11-slim

# Definir diretório de trabalho dentro do container
WORKDIR /app

# Copiar requirements e instalar dependências
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo o projeto
COPY . .

# Liberar porta usada pelo Flask
EXPOSE 5000

# Rodar o app
CMD ["python", "app.py"]
