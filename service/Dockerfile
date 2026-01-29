FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema (curl para healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements y instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY app/ ./app/

# Exponer puerto
EXPOSE 8080

# Comando para ejecutar con uvicorn
# Usar workers según CPUs disponibles para producción
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8080 --workers $(nproc)"]

