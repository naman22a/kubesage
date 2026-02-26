# KubeSage

> AI-Powered Kubernetes Debugging Agent

## 🤔 Problem Statement

Debugging Kubernetes clusters is complex, time-consuming, and often reactive. Developers and DevOps engineers must manually inspect:

- Pod logs
- Events
- YAML manifests
- Resource metrics

Root causes are buried inside noisy logs, and Mean Time To Resolution (MTTR) can be high.
This challenge becomes even more critical in production EKS environments where rapid incident triage is essential.

## 💡 Solution Overview

**KubeSage** is an AI-powered Kubernetes debugging agent that integrates with Amazon Bedrock to perform automated root cause analysis of cluster failures.

It combines:

- Real-time Kubernetes inspection
- Structured log extraction
- GenAI-powered reasoning
- Risk classification and remediation suggestions

All from a lightweight CLI interface.

Instead of manually scanning logs, users can run:

```bash
python cli.py --pod crashloop-app
```

And receive:

- 🔍 Root Cause
- ⚠ Risk Level
- 💡 Suggested Fix
- 📊 Confidence Score

## 🧠 How It Works (Architecture)

KubeSage follows this flow:

```
Kubernetes Cluster (EKS or local)
     ↓
Kubernetes Logs
     ↓
KubeSage Context Builder
     ↓
Strands Agent
     ↓
Amazon Bedrock (Claude 3.5 Sonnet)
     ↓
Structured Root Cause Analysis
     ↓
CLI Output + Optional Storage
```

## AWS Services Used

- Amazon Bedrock – GenAI reasoning for log analysis and remediation generation
- Amazon EKS (optional deployment target) – Kubernetes environment
- AWS Lambda (optional extension) – Event-driven debugging automation
- Amazon DynamoDB (optional extension) – Structured incident storage
- Amazon S3 (optional extension) – Log archival and debugging reports

🐈 Core Features

- AI-driven root cause analysis for:
    - CrashLoopBackOff
    - OOMKilled
    - ImagePullBackOff
- Structured, type-safe debugging output
- Risk-level classification (LOW / MEDIUM / HIGH)
- Confidence scoring
- Clean, rich CLI interface
- Modular and extensible architecture
- AWS Bedrock integration via strands

## 🎯 Impact

KubeSage reduces:

- Manual log inspection time
- Context-switching between tools
- Mean Time To Resolution (MTTR)

By transforming raw Kubernetes failures into actionable insights using GenAI.

## ⚙️ Tech Stack

### Core

- Python 3.10
- Typer – CLI framework
- Rich – Styled terminal outputs
- Pydantic – Structured result modeling
- Kubernetes Python Client – Cluster interaction

### GenAI

- Amazon Bedrock – LLM inference
- Claude 3.5 Sonnet (primary reasoning)
- Claude 3 Haiku (lightweight classification)

## AWS SDK

- strands – Bedrock invocation

## Installation

### 🐍 Using Conda

```bash
git clone https://github.com/naman22a/kubesage.git
cd kubesage
conda env create -f environment.yml
conda activate kubesage
```

### 🐍 Using pip

```bash
git clone https://github.com/naman22a/kubesage.git
cd kubesage
pip install -r requirements.txt
```

## 🔐 AWS Setup (Bedrock)

1. Enable Amazon Bedrock in your AWS region.
2. Ensure model access is granted (Claude model).
3. Configure credentials:

```bash
aws configure
```

4. Set environment variables (if needed):

```bash
export AWS_REGION=us-east-1
```

## 📁 Code Structure

```
kubesage/
├── k8s/                  # K8s manifest files for testing
├── src/                  # Main source code
│   ├── agent.py
│   ├── constants.py
│   ├── custom_types.py
│   ├── fns.py
│   └── k8s.py
├── cli.py                # CLI entry point
├── environment.yml       # Conda environment
├── requirements.txt      # Python dependencies
```

## 🗒️ LICENSE

KubeSage is [GPL V3](./LICENSE)
