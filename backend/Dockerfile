FROM python:3.12-slim

# Evita la generación de archivos .pyc y fuerza salida sin buffer en logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Puerto por defecto de la aplicación
ENV APP_PORT=8000

# Usuario sin privilegios para ejecutar la aplicación
RUN useradd -m -u 1000 app \
    && chown -R app:app /home/app

USER app
ENV HOME=/home/app
WORKDIR /app

# Instalación de dependencias (capa separada del código para aprovechar cache de build)
COPY --chown=app:app requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=app:app app ./app

# Puerto de la aplicación (informativo, no publica nada por sí solo)
EXPOSE ${APP_PORT}

# Comando de arranque por defecto
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${APP_PORT}"]