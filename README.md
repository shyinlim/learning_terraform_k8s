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
- **Docker Desktop** — [下載](https://www.docker.com/products/docker-desktop/)
  - 裝完打開它，等鯨魚 🐳 圖示在選單列出現且穩定
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

## Phase 1：FastAPI + Docker

> 👉 TODO：補上 app/ 結構說明、Dockerfile 邏輯、build 指令。等目前主線推進到哪就回頭補。

---

## Phase 1.3：部署到 minikube（進行中）

> 👉 TODO：ConfigMap / Deployment / Service yaml 寫完後補這段。

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
