# Platform Engineering Microservices

A fictitious **cloud-native e-commerce application** built with polyglot microservices, demonstrating modern architectural patterns including independent deployability, per-service databases, reactive programming, and container-native deployment on Kubernetes.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Services](#services)
- [Data Flow](#data-flow)
- [Databases & Data Stores](#databases--data-stores)
- [Inter-Service Communication](#inter-service-communication)
- [Docker & Container Setup](#docker--container-setup)
- [Kubernetes Deployment](#kubernetes-deployment)
- [CI/CD](#cicd)
- [Authentication & Security](#authentication--security)
- [Getting Started](#getting-started)
  - [Running Locally](#running-locally)
  - [Deploying to Kubernetes (Minikube)](#deploying-to-kubernetes-minikube)
  - [Deploying to AWS (EKS)](#deploying-to-aws-eks)

---

## Architecture Overview

```
                        ┌─────────────────────────────┐
                        │         store-ui             │
                        │   React SPA (port 3000)      │
                        │   served by nginx             │
                        └──────┬──────────┬────────────┘
                               │          │
             ┌─────────────────┘          └──────────────────┐
             │                                               │
   ┌─────────▼──────────┐                        ┌──────────▼─────────┐
   │  products-service  │                        │   search-service   │
   │  Node.js / Express │                        │  Node.js / Express │
   │  port 5000          │                        │  port 4000         │
   │  MongoDB            │                        │  ElasticSearch     │
   └────────────────────┘                        │  (proxied)         │
                                                  └────────────────────┘
             ┌────────────────────────────────────────────┐
             │                                            │
   ┌─────────▼──────────┐                    ┌───────────▼────────────┐
   │   cart-service     │                    │    users-service       │
   │  Java / Spring Boot│                    │   Python / FastAPI     │
   │  port 8080          │                    │   port 9090            │
   │  Redis              │                    │   PostgreSQL (prod)    │
   └────────────────────┘                    └────────────────────────┘
```
### UI/UX, Architecture & Technologies Used

Architecture         |  Application UI/UX
:-------------------------:|:-------------------------:
<img src="architecture.png" alt="Architecture"> | <img src="app-showcase.png" alt="Application UI"> 

**Technology choices at a glance:**

| Concern | Choice |
|---|---|
| Languages | Node.js, Java 17, Python 3.11 |
| Frameworks | Express, Spring Boot + WebFlux, FastAPI |
| Databases | MongoDB, Redis, PostgreSQL, ElasticSearch |
| Containerization | Docker (multi-stage builds, non-root users) |
| Orchestration | Kubernetes (Kustomize base + overlays) |
| Service mesh | Istio (on GKE platform deployment) |

---

## Services

### Products Service (`products-cna-microservice/`)

| Attribute | Detail |
|---|---|
| Language / Framework | Node.js 18 / Express.js |
| Port | `5000` |
| Database | MongoDB |
| Docker base | `node:18-alpine` |

**API Routes:**

| Method | Path | Description |
|---|---|---|
| `GET` | `/deals` | Promotional deals (max 50 records) |
| `GET` | `/products/sku/:id` | Product by variant SKU |

**Key details:**
- Seed data loaded from `data/products.json` and `data/deals.json` at startup
- Pre-commit hooks via husky + lint-staged (eslint + prettier enforce code style)
- `nodemon` for hot-reload in development

---

### Cart Service (`cart-cna-microservice/`)

| Attribute | Detail |
|---|---|
| Language / Framework | Java 17 / Spring Boot 2.7.1 + Spring WebFlux |
| Build tool | Gradle 7.5 |
| Port | `8080` |
| Database | Redis (in-memory session store) |
| Docker base | `eclipse-temurin:17-jre-alpine` (multi-stage — Gradle builder) |

**API Routes:**

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Health / index |
| `GET` | `/cart` | List all carts |
| `GET` | `/cart/{customerId}` | Get cart for a specific customer |
| `POST` | `/cart` | Create or update cart — calculates total |

**Key details:**
- Fully **reactive / non-blocking** via `ReactiveRedisTemplate` and Spring WebFlux
- Jackson JSON serialization for Redis object storage
- `spring-cloud-starter-sleuth` for distributed tracing propagation
- `resilience4j` circuit breaker support
- Multi-stage Docker build: Gradle compiles JAR → minimal JRE-only runtime image
- Container runs as non-root (`spring:spring`)

---

### Users Service (`users-cna-microservice/`)

| Attribute | Detail |
|---|---|
| Language / Framework | Python 3.11 / FastAPI + async SQLAlchemy |
| Package manager | pipenv |
| Port | `9090` |
| Database | PostgreSQL (production) / SQLite (local dev) |
| Docker base | `python:3.11-alpine` (multi-stage) |

**API Routes:**

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/users` | Create user (name, email, mobile) |
| `GET` | `/users` | List all users |
| `GET` | `/users/{user_id}` | Get user by ID |
| `PUT` | `/users/{user_id}` | Update user |

**Key details:**
- Fully **async/await** throughout — `asyncpg` driver for PostgreSQL, `aiosqlite` for local dev
- SQLAlchemy ORM with connection pooling for PostgreSQL
- Pydantic schemas for request/response validation
- Seed data injected on startup
- Gunicorn + 4 Uvicorn workers in Docker — production-ready concurrency
- Container runs as non-root (`app:app`)

---

### Search Service (`search-cna-microservice/`)

| Attribute | Detail |
|---|---|
| Language / Framework | Node.js 18 / Express.js |
| Port | `4000` |
| Backend | ElasticSearch (proxied via `ELASTIC_URL` env var) |
| Docker base | `node:18-alpine` |

**API Routes:**

All routes (GET + POST) are transparently proxied to the ElasticSearch backend — request body and query parameters are passed through as-is.

**Key details:**
- Thin proxy — no business logic; enables autocomplete, typeahead, and faceted product search
- `ELASTIC_URL` environment variable controls the upstream ElasticSearch endpoint

---

### Store UI (`store-ui/`)

| Attribute | Detail |
|---|---|
| Framework | React (CRA), Material UI, TypeScript/JavaScript |
| Dev port | `3000` |
| Production serving | nginx `1.21.6-alpine` |
| Docker build | Multi-stage: Node builds bundle → nginx serves static files |

**Key details:**
- SPA with client-side routing (`try_files $uri /index.html` in nginx config)
- Communicates with all four backend services via HTTP
- Production Docker image serves only the compiled static bundle — no Node.js runtime

---

## Data Flow

```
1. User opens store-ui in browser
2. UI fetches product catalog   →  GET /products/sku/:id, GET /deals   →  products-service  →  MongoDB
3. User searches for products   →  proxied query                        →  search-service    →  ElasticSearch
4. User adds item to cart       →  POST /cart                           →  cart-service      →  Redis
5. UI retrieves cart            →  GET /cart/{customerId}               →  cart-service      →  Redis
6. User manages account         →  CRUD /users                          →  users-service     →  PostgreSQL
```

All communication is **synchronous REST over HTTP** — no message queues or event streaming.

---

## Databases & Data Stores

| Database | Version | Used By | Kubernetes Namespace | Notes |
|---|---|---|---|---|
| MongoDB | `mongo:latest` | Products | `shared-services` | Collections: `products`, `deals`; init script sets root credentials |
| Redis | `redis:7-alpine` | Cart | `shared-services` | Session/cart storage; empty password in local dev |
| PostgreSQL | CNPG-managed (prod) / SQLite (dev) | Users | `postgres` (GKE platform) | Async connection pooling via asyncpg |
| ElasticSearch | `elasticsearch:8.2.3` | Search | `shared-services` | Security disabled, single-node, `vm.max_map_count` set via initContainer |

On the **GKE platform**, PostgreSQL is managed by CloudNativePG with 3-instance HA and continuous backup to GCS. Locally, SQLite is used for zero-config development.

---

## Inter-Service Communication

- **Pattern:** Synchronous REST over HTTP
- **Service discovery:** Kubernetes DNS (e.g., `mongo-service.shared-services.svc.cluster.local`)
- **No async messaging:** No Kafka, RabbitMQ, or event streaming between services
- **Frontend → backend:** React UI makes direct HTTP calls to each microservice endpoint

On the GKE platform, Istio Ambient mode provides **transparent mTLS** for all service-to-service communication without requiring application-level TLS configuration.

---

## Docker & Container Setup

### Image Build Strategy

| Service | Build Strategy | Runtime Image |
|---|---|---|
| Products | Single-stage | `node:18-alpine` |
| Cart | Multi-stage (Gradle builder) | `eclipse-temurin:17-jre-alpine` |
| Users | Multi-stage (pipenv install) | `python:3.11-alpine` |
| Search | Single-stage | `node:18-alpine` |
| Store UI | Multi-stage (Node build → nginx serve) | `nginx:1.21.6-alpine` |

### Image Registry

Images are pushed to GCP Artifact Registry:
```
us-central1-docker.pkg.dev/pe-staging-project-*/images/<service-name>
```

Multi-platform builds target `linux/amd64`.

---

## Kubernetes Deployment

### Structure (Kustomize base + overlays)

```
infra/k8s/
├── apps/
│   ├── base/                         # Deployments + ClusterIP Services per microservice
│   │   ├── products/
│   │   ├── cart/
│   │   ├── users/
│   │   ├── search/
│   │   ├── store-ui/
│   │   └── namespace.yaml            # e-commerce namespace
│   └── overlays/
│       └── local/                    # Minikube overrides
│           ├── products/             # ConfigMap: MONGO_URI, DATABASE
│           ├── cart/                 # ConfigMap: SPRING_REDIS_HOST, PORT, PASSWORD
│           ├── users/
│           ├── search/
│           └── store-ui/             # NodePort service for local browser access
└── shared-services/
    ├── base/                         # MongoDB, Redis, ElasticSearch Deployments + Services + Secrets
    │   ├── mongodb/
    │   ├── redis/
    │   ├── elasticsearch/
    │   └── namespace.yaml            # shared-services namespace
    └── overlays/
        └── local/                    # NodePort services for local dev access
```

### Namespaces

| Namespace | Contents |
|---|---|
| `e-commerce` | All microservice workloads |
| `shared-services` | Shared databases (MongoDB, Redis, ElasticSearch) |

### On the GKE Platform

When deployed to GKE via ArgoCD, the `users` and `store-ui` services additionally get:
- `istio-injection=enabled` on their namespace → full Envoy sidecar injection
- `VirtualService` and `DestinationRule` resources for Istio traffic management
- `VerticalPodAutoscaler` for automatic resource right-sizing
- Resource `requests` and `limits` defined on all containers

---

## CI/CD

| Service | CI Status | Details |
|---|---|---|
| Products | `.github/workflows/node.js.yml` | Push/PR to `master` → `npm ci` → `npm test` |
| Cart | Not configured | No GitHub Actions workflow |
| Users | Not configured | No GitHub Actions workflow |
| Search | Not configured | No GitHub Actions workflow |
| Store UI | Not configured | No GitHub Actions workflow |

The platform-level GitOps deployment is handled by ArgoCD in the [platform-engineering-project](../platform-engineering-project) repository — any image push triggers a manifest update and ArgoCD reconciles the cluster.

**Performance testing:** `infra/performance/JMeter Test Plan.jmx` for load testing the application stack.

---

## Authentication & Security

**Current state:** Minimal — the application is a demonstration project.

- No OAuth2, JWT, or API key validation on any service
- Cart service uses a hardcoded customer ID (`john@example.com`)
- All endpoints are publicly accessible within the cluster
- ElasticSearch runs with security disabled
- Redis has no password set in local dev configs

**On GKE:** Network-level security is provided by Istio Ambient mTLS, Cloud Armor DDoS protection, and Cloudflare rate limiting — all managed by the platform layer.

---

## Getting Started

### Prerequisites

- Node.js 18+
- Java 17, Gradle 7.5
- Python 3.11, pipenv
- Docker
- kubectl + Minikube (for local k8s deployment)

### Running Locally (Per-Service)

**Products:**
```bash
cd products-cna-microservice
npm install
npm start
# Requires: MongoDB running locally or via Docker
```

**Cart:**
```bash
cd cart-cna-microservice
# Set env vars: SPRING_REDIS_HOST, SPRING_REDIS_PORT
gradle bootRun
# Requires: Redis running locally or via Docker
```

**Users:**
```bash
cd users-cna-microservice
pipenv install
pipenv shell
python app.py
# Uses SQLite locally — no database setup needed
```

**Search:**
```bash
cd search-cna-microservice
npm install
ELASTIC_URL=http://localhost:9200 npm start
# Requires: ElasticSearch running locally
```

**Store UI:**
```bash
cd store-ui
npm install
npm start
# Opens at http://localhost:3000
```

### Deploying to Kubernetes (Minikube)

```bash
# Start Minikube
minikube start --driver=hyperkit   # macOS
minikube start --driver=hyperv     # Windows

# Deploy shared databases first
kubectl apply -k infra/k8s/shared-services/overlays/local

# Deploy application microservices
kubectl apply -k infra/k8s/apps/overlays/local

# List all running services
kubectl get services --all-namespaces
```

### Deploying to AWS (EKS)

```bash
# Provision EKS cluster via Terraform
cd infra/terraform
terraform init
terraform apply

# Deploy workloads (same Kustomize overlays — create a prod overlay targeting EKS)
kubectl apply -k infra/k8s/shared-services/overlays/local
kubectl apply -k infra/k8s/apps/overlays/local
```

Refer to [infra/README.md](infra/README.md) for full deployment instructions.

---

## Folder Structure

```
.
├── products-cna-microservice/    # Product catalog (Node.js, MongoDB)
├── cart-cna-microservice/        # Shopping cart (Java Spring Boot, Redis)
├── users-cna-microservice/       # User profiles (Python FastAPI, PostgreSQL)
├── search-cna-microservice/      # Search proxy (Node.js, ElasticSearch)
├── store-ui/                     # React frontend (nginx in production)
├── infra/
│   ├── k8s/
│   │   ├── apps/                 # Microservice Kubernetes manifests (Kustomize)
│   │   └── shared-services/      # Database Kubernetes manifests (Kustomize)
│   ├── terraform/                # AWS EKS infrastructure
│   └── performance/              # JMeter load test plans
├── architecture.png              # Architecture diagram
└── app-showcase.png              # UI screenshot
```

---

## Issues & Feedback

Raise an issue on GitHub. Pull requests welcome.