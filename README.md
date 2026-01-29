# POC - Performance Testing con JMeter en Docker

Stack completo dockerizado para ejecutar pruebas de performance con JMeter contra un servicio mock. Todo corre en contenedores, no necesitas instalar nada más que Docker.

## Func

1. **API Mock** (FastAPI): Servicio HTTP que simula un backend bancario con latencias y errores configurables
2. **JMeter 5.6.3**: Motor de pruebas de carga en modo non-GUI
3. **Docker Compose**: Orquestación de ambos servicios con networking, healthchecks y resource limits

Todo está dockerizado.

## Arquitectura del Stack

```
┌─────────────────────────────────────────┐
│  docker-compose.yml                     │
│  ┌────────────────┐  ┌────────────────┐│
│  │   api:8080     │  │   jmeter       ││
│  │  (FastAPI)     │◄─┤  (profile:test)││
│  │                │  │                ││
│  │ Resources:     │  │ Resources:     ││
│  │ 1 CPU, 512MB   │  │ 2 CPU, 2GB     ││
│  └────────────────┘  └────────────────┘│
│           │                  │          │
│     performance-network      │          │
│           │                  │          │
│       healthcheck    volumes mounted    │
│                      (test-plans/       │
│                       results/)         │
└─────────────────────────────────────────┘
```

## Prerequisitos

Solo necesitas tener Docker y Docker Compose instalados en el servidor donde vas a correr las pruebas.

**Verificar versiones:**
```bash
docker --version          # >= 20.10
docker-compose --version  # >= 2.0
```

## Quick Start

### 1. Clonar el repo y levantar el servicio

```bash
# En el servidor de pruebas
git clone <este-repo>
cd poc-performance

# Levantar el API en background
docker-compose up -d --build api

# Verificar que levantó bien
docker-compose ps
docker-compose logs -f api

# Probar el health check
curl http://localhost:8080/health
```

### 2. Ejecutar las pruebas de performance

```bash
# Ejecutar JMeter con el test plan incluido
docker-compose --profile test run --rm jmeter \
  -n \
  -t /jmeter/test-plans/test-plan.jmx \
  -l /jmeter/results/results.jtl \
  -e \
  -o /jmeter/results/html-report

# Los resultados quedan en ./jmeter/results/
```

### 3. Ver los resultados

```bash
# Abrir el reporte HTML generado
open jmeter/results/html-report/index.html

# O copiar los resultados a otro lado
scp -r jmeter/results/* usuario@servidor:/path/destino/
```

## Validar que Funciona

**Smoke test manual** - Verificar que todos los endpoints responden:

```bash
# Health check (sin latencia)
curl http://localhost:8080/health

# GET account (latencia 20-80ms)
curl http://localhost:8080/api/accounts/1

# GET balance (latencia 20-80ms) 
curl http://localhost:8080/api/accounts/1/balance

# POST transfer (latencia 50-200ms)
curl -X POST http://localhost:8080/api/transfers \
  -H "Content-Type: application/json" \
  -d '{"from_account":"1","to_account":"2","amount":100}'

# GET transfer status
curl http://localhost:8080/api/transfers/{transfer_id}
```

Si todos responden con 200/201, el API está listo para las pruebas.

## Configuración del Test Plan

El test plan incluido (`jmeter/test-plans/test-plan.jmx`) ejecuta un test básico:

**Configuración de carga:**
- 10 usuarios concurrentes
- Ramp-up: 10 segundos (1 usuario/segundo)
- Duración: 60 segundos
- Loops: infinito (hasta que se cumplan los 60 segundos)

**Endpoints testeados:**
1. `GET /health`
2. `GET /api/accounts/1/balance`
3. `POST /api/transfers`

**Request por minuto esperados:**
Aproximadamente 600-1000 requests dependiendo de las latencias del API.

## Modificar el Test Plan

Si necesitas cambiar los parámetros de carga, edita `jmeter/test-plans/test-plan.jmx`:

```xml
<!-- Cambiar número de usuarios -->
<stringProp name="ThreadGroup.num_threads">50</stringProp>

<!-- Cambiar ramp-up time (segundos) -->
<stringProp name="ThreadGroup.ramp_time">30</stringProp>

<!-- Cambiar duración total (segundos) -->
<stringProp name="ThreadGroup.duration">300</stringProp>
```

O crear tu propio test plan y guardarlo en `jmeter/test-plans/`.

## Entender los Resultados

Después de ejecutar JMeter, vas a tener:

### 1. Archivo JTL (`results.jtl`)
CSV con cada request individual:
- timestamp
- elapsed time (ms)
- response code
- success/failure
- bytes enviados/recibidos

**Útil para:** Importar en herramientas de análisis, Excel, Grafana, etc.

### 2. Reporte HTML (`html-report/`)
Dashboard interactivo con:
- **Dashboard**: Overview de métricas principales
- **APDEX**: Application Performance Index
- **Requests Summary**: Tabla con stats por endpoint
- **Charts**: Gráficos de throughput, latencias, errores
- **Response Times**: Percentiles (50, 90, 95, 99)

**Métricas clave a revisar:**
- **Throughput**: requests/segundo que soporta el API
- **P95/P99 Response Time**: Latencias en percentiles altos
- **Error %**: Debe ser ~1% (es el valor configurado en el mock)

## API Mock - Endpoints Disponibles

| Endpoint | Método | Latencia | Códigos | Descripción |
|----------|--------|----------|---------|-------------|
| `/health` | GET | 0ms | 200 | Health check - nunca falla |
| `/api/accounts/{id}` | GET | 20-80ms | 200, 404, 500 (1%) | Info de cuenta (IDs válidos: 1-100) |
| `/api/accounts/{id}/balance` | GET | 20-80ms | 200, 404, 500 (1%) | Saldo de cuenta |
| `/api/transfers` | POST | 50-200ms | 201, 400, 404, 500 (1%) | Crear transferencia |
| `/api/transfers/{id}` | GET | 20-80ms | 200, 404, 500 (1%) | Estado de transferencia |

**Datos mock:**
- 100 cuentas en memoria (IDs 1-100)
- Balances aleatorios entre $1,000 y $100,000
- Sin persistencia (se resetea al reiniciar el contenedor)

**Comportamiento simulado:**
- 1% de probabilidad de error 500 en cada request (excepto `/health`)
- Latencias variables para simular carga real
- Logging JSON estructurado con request_id único

## Docker Compose - Detalles de la Configuración

### Servicio: `api`

```yaml
services:
  api:
    build: ./service
    container_name: banking-api
    ports:
      - "8080:8080"
    resources:
      cpus: '1'
      memory: 512M
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 10s
      timeout: 5s
      retries: 3
```

**Explicación:**
- Expone puerto 8080 en el host
- Limita recursos a 1 CPU y 512MB (ajustar según capacidad del servidor)
- Healthcheck automático cada 10 segundos
- Uvicorn con workers dinámicos según CPUs disponibles

**Imagen base:** `python:3.11-slim`
**Stack:** FastAPI + Uvicorn (async workers)

### Servicio: `jmeter`

```yaml
services:
  jmeter:
    build: ./jmeter
    container_name: jmeter-test
    profiles:
      - test
    depends_on:
      api:
        condition: service_healthy
    volumes:
      - ./jmeter/test-plans:/jmeter/test-plans
      - ./jmeter/results:/jmeter/results
    resources:
      cpus: '2'
      memory: 2G
```

**Explicación:**
- Perfil `test`: solo arranca con `--profile test` (no por defecto)
- Espera a que `api` pase el healthcheck antes de empezar
- Monta volúmenes locales para test plans y resultados
- Más recursos que el API porque JMeter genera la carga

**Imagen base:** `openjdk:11-jre-slim`
**JMeter version:** 5.6.3 (descargado desde Apache Mirror)

### Red Docker

```yaml
networks:
  performance-network:
    driver: bridge
```

Ambos servicios en la misma red bridge. El nombre `api` resuelve automáticamente dentro del contenedor de JMeter (DNS interno de Docker).

## Ajustar Recursos según el Servidor

Edita `docker-compose.yml` según las specs del servidor:

```yaml
# Servidor pequeño (2 CPUs, 4GB RAM)
api:
  resources:
    limits:
      cpus: '0.5'
      memory: 256M

jmeter:
  resources:
    limits:
      cpus: '1'
      memory: 1G

# Servidor mediano (4 CPUs, 8GB RAM)
api:
  resources:
    limits:
      cpus: '1'
      memory: 512M

jmeter:
  resources:
    limits:
      cpus: '2'
      memory: 2G

# Servidor grande (8+ CPUs, 16GB+ RAM)
api:
  resources:
    limits:
      cpus: '2'
      memory: 1G

jmeter:
  resources:
    limits:
      cpus: '4'
      memory: 4G
```

## Troubleshooting
```

### Performance pobre del API

```bash
# Ver uso de recursos
docker stats banking-api

# Si está al límite de CPU/RAM, aumentar en docker-compose.yml
# O reducir workers de Uvicorn editando service/Dockerfile:
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]
```

## Estructura de Archivos

```
poc-performance/
├── docker-compose.yml          # Orquestación de servicios
├── README.md                   # Esta documentación
├── jmeter/
│   ├── Dockerfile             # Imagen de JMeter 5.6.3
│   ├── test-plans/
│   │   └── test-plan.jmx      # Test plan incluido
│   └── results/               # Resultados de las pruebas (generado)
│       ├── results.jtl
│       └── html-report/
└── service/
    ├── Dockerfile             # Imagen del API mock
    ├── requirements.txt       # Dependencias Python
    └── app/
        ├── main.py           # FastAPI app + config
        ├── routes/           # Endpoints (health, accounts, transfers)
        └── models/           # Pydantic schemas
```

# poc-performance-jmeter
