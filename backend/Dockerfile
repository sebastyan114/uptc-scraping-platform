# Etapa de compilación: se usa únicamente para extraer el binario de nuclei
FROM projectdiscovery/nuclei:latest AS nuclei

# Imagen final de la aplicación
FROM python:3.12-slim

# Certificados raíz requeridos para validar conexiones HTTPS salientes
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copia del binario de nuclei desde la etapa de compilación
COPY --from=nuclei /usr/local/bin/nuclei /usr/local/bin/nuclei

# Evita la generación de archivos .pyc y fuerza salida sin buffer en logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Puerto por defecto de la aplicación
ENV PORT=8000

# Usuario sin privilegios para ejecutar la aplicación
RUN useradd -m -u 1000 app \
    && chown -R app:app /home/app

USER app
ENV HOME=/home/app
WORKDIR /app

# Descarga de templates de nuclei en su ubicación por defecto ($HOME/nuclei-templates)
RUN nuclei -update-templates -silent

# Instalación de dependencias (capa separada del código para aprovechar cache de build)
COPY --chown=app:app requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=app:app app ./app

# Puerto de la aplicación (informativo, no publica nada por sí solo)
EXPOSE ${PORT}

# Comando de arranque por defecto
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]