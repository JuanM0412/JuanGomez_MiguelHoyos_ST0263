# Usa una imagen base de Python
FROM python:3.12-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar los archivos de requerimientos y los archivos del proyecto
COPY requirements.txt .

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el contenido del proyecto al directorio de trabajo
COPY . .

# Expone los puertos necesarios (ajusta según tus necesidades)
EXPOSE 50051

# Comando por defecto para ejecutar el nodo
CMD ["python", "run_server.py"]
