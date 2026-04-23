# Learning Terraform & Kubernetes — From Scratch

一份從零開始、手把手的學習筆記。最終目標：寫一個 FastAPI CRUD + PostgreSQL，一路從 Docker 打包 → 丟進 Kubernetes → 用 Terraform 管理 → 最後推上 AWS。

> 詳細的學習路徑與 checklist 看 [PLAN.md](./PLAN.md)。這份 README 是**實際操作的流水帳**，給第一次上手的人照做就行。

---

## 這份筆記適合誰？

- 沒碰過 K8s / Terraform，但會寫一點 Python 和用過 Docker 的人
- 想要一份「照著做就能跑起來」的教學
- 用 macOS 環境（其他 OS 大致相同，指令可能要微調）

---

## 最終架構（做完長這樣）

```
本機 Mac
├── Docker Desktop      ← 跑容器的引擎
└── minikube            ← 本機的迷你 K8s cluster
    └── namespace: learning
        ├── FastAPI pods   ← 你的 app（2 個副本）
        ├── PostgreSQL     ← DB（StatefulSet + PVC）
        └── Services       ← 對外的連線口
```

底下的設定最後全部用 **Terraform** 管理，而不是手動 `kubectl apply`。

---

## Phase 0：環境準備

### 0.1 前置需求

你需要先有：

- **macOS**（這份筆記用 macOS 示範）
- **Docker 環境**（擇一，提供 `docker` CLI 和 daemon）：
  - **OrbStack**（推薦，輕量快速）— [下載](https://orbstack.dev/)
  - 或 **Docker Desktop** — [下載](https://www.docker.com/products/docker-desktop/)
  - 裝完打開它，確認選單列圖示穩定後
  - 驗證：terminal 跑 `docker ps`，不報錯就 OK
- **Homebrew** — macOS 的套件管理器
  - 驗證：`brew --version`，沒有的話去 [brew.sh](https://brew.sh) 裝

### 0.2 安裝 K8s 相關 CLI 工具

我們需要兩個工具：

| 工具 | 用途 | 比喻 |
|------|------|------|
| **minikube** | 在你 Mac 上跑一個迷你 K8s cluster | 「本機的 K8s 模擬器」 |
| **kubectl** | 跟 K8s cluster 講話的 CLI | 「K8s 的遙控器」 |

安裝：

```bash
brew install minikube kubectl
```

驗證：

```bash
minikube version
kubectl version --client
```

應該各自印出版本號。

### 0.3 啟動 minikube

```bash
minikube start --driver=docker
```

第一次會花幾分鐘（要下載 K8s 的 image）。成功會看到 `Done! kubectl is now configured to use "minikube"`。

驗證 cluster 活著：

```bash
minikube status
kubectl get nodes
```

- `minikube status` → host / kubelet / apiserver 都是 `Running`
- `kubectl get nodes` → 看到一個節點，`STATUS` 是 `Ready`

**常用操作**：

```bash
minikube stop      # 關閉（保留狀態，之後 start 可以繼續）
minikube delete    # 整組砍掉重練
```

---

## 核心概念速查（動手前先讀）

### Docker vs K8s

| | Docker | Kubernetes |
|---|---|---|
| 管什麼 | 單一容器 | 一群容器 |
| 誰重啟掛掉的 | 你自己 | K8s 自動 |
| 要跑 5 個 replica | `docker run` x5 | `replicas: 5` 一行 |
| 多容器互相溝通 | 自己管 IP | Service + DNS |
| 滾動升級 | 手動 | 內建 |

K8s **不取代** Docker — 它底層還是用 Docker 跑容器，只是在上面蓋了一層管理。

### K8s 的三層抽象（由下到上）

```
Container  ← Docker 層級的跑 process
    ↑
   Pod      ← K8s 最小單位，1~N 個 container 共享網路和儲存
    ↑
ReplicaSet ← 確保「永遠有 N 個一樣的 Pod 在跑」
    ↑
Deployment ← 管 ReplicaSet，處理 rolling update / rollback
```

**你日常只寫 Deployment，不直接寫 Pod 和 ReplicaSet。** 它們是 Deployment 自動建出來的。

### Service 為什麼需要

Pod 會死會重生、IP 會變。Service 提供一個**穩定的虛擬 IP + DNS 名字**，自動把流量分給符合 label 的 Pod 們。

```
Client → Service (穩定) → Pod1 / Pod2 / Pod3 (IP 亂變沒差)
```

### minikube 內部的「兩個 Docker」

minikube 跑在你 Mac 的 Docker 裡，但它**內部又有一個自己的 Docker daemon**。所以：

- 你 Mac terminal 的 `docker build` → image 跑在 Mac daemon，minikube **看不到**
- 要讓 minikube 看到 → 先執行 `eval $(minikube docker-env)` 切到 minikube 的 daemon，再 build

這是部署到 minikube 時最常見的坑（Pod 會卡 `ErrImageNeverPull`）。

---

## Phase 1：FastAPI + Docker

> 👉 TODO：補上 app/ 結構說明、Dockerfile 邏輯、build 指令。等目前主線推進到哪就回頭補。

---

## Phase 1.3：部署到 minikube（進行中）

### 3.1 ConfigMap — 把設定抽出來

**為什麼要 ConfigMap？** 如果 `APP_ENV=local` 寫死在 image 裡，換環境就要 rebuild。ConfigMap 讓你「改設定不用動 image」。

**檔案**：[`deployment/k8s/base/api-configmap.yaml`](./deployment/k8s/base/api-configmap.yaml)

**幾個重點**：

- `data:` 底下的值**一定要是 string** — 習慣全部加引號，不然 `true` / 數字會被 YAML 解成 boolean / int，apply 失敗
- Pod 怎麼讀？用 `envFrom.configMapRef`，整包 key-value 變成環境變數
- ConfigMap 改了之後，用 `envFrom` 注入的環境變數**不會自動更新** — 要 `kubectl rollout restart deployment/xxx`

**部署並驗證**：

```bash
kubectl apply -f deployment/k8s/base/namespace.yaml
kubectl apply -f deployment/k8s/base/api-configmap.yaml
kubectl get configmap -n learning
kubectl describe configmap api-config -n learning
```

### 3.2 Deployment — 跑 app

> 👉 TODO：寫完 api-deployment.yaml 補這段。

### 3.3 Service — 對外暴露

> 👉 TODO：寫完 api-service.yaml 補這段。

---

## 進度追蹤

- [x] Phase 0：環境準備
- [x] Phase 1.1：FastAPI app
- [x] Phase 1.2：Dockerize
- [ ] Phase 1.3：部署到 minikube ← **現在在這**
- [ ] Phase 1.4：Terraform 管理 K8s
- [ ] Phase 2：PostgreSQL
- [ ] Phase 3：LocalStack
- [ ] Phase 4：AWS
