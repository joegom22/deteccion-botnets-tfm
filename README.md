<h3 align="center">Framework para la Detección de Botnets en Redes IoT Utilizando Técnicas de Aprendizaje Automático y Microservicios</h3>

<div align="center">

[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](/LICENSE)

</div>

---

<p align="center"> Framework en microservicios para la detección de botnets en redes IoT empleando modelos de aprendizaje automático. Se busca un despliegue modular y portable además de ligero para su uso en capas intermedias del IoT.
    <br> 
</p>

## Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [Usage](#usage)
- [Deployment](#deployment)

## About <a name = "about"></a>

Write about 1-2 paragraphs describing the purpose of your project.

## Getting Started <a name = "getting_started"></a>

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See [deployment](#deployment) for notes on how to deploy the project on a live system.

### Prerequisites

Para usar este framework es necesario emplear un sistema con Docker.

### Installing

Es suficiente con clonar el repositorio.

## Usage <a name="usage"></a>
Los microservicios de captura y análisis son invocados mediante peticiones HTTP (consultar README particular de cada microservicio).

El microservicio de visualización muestra el dashboard de forma permanente y es accesible mediante un navegador web.

## Deployment <a name = "deployment"></a>

Para el despliegue del framework en un sistema basta con construir las imágenes de los microservicios e instanciarlas. Esto puede hacerse de forma sencilla empleando Docker Compose.


