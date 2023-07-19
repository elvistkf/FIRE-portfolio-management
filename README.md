# FIRE - Portfolio Management Tool
[![Python Backend Application](https://github.com/elvistkf/FIRE-portfolio-management/actions/workflows/python.yaml/badge.svg)](https://github.com/elvistkf/FIRE-portfolio-management/actions/workflows/python.yaml)

FIRE is a self-hosting web-based portfolio management tool designed to help you make the most optimal investment decisions.

FIRE is containerized using Docker, meaning that it should be compatible with most modern hardware and platforms.

## Technologies
This project used the following technologies:
- Docker
- Python
    - Pandas
    - Numpy
    - Scipy
    - FastAPI
    - SQLModel (based on SQLAlchemy and Pydantic)

Note that you do not need to have the above installed in your systems except Docker.

## Prerequisite
The following operating systems are tested and supported:
- Windows
- MacOS
- Linux
- Synology DiskStation Manager (on x86-based NAS)

In addition, the following software must be installed on your system:
- Docker

## Installation and Setup
To install the application, first clone the project to your system locally:
```
git clone https://github.com/elvistkf/FIRE-portfolio-management.git
```
Then navigate into the root directory of the project,
```
cd FIRE-portfolio-management
```
and run the following docker command:
```
docker compose up -d
```
