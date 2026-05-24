# 1. Usar imagen oficial de Python
FROM python:3.11-slim

# 2. Configurar directorio
WORKDIR /app

# 3. Herramientas base
RUN apt-get update && apt-get install -y gcc build-essential

# 4. Copiar todo tu código a la nube
COPY . .

# 5. INSTALACIÓN DIRECTA (Ignoramos el requirements.txt vacío)
RUN pip install --no-cache-dir fastapi uvicorn supabase postgrest google-generativeai pydantic python-dotenv

# 6. Encendido automático adaptado a Render
CMD uvicorn api:app --host 0.0.0.0 --port $PORT
