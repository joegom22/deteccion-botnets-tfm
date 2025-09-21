<h1 align="center">Microservice: Traffic Visualizer</h1>

<p align="center"> Microservicio que expone un Dashboard de Streamlit en el que se presentan los resultados de la predicción realizada y almacenada en un archivo CSV.
</p>

## Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [Deployment](#deployment)
- [Built Using](#built_using)
- [Authors](#authors)

## About <a name = "about"></a>

**Traffic Visualizer** es un microservicio desarrollado como parte de un sistema de detección de botnets en redes IoT. Este permite visualizar datos sobre predicciones que se encuentren almacenadas en el sistema. Su diseño dockerizado permite que se integre fácilmente con otros dispositivos.

Este componente representaría el último paso de la pipeline de detección de botnets en redes IoT.

## Getting Started <a name = "getting_started"></a>

Estas instrucciones te permitirán desplegar el servicio de forma local o como parte de un sistema basado en Docker Compose.

### Prerequisites

Para su uso es necesario tener:
- Docker instalado
- Linux (recomendado)
- Permisos para ejecutar contenedores

### Installing
#### Microservicio autónomo
Para poder tener el microservicio corriendo deben seguirse los siguientes pasos: <br>
1. Clonar el repositorio
2. Crea un volumen compartido si no existe
3. Construye el contenedor
4. Lanza el contenedor manualmente
#### Docker Compose
Para poder tener todo el sistema operativo deben seguirse los siguientes pasos: <br>
1. Clonar el repositorio
2. Crea un volumen compartido si no existe
3. Docker compose up --build

## Deployment <a name = "deployment"></a>

Este servicio se integra con otros microservicios mediante Docker Compose.

## Built Using <a name = "built_using"></a>

- Docker – Containerización y despliegue

- Python 3.10 – Lenguaje base

- Prometheus - Recogida de métricas

## Authors <a name = "authors"></a>

- [@joegom22](https://github.com/joegom22)

