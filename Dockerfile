# 1. Usar una imagen oficial de Python pura e industrial (versión súper estable)
FROM python:3.11-slim

# 2. Configurar el directorio de trabajo dentro del servidor
WORKDIR /app

# 3. Instalar herramientas de construcción del sistema operativo (El "destornillador" automático)
RUN apt-get update && apt-get install -y gcc build-essential

# 4. Copiar nuestro manifiesto de librerías
COPY requirements.txt .

# 5. Instalar todas las librerías con 100% de eficacia
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copiar todo el código de CRISS al servidor
COPY . .

# 7. Exponer el puerto industrial
EXPOSE 8000

# 8. Comando de encendido automático
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
