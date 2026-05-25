# Office Task: Python App + ACR + Kubernetes + GitOps + CronJob

This project completes both office tasks:

1. Develop a Python program and push it to GitHub.
2. Build and push Docker image to Azure Container Registry using GitHub Actions.
3. Create Kubernetes deployment that pulls image from ACR.
4. Test whether pod is running.
5. Implement GitOps using Argo CD.
6. Create Kubernetes CronJob that runs every minute and logs timestamp.

---

## Project Structure

```text
office-k8s-gitops-project/
├── app/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── k8s/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── cronjob.yaml
│   └── kustomization.yaml
├── argocd/
│   └── application.yaml
├── .github/workflows/
│   └── build-push-acr.yml
├── scripts/
│   └── local-test.sh
└── README.md
```

---

# Part 1: Run Python Flask App Locally

Go to the app folder:

```bash
cd app
```

Install requirements:

```bash
pip install -r requirements.txt
```

Run app:

```bash
python app.py
```

Open browser:

```text
http://localhost:5000
```

Health check:

```text
http://localhost:5000/health
```

---

# Part 2: Build Docker Image Locally

From project root:

```bash
docker build -t python-k8s-app:local ./app
```

Run container:

```bash
docker run -p 5000:5000 python-k8s-app:local
```

Test:

```bash
curl http://localhost:5000
curl http://localhost:5000/health
```

---

# Part 3: Create Azure Container Registry

Login to Azure:

```bash
az login
```

Create resource group:

```bash
az group create --name rg-office-k8s --location southeastasia
```

Create ACR:

```bash
az acr create \
  --resource-group rg-office-k8s \
  --name YOUR_ACR_NAME \
  --sku Basic
```

Example ACR name should be globally unique:

```text
neelimaofficeacr
```

Check ACR login server:

```bash
az acr show --name YOUR_ACR_NAME --query loginServer -o tsv
```

Example output:

```text
neelimaofficeacr.azurecr.io
```

---

# Part 4: GitHub Secrets Required

In GitHub repo, go to:

```text
Settings → Secrets and variables → Actions → New repository secret
```

Add these secrets:

```text
ACR_NAME              = your ACR name only, example: neelimaofficeacr
ACR_LOGIN_SERVER      = your login server, example: neelimaofficeacr.azurecr.io
AZURE_CREDENTIALS     = Azure service principal JSON
```

Create Azure credentials for GitHub Actions:

```bash
az ad sp create-for-rbac \
  --name github-acr-push-sp \
  --role Contributor \
  --scopes /subscriptions/<SUBSCRIPTION_ID>/resourceGroups/rg-office-k8s \
  --sdk-auth
```

Copy the full JSON output and paste it into GitHub secret:

```text
AZURE_CREDENTIALS
```

---

# Part 5: GitHub Actions Build and Push

Workflow file:

```text
.github/workflows/build-push-acr.yml
```

When you push to main branch, GitHub Actions will:

1. Login to Azure.
2. Login to ACR.
3. Build Docker image.
4. Tag image with GitHub commit SHA and latest.
5. Push image to ACR.

Push code:

```bash
git add .
git commit -m "Initial office k8s gitops project"
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/office-k8s-gitops-project.git
git push -u origin main
```

---

# Part 6: Update Kubernetes Image

Open:

```text
k8s/deployment.yaml
```

Replace:

```text
REPLACE_ACR_LOGIN_SERVER/python-k8s-app:latest
```

With your real ACR image:

```text
neelimaofficeacr.azurecr.io/python-k8s-app:latest
```

Then commit and push:

```bash
git add k8s/deployment.yaml
git commit -m "Update ACR image path"
git push
```

---

# Part 7: Create AKS Cluster

Create AKS:

```bash
az aks create \
  --resource-group rg-office-k8s \
  --name office-aks-cluster \
  --node-count 1 \
  --enable-managed-identity \
  --attach-acr YOUR_ACR_NAME \
  --generate-ssh-keys
```

Get AKS credentials:

```bash
az aks get-credentials \
  --resource-group rg-office-k8s \
  --name office-aks-cluster
```

Check cluster:

```bash
kubectl get nodes
```

---

# Part 8: Deploy App to Kubernetes Manually

Apply manifests:

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

Check deployment:

```bash
kubectl get deployment
kubectl get pods
kubectl get service
```

Check pod logs:

```bash
kubectl logs <pod-name>
```

Test using port-forward:

```bash
kubectl port-forward service/python-k8s-service 8080:80
```

Open:

```text
http://localhost:8080
```

---

# Part 9: If ImagePullBackOff Error Comes

Check pod:

```bash
kubectl describe pod <pod-name>
```

Common reason: AKS does not have permission to pull from ACR.

Fix:

```bash
az aks update \
  --resource-group rg-office-k8s \
  --name office-aks-cluster \
  --attach-acr YOUR_ACR_NAME
```

Restart deployment:

```bash
kubectl rollout restart deployment python-k8s-app
```

---

# Part 10: GitOps Using Argo CD

Install Argo CD:

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

Check Argo CD pods:

```bash
kubectl get pods -n argocd
```

Update this file:

```text
argocd/application.yaml
```

Replace:

```text
https://github.com/YOUR_GITHUB_USERNAME/office-k8s-gitops-project.git
```

With your actual GitHub repository URL.

Apply Argo CD application:

```bash
kubectl apply -f argocd/application.yaml
```

Check application:

```bash
kubectl get applications -n argocd
kubectl get pods
```

Access Argo CD UI:

```bash
kubectl port-forward svc/argocd-server -n argocd 8081:443
```

Open:

```text
https://localhost:8081
```

Username:

```text
admin
```

Password:

```bash
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 -d
```

---

# Part 11: CronJob Every Minute

CronJob file:

```text
k8s/cronjob.yaml
```

Apply:

```bash
kubectl apply -f k8s/cronjob.yaml
```

Check CronJob:

```bash
kubectl get cronjob
```

After one minute, check jobs:

```bash
kubectl get jobs
```

Check pods created by CronJob:

```bash
kubectl get pods
```

Check logs:

```bash
kubectl logs <cronjob-pod-name>
```

Expected output:

```text
CronJob running at: 2026-05-25T...
```

---

# Interview Explanation

You can explain like this:

```text
I developed a lightweight Python Flask application with health check endpoint. 
I containerized the application using Docker and configured GitHub Actions 
to build the image and push it to Azure Container Registry. 
Then I created Kubernetes Deployment and Service YAML files to deploy the image 
from ACR into AKS. I verified the deployment using kubectl get pods, 
kubectl describe pod, kubectl logs, and port-forward testing.

For GitOps, I implemented Argo CD. Argo CD continuously watches the GitHub repository 
and syncs the Kubernetes manifests from the k8s folder to the cluster. 
If there is any drift in the cluster, Argo CD self-heals it based on Git state.

For the second task, I created a Kubernetes CronJob with schedule * * * * * 
which runs every minute and prints the current timestamp into pod logs.
```

---

# Useful Commands Summary

```bash
kubectl get nodes
kubectl get pods
kubectl get deployment
kubectl get service
kubectl describe pod <pod-name>
kubectl logs <pod-name>
kubectl rollout restart deployment python-k8s-app
kubectl delete pod <pod-name>
kubectl get cronjob
kubectl get jobs
kubectl get applications -n argocd
```
