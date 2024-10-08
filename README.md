<div align="center">

# Arquitectura P2P y Comunicación entre procesos mediante API REST, RPC y MOM

</div>

### ST0263-242 Tópicos Especiales en Telemática

### Estudiante(s):
- Juan Manuel Gómez P. (jmgomezp@eafit.edu.co)
- Miguel Ángel Hoyos V. (mahoyosv@eafit.edu.co)

### Profesor:
- Edwin Nelson Montoya M. (emontoya@eafit.edu.co)

## 1. Descripción

Este proyecto implementa un sistema de compartición de archivos distribuido y descentralizado basado en una red P2P utilizando DHT y un algoritmo propio de gestión de la red, que se describirá a lo largo del proyecto. El sistema soporta concurrencia y utiliza un middleware para comunicación RPC mediante la tecnología gRPC.

La propuesta define un pequeño servidor que se encarga de armar y mantener la topología de la red gestionando los peers que desean registrarse o abandonar la red. El envío y recepción de archivos dummy se realiza directamente entre los peers. El proyecto plantea una topología basada en pools de peers agrupados en subintervalos, con el objetivo de optimizar el proceso de búsqueda de recursos dentro de la red.

El administrador de la red, al inicializar el servidor, define el número máximo de nodos que podrán estar en la red y el numero de subintervalos. Por ejemplo, se haran los diagramas basados en una red donde el número máximo de nodos es 100 y el numero de sub-intervalos es 4. Esto significa que, en el peor de los casos, se tendrán que recorrer como máximo 25 nodos para buscar un archivo. Si se desea mayor optimización, se puede reducir el tamaño del subintervalo. En promedio, el número de búsquedas necesarias para localizar un archivo es la mitad del tamaño del intervalo.

### 1.1. Aspectos cumplidos

Se obtuvo un excelente resultado final, donde la red se comporta de manera estable, permitiendo el envío y descarga de archivos de manera eficiente. La topología de la red se forma correctamente y todas las pruebas realizadas se pasaron satisfactoriamente. Además del reto de idear un nuevo mecanismo de indexación y búsqueda de archivos, así como de estructuración de la red, se aprendió mucho durante el proceso.

### 1.2. Aspectos no cumplidos

No se pudo implementar Chord DHT, que en la literatura se considera uno de los más óptimos para este tipo de redes. Sin embargo, esto no se considera del todo negativo, ya que la solución planteada también ofrece un muy buen rendimiento. Además, aunque los archivos no se envían directamente a través de la red, esto tampoco se considera un aspecto negativo. Dado que en la definición del proyecto y en los requerimientos solicitados los archivos eran dummy, se cumplió con lo esperado.

## 2. Diseño de alto nivel

### 2.1. Arquitectura

#### 2.1.0 Diagrama de clases

![8c05efdb-4a41-4d0a-b86a-bbbe7c0dbd6b](https://github.com/user-attachments/assets/52eeae76-224b-49a0-9fea-8d6fb3890f2c)

![21eba605-ffe5-4cca-87f3-90207f028dab](https://github.com/user-attachments/assets/c126ff84-4e87-4cf4-9492-853a2ce84b4a)

#### 2.1.1 Diagrama de arquitectura 
En el siguiente diagrama simplificado de la arquitectura, se observa cómo todos los peers están conectados al servidor para ejecutar funciones como registrarse en la red, salir de la red y solicitar los intervalos de peers, los cuales procesarán internamente para enviar y recibir archivos. Todas las comunicaciones se realizan mediante gRPC, y no hay restricciones para que los peers se comuniquen entre sí (aunque por simplicidad, no se muestra la conexión entre todos los peers en el diagrama).

![a844222f-b75b-4c09-b199-5929f62766eb](https://github.com/user-attachments/assets/00c0e4b3-72cd-4432-8610-aedb0fe3c284)

#### 2.1.2 Diagrama de sub-espacios 
En el siguiente diagrama se observa la gestión de subespacios por parte del servidor para una red de 100 nodos con un tamaño de subespacio de 25. En la primera imagen, se muestran todos los subintervalos definidos pero vacíos. Posteriormente, en la segunda imagen, se ve cómo se asigna el primer peer al primer subintervalo.

En la última imagen, se observa la red bien constituida. Para el correcto funcionamiento de la búsqueda y localización de archivos, los peers se ubican dentro de los intervalos en orden de llegada, de menor a mayor. Es decir, después de la llegada del primer peer, se añadió el segundo nodo, que tomó el ID 26 en el segundo subintervalo. El tercer peer que decidió unirse a la red tomó el ID 51 en el tercer intervalo, y finalmente, el cuarto peer se unió con el ID 76 en el último subintervalo. A partir de ese punto, todos los peers que llegaron se asignaron de manera aleatoria dentro de cada subintervalo, pero respetando el orden de asignación de IDs, que también va de menor a mayor.

![fab133ea-06bf-47f6-95a9-9e131e62639a](https://github.com/user-attachments/assets/b231d9e2-1108-40d7-a7a9-9db9e265b0dd)

### 2.2. Patrones

No se utilizó ningún patrón de diseño específico, pero se aplicaron los principios SOLID. El código está bien desacoplado. Además, si se quisiera implementar un patrón de diseño, como el patrón Observer para la función de reenviar los archivos que no son propios de la zona, se podría hacer de manera muy sencilla. También sería posible implementar un Singleton para la creación del servidor; sin embargo, dado que el código está diseñado para que no haya más de un servidor, en ese sentido se cumplió con lo requerido.

## 3. Descripción del ambiente de desarrollo y técnico: lenguaje de programación, librerías, paquetes, etc., con sus números de versiones.

### 3.1. Compilación y ejecución

#### 3.1.1. Generar y preparar el código fuente
1. Clonar el repositorio:
    ```
    git clone https://github.com/JuanM0412/JuanGomez_MiguelHoyos_ST0263.git
    ```
2. Acceder al directorio que se creó como consecuencia del paso anterior:
    ```
    cd JuanGomez_MiguelHoyos_ST0263/
    ```
3. Cambiar el archivo `.env.example` a `.env`:
    ```
    mv .env.example .env
    ```
4. Modificar archivo el archivo `.env` según la necesidad.

#### 3.1.2. Ejecución el local
1. Crear y activar un ambiente virtual:
    ```
    python -m venv venvname
    source venvname/bin/activate
    ```
    **Nota:** Reemplazar `venvname` con un nombre más adecuado, como lo puede ser `p2p_network`.
2. Instalar las dependencias:
    ```
    pip install -r requirements.txt
    ```
3. Ejecutar el servidor:
    ```
    python run_server.py
    ```
4. Ejecutar un peer:
    ```
    python peer.py
    ```
**Nota:** Para el correcto funcionamiento de estas últimas dos instrucciones se recomienda ir al archivo `.env` y cambiar el puerto y que no se repitan, es decir, que un peer y el servidor no tengan el mismo puerto, o que dos peers tengan el mismo puerto. Esto para evitar conflictos.

#### 3.1.3. Desplegar servidor en la nube usando Docker
1. Crear la imagen de Docker:
    ```
    docker build -t p2p_network .
    ```
2. Ejecutar un contenedor de Docker a partir de la imagen creada en el paso anterior:
    ```
    docker run -it --name p2p_server -p 50051:50051 p2p_network
    ```
    **Nota:** En este caso estamos ejecutando el contenedor de forma interactiva, si se quiere ejecutar en segundo plano se debe reemplazar `-it` por `-d`. Además, se deben reemplazar los puertos (`50051:50051`) según la necesidad.
3. Conectar peers a este servidor.

### 3.2. Detalles del desarrollo y detalles técnicos

Se utilizó Python (3.12.x) como lenguaje de programación y gRPC (1.66.0) como middleware RPC. Entre las bibliotecas más relevantes que se emplearon, se encuentran las bibliotecas nativas de Python, como request (2.31.0), dotenv (1.0.1), random y os, entre otras necesarias para la implementación de ciertas funcionalidades. Se evitó un alto acoplamiento en el desarrollo. Además, se utilizó Docker (24.0.7) como servicio de virtualización y se desplegó el servidor en instancias EC2 (Ubuntu 24.04) de AWS.

### 3.3. Parámetros

En cuanto a los parámetros del programa, existe un archivo llamado .env.example que debe ser renombrado a .env. Dentro de este archivo se encuentran los parámetros de ejecución del proyecto, que incluyen los atributos del servidor, como la dirección IP, el puerto, el número máximo de nodos, y la cantidad de subespacios que se van a crear. Además, están los parámetros de cada peer, que incluyen la dirección IP, el puerto, y la carpeta donde se descargarán los archivos de la red.

## 4. Vídeo sustentación
[Link al vídeo](https://eafit-my.sharepoint.com/:v:/g/personal/jmgomezp_eafit_edu_co/EdRBT5zuhCFAu1VirjoFUd4B3P5vFm53v5r0HSolpHlWrg?nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJTdHJlYW1XZWJBcHAiLCJyZWZlcnJhbFZpZXciOiJTaGFyZURpYWxvZy1MaW5rIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXcifX0%3D&e=g0xQWf)

## 5. Referencias:
- [https://github.com/st0263eafit/st0263-242/blob/main/README-template.md](https://github.com/st0263eafit/st0263-242/blob/main/README-template.md)
- [https://en.wikipedia.org/wiki/Chord_(peer-to-peer)](https://en.wikipedia.org/wiki/Chord_(peer-to-peer))
- [https://grpc.io/docs/languages/python/basics/](https://grpc.io/docs/languages/python/basics/)
