<h1 align="center">Microservice: Traffic Gatherer</h1>

<p align="center"> Microservicio que expone una API HTTP para capturar tráfico de red durante un periodo de tiempo definido y guarda el resultado como archivo `.pcap` en un volumen compartido para su posterior análisis. Además, procesa flujos conversacionales en el tráfico y genera archivos CSV con los flujos.
</p>

## Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [Deployment](#deployment)
- [Usage](#usage)
- [Built Using](#built_using)
- [Authors](#authors)

## About <a name = "about"></a>

**Traffic Gatherer** es un microservicio desarrollado como parte de un sistema de detección de botnets en redes IoT. Este permite capturar tráfico de red a través de una solicitud HTTP utilizando `tshark`. Su diseño dockerizado permite que se integre fácilmente con otros dispositivos.

Este componente representaría el primer paso de la pipeline de detección de botnets en redes IoT.

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

## Usage <a name="usage"></a>

Para iniciar la captura se envía una solicitud HTTP.
```
curl -X POST http://localhost:9000/gather \
     -H "Content-Type: application/json" \
     -H "x-token: DUMMY_TOKEN" \
     -d '{"duration": 30}'
```
Donde el parámetro duration debe ser la cantidad de tiempo en segundos durante los que se recolectará el tráfico.

## Built Using <a name = "built_using"></a>

- FastAPI – Web framework para la API REST

- Uvicorn – Servidor ASGI

- tshark – Captura de tráfico de red

- Docker – Containerización y despliegue

- Python 3.10 – Lenguaje base

- Prometheus - Recogida de métricas

## Authors <a name = "authors"></a>

- [@joegom22](https://github.com/joegom22)
