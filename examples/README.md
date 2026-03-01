# 🚀 Kubesage – AI Kubernetes Debugger

> 🏆 AI for Bharat Hackathon Submission

An AI-powered Kubernetes debugging CLI that works with both:

- 🖥️ Local clusters (Kind)
- ☁️ AWS EKS clusters

## 📋 Prerequisites

Make sure you have:

- 🐧 Linux (Ubuntu recommended)
- 🐍 Python 3.9+
- ☁️ AWS Account
- 💳 Billing enabled on AWS
- 🧠 Basic knowledge of Kubernetes

## 🔐 Step 1: Setup AWS IAM

1️⃣ Create IAM User

Go to:

```
👉 IAM → Users → Create User
```

Create user:

```
eks-admin
```

Attach policy:

```
AdministratorAccess
```

**⚠️ For production use, avoid AdministratorAccess. Create a scoped policy instead.**

2️⃣ Generate Access Keys

Go to:

```
IAM → Users → eks-admin → Security Credentials
```

Create:

Access Key ID
Secret Access Key

**⚠️ Save them securely.**

## 🛠️ Step 2: Install Required Tools

### ☁️ Install AWS CLI v2

```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
sudo apt install unzip -y
unzip awscliv2.zip
sudo ./aws/install

aws --version
```

### 🔑 Configure AWS Credentials

```bash
aws configure
```

Enter:

- Access Key
- Secret Key
- Region → us-east-1
- Output → json

### 🐳 Install Docker

```bash
sudo apt update
sudo apt install docker.io -y
sudo systemctl enable docker
sudo systemctl start docker
```

Add your user to docker group:

```bash
sudo usermod -aG docker $USER
newgrp docker
```

Verify:

```bash
docker --version
docker ps
```

### ☸️ Install kubectl

```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

kubectl version --client
```

### 🧩 Install eksctl

```bash
ARCH=amd64
PLATFORM=$(uname -s)_$ARCH

curl -sLO "https://github.com/eksctl-io/eksctl/releases/latest/download/eksctl_$PLATFORM.tar.gz"

tar -xzf eksctl_$PLATFORM.tar.gz -C /tmp
sudo install -m 0755 /tmp/eksctl /usr/local/bin
```

Verify:

```bash
eksctl version
```

## ☁️ Step 3: Create EKS Cluster

```bash
eksctl create cluster \
  --name kubesage-demo \
  --region us-east-1 \
  --node-type t2.medium \
  --nodes-min 2 \
  --nodes-max 2
```

⏳ Takes ~10–15 minutes.

## 🔗 Connect kubectl to EKS

```bash
aws eks update-kubeconfig --region us-east-1 --name kubesage-demo
```

Verify:

```bash
kubectl get nodes
```

You should see 2 worker nodes ✅

## 📦 Step 4: Deploy Application

```bash
kubectl apply -f ./k8s/
```

Check:

```bash
kubectl get pods
```

## 🤖 Step 5: Run AI Debugger CLI

Setup Virtual Environment using pip

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

```bash
python cli.py \
  -p <pod_name> \
  --cluster-type eks \
  --cluster-name kubesage-demo \
  --region us-east-1
```

Example:

```bash
python cli.py -p oom-deployment-xxxxx \
  --cluster-type eks \
  --cluster-name kubesage-demo \
  --region us-east-1
```

## 🔍 Step 6: Observe AI Debugging

```bash
kubectl get pods
kubectl describe pod <pod_name>
kubectl logs <pod_name>
```

# 🖥️ (Optional) Run on Local Kubernetes (Kind)

If using Kind:

```bash
kind create cluster
kubectl get nodes
```

Switch context:

```bash
kubectl config use-context kind-kind
```

Run CLI:

```bash
python cli.py -p <pod_name> --cluster-type local
```

# 💰 VERY IMPORTANT: Cleanup (Avoid AWS Bill Shock 😭)

After testing:

```bash
eksctl delete cluster \
  --name kubesage-demo \
  --region us-east-1
```

Also verify:

- EC2 instances deleted
- Load balancers deleted
- EBS volumes deleted
