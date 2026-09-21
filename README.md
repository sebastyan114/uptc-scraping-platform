Plataforma web para realizar scraping controlado y análisis de seguridad sobre sitios web

Estado actual
- Backend FastAPI ejecutándose en Docker
- PostgreSQL 16 disponible para datos relacionales
- Qdrant disponible para búsqueda vectorial
- Variables de entorno mediante `.env`
- Endpoints de salud para backend, PostgreSQL y Qdrant
- Documentación OpenAPI/Swagger disponible


Antes de iniciar, instala:

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Docker Compose v2, incluido normalmente con Docker Desktop
- Git


Verifica que Docker esté funcionando:

```bash
docker --version
docker compose version
```

## Estructura del proyecto

```text
uptc-scraping-platform/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   └── config.py
│   │   ├── __init__.py
│   │   └── main.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
├── infra/
├── .env.example
├── .gitignore
├── docker-compose.yml
└── README.md
```


Inicio 
2. Crear el archivo de variables de entorno Copy-Item .env.example .env

 3. Levantar los servicios  docker compose up --build o para segundo plano docker compose up --build -d

 4. Verificar los servicios

  API raíz | [http://localhost:8000/](http://localhost:8000/)


  | Salud de PostgreSQL | [http://localhost:8000/health/postgres]

  (http://localhost:8000/health/qdrant) | `service: qdrant` |

   Swagger/OpenAPI | [http://localhost:8000/docs](http://localhost:8000/docs) | Documentación interactiva de FastAPI |

   ReDoc | [http://localhost:8000/redoc](http://localhost:8000/redoc) | Documentación alternativa de la API |

   Endpoints disponibles


## Variables de entorno

El archivo `.env.example` contiene valores seguros para desarrollo local.

```env
APP_NAME=UPTC Scraping Platform API
APP_VERSION=0.1.0
APP_ENV=development

BACKEND_PORT=8000

DATABASE_URL=postgresql+asyncpg://websec_user:websec_password@postgres:5432/websec

QDRANT_URL=http://qdrant:6333
QDRANT_COLLECTION=analysis_embeddings

MAX_REQUESTS_PER_SECOND=1.0
TARGET_TIMEOUT_SECONDS=10


Dentro de Docker Compose, el backend se conecta a otros servicios por el nombre del servicio:

```env
DATABASE_URL=postgresql+asyncpg://websec_user:websec_password@postgres:5432/websec
QDRANT_URL=http://qdrant:6333
```
