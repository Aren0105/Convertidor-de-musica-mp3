# Usamos una versión ligera de Python (Linux)
FROM python:3.9-slim

# INSTALAMOS FFMPEG (Esto es lo que hace la magia en la nube)
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Preparamos la carpeta de trabajo
WORKDIR /app

# Copiamos los requerimientos e instalamos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código
COPY . .

# Comando para iniciar la app en el puerto que asigne la nube
CMD gunicorn app:app --bind 0.0.0.0:$PORT