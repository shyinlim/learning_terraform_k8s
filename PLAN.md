# Learning Terraform & Kubernetes — Study Guide

> Goal: Build a FastAPI CRUD API + PostgreSQL, progressively learn Docker → K8s → Terraform → AWS

## Tech Stack

| Layer | Tool | Purpose |
|-------|------|---------|
| App | Python FastAPI + SQLAlchemy | CRUD API |
| DB | SQLite (Phase 1) → PostgreSQL (Phase 2+) | Data storage |
| Container | Docker | Package the app |
| Orchestration | Kubernetes (minikube) | Container orchestration |
| IaC | Terraform | Infrastructure as Code |
| Cloud | LocalStack → AWS | Cloud deployment |

## Directory Structure

```
learning_terraform_k8s/
├── app/                        # FastAPI application
│   ├── main.py                 # Entry point
│   ├── models.py               # SQLAlchemy models
│   ├── schemas.py              # Pydantic schemas
│   ├── database.py             # DB connection config
│   ├── crud.py                 # CRUD operations
│   ├── requirements.txt
│   └── Dockerfile
├── k8s/base/                   # K8s manifests
├── terraform/local/            # Terraform (minikube)
├── terraform/localstack/       # Terraform (LocalStack, simulated AWS)
├── terraform/aws/              # Terraform (real AWS)
└── docker-compose.yaml         # Local dev
```

---

## Phase 1: FastAPI + Docker + minikube

### 1.1 — FastAPI CRUD App

**Goal**: Build an Items CRUD API using SQLite (zero setup)

**Checklist**:
- [ ] `app/requirements.txt`
- [ ] `app/database.py` — engine, SessionLocal, Base, `get_db()` generator
- [ ] `app/models.py` — Item table (id, name, description, created_at, updated_at)
- [ ] `app/schemas.py` — ItemCreate, ItemUpdate, ItemResponse
- [ ] `app/crud.py` — create_item, get_items, get_item, update_item, delete_item
- [ ] `app/main.py` — FastAPI app with 6 endpoints
- [ ] Verify: `uvicorn main:app --reload` → Swagger UI works at `/docs`
- [ ] Verify: All CRUD operations work (create, read, update, delete)

**Endpoints to implement**:
- `GET /health` — health check
- `POST /items` — create item
- `GET /items` — list items
- `GET /items/{id}` — get item
- `PUT /items/{id}` — update item
- `DELETE /items/{id}` — delete item

**Key Concepts**:

| Concept | Description |
|---------|-------------|
| FastAPI | High-performance Python web framework, auto-generates OpenAPI docs |
| Pydantic | Data validation — defines request/response schemas |
| SQLAlchemy | ORM — maps Python classes to DB tables |
| Dependency Injection | FastAPI's `Depends(get_db)` manages DB session lifecycle |

**Hints**:
- `database.py` — Create engine, SessionLocal, Base; write a `get_db()` generator
- `models.py` — Inherit from Base, define Item table
- `schemas.py` — Use `model_config = {"from_attributes": True}` for ORM compatibility
- `crud.py` — Each function takes `db: Session` as first arg
- `main.py` — Call `Base.metadata.create_all()` to auto-create tables at startup

**Verify**:
```bash
cd app
pip install -r requirements.txt
uvicorn main:app --reload
# Open http://localhost:8000/docs for Swagger UI
```

**Notes**:
<!-- What I learned, what I got stuck on -->


---

### 1.2 — Dockerize

**Goal**: Package the app into a Docker image

**Checklist**:
- [ ] `app/Dockerfile` — multi-stage build
- [ ] `.dockerignore`
- [ ] Verify: `docker build` succeeds
- [ ] Verify: `docker run` → `curl /health` returns OK

**Key Concepts**:

| Concept | Description |
|---------|-------------|
| Multi-stage build | Stage 1 installs deps, Stage 2 copies only the result — smaller image |
| Image layers | Each instruction creates a layer; order affects cache efficiency |
| `.dockerignore` | Excludes unnecessary files, reduces build context |

**Dockerfile structure hint**:
```
Stage 1 (builder): python:3.12-slim → install requirements
Stage 2 (runtime): python:3.12-slim → copy packages + code → CMD uvicorn
```

**Verify**:
```bash
docker build -t fastapi-crud:v1 ./app
docker run -p 8000:8000 fastapi-crud:v1
curl http://localhost:8000/health
```

**Notes**:
<!-- What I learned, what I got stuck on -->


---

### 1.3 — Deploy to minikube

**Goal**: Run the app in minikube using K8s manifests

**Checklist**:
- [ ] `k8s/base/namespace.yaml`
- [ ] `k8s/base/api-configmap.yaml`
- [ ] `k8s/base/api-deployment.yaml` — with replicas, resource limits, probes
- [ ] `k8s/base/api-service.yaml` — NodePort
- [ ] Verify: Pods are running (`kubectl get pods -n learning`)
- [ ] Verify: API is accessible via `minikube service`

**Key Concepts**:

| Concept | Description |
|---------|-------------|
| Namespace | Logical isolation, like a folder |
| Pod | Smallest deployable unit in K8s, wraps one or more containers |
| Deployment | Manages replica count, rolling updates |
| Service (NodePort) | Exposes Pods externally; NodePort opens a port on the node |
| ConfigMap | Stores non-sensitive config (e.g. DATABASE_URL) |
| Readiness Probe | Is the Pod ready to receive traffic? |
| Liveness Probe | Is the Pod still alive? Restart if not |

**Deployment YAML key points**:
- `replicas`: how many copies
- `imagePullPolicy: Never` — use local image (minikube only)
- `envFrom.configMapRef` — inject env vars from ConfigMap
- `resources.requests/limits` — CPU and memory constraints
- `readinessProbe` / `livenessProbe` — both hit `/health`

**Common commands**:
```bash
minikube start
eval $(minikube docker-env)     # Point docker to minikube's Docker daemon
docker build -t fastapi-crud:v1 ./app

kubectl apply -f k8s/base/namespace.yaml
kubectl apply -f k8s/base/
kubectl get pods -n learning
kubectl logs -n learning <pod-name>
minikube service fastapi-crud -n learning   # Open browser to API
```

**Notes**:
<!-- What I learned, what I got stuck on -->


---

### 1.4 — Terraform for Local K8s

**Goal**: Replace `kubectl apply` with Terraform — experience IaC

**Checklist**:
- [ ] `terraform/local/variables.tf` — kube_context, namespace, app_image, replicas, node_port, database_url
- [ ] `terraform/local/main.tf` — kubernetes provider + namespace + configmap + deployment + service
- [ ] `terraform/local/outputs.tf` — namespace, node_port, app_url
- [ ] Verify: `terraform init` succeeds
- [ ] Verify: `terraform plan` shows expected resources
- [ ] Verify: `terraform apply` creates everything in minikube
- [ ] Verify: `terraform destroy` cleans up

**Key Concepts**:

| Concept | Description |
|---------|-------------|
| Provider | Terraform plugin that talks to a platform (`hashicorp/kubernetes` here) |
| Resource | Something you want to create (e.g. `kubernetes_deployment`) |
| State | Terraform's record of "what exists now", stored in `terraform.tfstate` |
| Plan | `terraform plan` previews changes without applying |
| Variables | `variable` blocks define parameters for reuse |
| Outputs | Print useful info after apply (e.g. NodePort) |

**Terraform workflow**:
```bash
cd terraform/local
terraform init      # Download providers
terraform plan      # Preview what will happen
terraform apply     # Execute changes
terraform destroy   # Tear down all resources
```

**main.tf structure hint**:
```
terraform {} block  — set required_providers
provider "kubernetes" {} — point to ~/.kube/config + minikube context
resource "kubernetes_namespace" — create namespace
resource "kubernetes_config_map" — create configmap
resource "kubernetes_deployment" — create deployment (mirrors the YAML)
resource "kubernetes_service" — create service
```

**Notes**:
<!-- What I learned, what I got stuck on -->


---

## Phase 2: PostgreSQL (Stateful Workload)

### 2.1 — PostgreSQL in K8s

**Goal**: Run PostgreSQL in K8s, learn stateful workloads

**Checklist**:
- [ ] `k8s/base/pg-secret.yaml` — POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
- [ ] `k8s/base/pg-pvc.yaml` — 1Gi ReadWriteOnce
- [ ] `k8s/base/pg-statefulset.yaml` — postgres:16-alpine, mount PVC, readiness probe
- [ ] `k8s/base/pg-service.yaml` — ClusterIP on port 5432
- [ ] Verify: `kubectl get statefulset -n learning` shows postgres
- [ ] Verify: `kubectl get pvc -n learning` shows Bound

**Key Concepts**:

| Concept | Why it matters |
|---------|---------------|
| StatefulSet vs Deployment | StatefulSet guarantees stable Pod names (postgres-0), ordered startup, pairs with PVC |
| PersistentVolumeClaim (PVC) | Requests persistent storage from K8s — data survives Pod restarts |
| Secret | Stores sensitive data (DB password), base64 encoded, more protected than ConfigMap |
| ClusterIP Service | Only reachable inside the cluster — for API Pods to reach DB |

**Think about it**: Why use StatefulSet instead of Deployment for a database?
> Hint: What happens to the Pod name after deletion and recreation? Is the volume still there?

**Notes**:
<!-- What I learned, what I got stuck on -->


---

### 2.2 — Update App to Use Environment Variables

**Goal**: Read DATABASE_URL from env vars, don't hardcode it

**Checklist**:
- [ ] `app/database.py` — use `os.getenv("DATABASE_URL", "sqlite:///./items.db")`
- [ ] `app/requirements.txt` — add `psycopg2-binary`
- [ ] Update `k8s/base/api-configmap.yaml` — change to PostgreSQL connection string
- [ ] Verify: App still works locally with SQLite (default fallback)
- [ ] Verify: App connects to PostgreSQL in K8s

**Key concept**: 12-Factor App, Factor III — Store config in environment variables

**Notes**:
<!-- What I learned, what I got stuck on -->


---

### 2.3 — docker-compose

**Goal**: Run API + DB together locally with docker-compose

**Checklist**:
- [ ] `docker-compose.yaml` — two services: api + db
- [ ] db has healthcheck (`pg_isready`)
- [ ] api has `depends_on: condition: service_healthy`
- [ ] Verify: `docker-compose up` → API works at localhost:8000
- [ ] Verify: Data persists in the volume

**Verify**:
```bash
docker-compose up
curl http://localhost:8000/items
docker-compose down -v   # -v removes volumes
```

**Notes**:
<!-- What I learned, what I got stuck on -->


---

### 2.4 — Terraform Manages PostgreSQL Resources

**Goal**: Manage PostgreSQL K8s resources via Terraform

**Checklist**:
- [ ] Add `kubernetes_secret` to main.tf
- [ ] Add `kubernetes_persistent_volume_claim` to main.tf
- [ ] Add `kubernetes_stateful_set` to main.tf
- [ ] Add `kubernetes_service` (postgres) to main.tf
- [ ] Update variables.tf — pg_user, pg_password, pg_database
- [ ] Update outputs.tf — postgres_service
- [ ] Verify: `terraform apply` creates all resources
- [ ] Verify: Data survives `kubectl delete pod postgres-0 -n learning`

**Verify**:
```bash
terraform apply
kubectl get statefulset -n learning
kubectl get pvc -n learning
# Delete Pod to see if data survives
kubectl delete pod postgres-0 -n learning
```

**Notes**:
<!-- What I learned, what I got stuck on -->


---

## Phase 3: LocalStack (Simulated AWS, Zero Cost)

### 3.1 — LocalStack Setup

**Goal**: Simulate AWS services locally with LocalStack

**Checklist**:
- [ ] Start LocalStack container
- [ ] `terraform/localstack/main.tf` — AWS provider pointing to localhost:4566
- [ ] `terraform/localstack/variables.tf`
- [ ] Verify: `terraform init` succeeds with LocalStack endpoint

**Key Concepts**:

| Concept | Description |
|---------|-------------|
| LocalStack | Simulates AWS APIs locally; free tier supports S3, EC2, VPC, etc. |
| AWS Provider | Terraform's AWS plugin — use `endpoints` to point to LocalStack |
| `skip_credentials_validation` | Skip real AWS auth, needed for LocalStack |

```bash
docker run -d -p 4566:4566 localstack/localstack
```

**Notes**:
<!-- What I learned, what I got stuck on -->


---

### 3.2 — Simulated AWS Resources

**Goal**: Practice creating AWS resources with Terraform (zero cost)

**Checklist**:
- [ ] VPC with DNS support
- [ ] Public subnets (2) with Internet Gateway
- [ ] Private subnets (2)
- [ ] Route Table + associations
- [ ] Security Group (ports: 22, 80, 8000)
- [ ] S3 Bucket
- [ ] ECR Repository
- [ ] Verify: `aws --endpoint-url=http://localhost:4566 ec2 describe-vpcs`
- [ ] Verify: `aws --endpoint-url=http://localhost:4566 s3 ls`

**Key Concepts**:

| Concept | Description |
|---------|-------------|
| VPC | Virtual Private Cloud — your private network in AWS |
| Subnet | Sub-networks within a VPC; public = has Internet Gateway, private = doesn't |
| Security Group | Firewall rules controlling inbound/outbound traffic |
| Internet Gateway | Allows public subnet resources to reach the internet |
| Route Table | Determines how packets are routed |

**Verify**:
```bash
cd terraform/localstack && terraform init && terraform apply
aws --endpoint-url=http://localhost:4566 s3 ls
aws --endpoint-url=http://localhost:4566 ec2 describe-vpcs
```

**Notes**:
<!-- What I learned, what I got stuck on -->


---

### 3.3 — Remote State

**Goal**: Store terraform.tfstate in S3, learn team collaboration patterns

**Checklist**:
- [ ] Configure `backend "s3"` in terraform block
- [ ] Point backend to LocalStack endpoint
- [ ] Verify: `terraform init` migrates state to S3
- [ ] Understand state locking concept (DynamoDB)

**Key Concepts**:

| Concept | Description |
|---------|-------------|
| Remote State | Store tfstate remotely (S3) for team sharing |
| State Locking | Use DynamoDB to lock state, prevent concurrent applies |
| Backend | Configure `backend "s3"` in the `terraform {}` block |

**Notes**:
<!-- What I learned, what I got stuck on -->


---

## Phase 4: Real AWS (Optional, Watch Your Costs!)

### 4.1 — AWS Account Setup

**Checklist**:
- [ ] Create AWS account (Free Tier)
- [ ] Create IAM user + programmatic access
- [ ] Run `aws configure`
- [ ] Verify: `aws sts get-caller-identity` works

**Notes**:
<!-- What I learned, what I got stuck on -->


---

### 4.2 — Terraform Modules

**Goal**: Create reusable Terraform modules for AWS infrastructure

**Checklist**:
- [ ] `terraform/aws/modules/vpc/` — VPC + subnets + IGW
- [ ] `terraform/aws/modules/ec2/` — EC2 t3.micro instance
- [ ] `terraform/aws/modules/k3s/` — k3s installation on EC2
- [ ] `terraform/aws/main.tf` — compose modules together
- [ ] `terraform/aws/variables.tf`
- [ ] `terraform/aws/outputs.tf` — EC2 public IP
- [ ] Verify: `terraform plan` shows all resources

**Key Concepts**:

| Concept | Description |
|---------|-------------|
| Module | Reusable Terraform code package with its own variables/outputs |
| EC2 (t3.micro) | Free Tier virtual machine |
| k3s | Lightweight K8s, suitable for single-node setups |

**Notes**:
<!-- What I learned, what I got stuck on -->


---

### 4.3 — Deploy to Cloud

**Checklist**:
- [ ] Push Docker image to ECR (or Docker Hub)
- [ ] Apply K8s manifests to k3s on EC2
- [ ] Expose API via NodePort + EC2 public IP
- [ ] Verify: `curl http://<ec2-ip>:<port>/health` works
- [ ] Verify: CRUD operations work end-to-end

**Notes**:
<!-- What I learned, what I got stuck on -->


---

### 4.4 — DESTROY When Done

**Checklist**:
- [ ] `terraform destroy -auto-approve`
- [ ] Verify: AWS console shows no running resources
- [ ] Double-check: No unexpected charges

```bash
cd terraform/aws && terraform destroy -auto-approve
```

---

## Cheat Sheet

### Docker
```bash
docker build -t <name>:<tag> <path>
docker run -p <host>:<container> <image>
docker ps                    # List running containers
docker images                # List images
docker logs <container>
```

### kubectl
```bash
kubectl get pods -n <namespace>
kubectl get svc -n <namespace>
kubectl describe pod <name> -n <namespace>
kubectl logs <pod> -n <namespace>
kubectl exec -it <pod> -n <namespace> -- /bin/sh
kubectl delete pod <pod> -n <namespace>
kubectl apply -f <file.yaml>
```

### Terraform
```bash
terraform init       # Initialize, download providers
terraform plan       # Preview changes
terraform apply      # Execute (prompts yes/no)
terraform destroy    # Tear down all resources
terraform fmt        # Format .tf files
terraform validate   # Syntax check
terraform state list # List managed resources
```

---

## Skills Learned per Phase

| Phase | Skills |
|-------|--------|
| 1 | REST API, Docker, K8s Deployment/Service/Probe, Terraform basics |
| 2 | StatefulSet, PV/PVC, Secrets, 12-factor app, docker-compose |
| 3 | AWS VPC/S3, Terraform remote state, state locking |
| 4 | Terraform modules, AWS networking, ECR, cost management |
