# Usa una imagen base de Python
FROM python:3.11-slim

# Configura el directorio de trabajo
WORKDIR /app

# Copia los archivos necesarios al contenedor
COPY . /app

# Instala las dependencias del proyecto
RUN pip install --no-cache-dir -r requirements.txt

# Compila el archivo .proto a archivos Python
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. peer.proto

# Expone los puertos necesarios (ajusta según tus necesidades)
EXPOSE 50051  # Puerto para gRPC
EXPOSE 8000   # Puerto para FastAPI

# Comando por defecto para ejecutar el nodo
CMD ["python", "node.py"]
