# Imagem base oficial do Python
FROM python:3.11-slim

# Definir diretório de trabalho dentro do container
WORKDIR /app

# Copiar todo o projeto
COPY . .

# Instalar dependências
RUN pip install -r requirements.txt

# Liberar porta usada pelo Flask
EXPOSE 5000

# Rodar o app
CMD ["python", "app.py"]
