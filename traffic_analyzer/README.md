<h1 align="center">Microservice: Traffic Analyzer</h1>

<p align="center"> Microservicio que expone una API HTTP para analizar tráfico de red empleando un modelo de aprendizaje automático a elección y guarda las predicciones junto a sus probabilidades en un fichero CSV.
</p>

## Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [Deployment](#deployment)
- [Usage](#usage)
- [Built Using](#built_using)
- [Authors](#authors)

## About <a name = "about"></a>

**Traffic Analyzer** es un microservicio desarrollado como parte de un sistema de detección de botnets en redes IoT. Este permite analizar tráfico de red a través de una solicitud HTTP utilizando un modelo de aprendizaje automático. Su diseño dockerizado permite que se integre fácilmente con otros dispositivos.

Este componente representaría el segundo paso de la pipeline de detección de botnets en redes IoT.

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

Para iniciar el análisis se envía una solicitud HTTP como la siguiente:
```
curl -X POST http://localhost:8000/analyze \
     -H "Content-Type: application/json" \
     -H "x-token: DUMMY_TOKEN" \
     -d '{"file_path": "/app/shared/flows_summary.csv", "model": "XGBoost"}'

```
Donde el parámetro file_path debe ser la ruta al fichero de flujos a analizar y model el modelo a emplear por el microservicio.

## Built Using <a name = "built_using"></a>

- FastAPI – Web framework para la API REST

- Uvicorn – Servidor ASGI

- Docker – Containerización y despliegue

- Python 3.10 – Lenguaje base

- Prometheus - Recogida de métricas

## Authors <a name = "authors"></a>

- [@joegom22](https://github.com/joegom22)
