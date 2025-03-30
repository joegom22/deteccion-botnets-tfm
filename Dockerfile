FROM python:3.12-slim

WORKDIR /botnet-detection

# Copiar los archivos del proyecto a la carpeta de trabajo
COPY . /botnet-detection

# Asegurarse de que las dependencias estén instaladas
RUN pip install -r requirements.txt

# Comando para ejecutar el script
CMD ["bash"]