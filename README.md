# ☸️ KubeSage

> AI-Powered Kubernetes Debugging Agent

KubeSage is an AI-driven Kubernetes debugging assistant that automatically analyzes failing pods and identifies root causes using Amazon Bedrock LLMs.

Instead of manually digging through logs, events, and YAML manifests, KubeSage performs automated root cause analysis and provides actionable remediation suggestions directly from your terminal.

See [examples/README.md](./examples/README.md)

## 🚀 Features

### ✨ AI-powered root cause analysis

Detects common Kubernetes failures such as:

- 🔁 CrashLoopBackOff
- 💥 OOMKilled
- 📦 ImagePullBackOff
- ⚙️ Misconfigured resources
- 📉 Resource starvation

### 🧠 GenAI reasoning

Powered by Amazon Bedrock using:

- Claude 3 Haiku – fast classification

### 📊 Structured debugging results

KubeSage provides:

- 🔍 Root cause
- ⚠ Risk level
- 💡 Suggested fix
- 📈 Confidence score

### 🗄️ Incident History with DynamoDB

Every analysis is automatically persisted to Amazon DynamoDB:

- Stores pod name, namespace, risk level, root cause, and timestamp
- Query past incidents by pod name or risk severity
- Enables post-mortem analysis and trend detection
- Full incident record retained for audit and compliance

### 🔔 Intelligent Alerting with Amazon SNS

KubeSage automatically notifies your team on critical failures:

- Real-time email alerts triggered for **HIGH** risk incidents
- Incident summary with root cause and suggested fix delivered to inbox
- No manual monitoring required — KubeSage alerts you before you notice
- Extensible to SMS, Slack, and PagerDuty via SNS subscriptions

### 🖥️ Developer-friendly CLI

```bash
python cli.py --pod oom-deployment-86b87cc56-45flm
```

Example output:

![image](./assets/1.png)
![image](./assets/2.png)
![image](./assets/3.png)
![image](./assets/4.png)

## 🏗 Architecture

Below is the high-level architecture of KubeSage.

![KubeSage](./assets/architecture.png)

## ☁️ AWS Services Used

KubeSage integrates with several AWS services:

| Service                               | Purpose                                                |
| ------------------------------------- | ------------------------------------------------------ |
| **Amazon Bedrock**                    | LLM inference for debugging reasoning (Claude 3 Haiku) |
| **Amazon Elastic Kubernetes Service** | Managed Kubernetes cluster                             |
| **Amazon CloudWatch**                 | Pod logs and container metrics collection              |
| **Amazon DynamoDB**                   | Persistent incident storage and history querying       |
| **Amazon SNS**                        | Real-time email/SMS alerts for HIGH risk incidents     |
| **AWS Lambda** _(optional)_           | Event-driven autonomous debugging                      |
| **Amazon S3** _(optional)_            | Long-term log archival                                 |

## ⚙️ Tech Stack

### Core

- Python 3.10
- Typer (CLI framework)
- Rich (terminal UI)
- Pydantic (structured outputs)
- Kubernetes Python Client

### GenAI

- Amazon Bedrock
- Claude models from Anthropic

### AWS SDK

- strands – Bedrock invocation
- boto3 – DynamoDB and SNS integration

## 🎯 Impact

KubeSage helps engineers:

- ⏱ Reduce Mean Time To Resolution (MTTR) from 30+ minutes to under 1 minute
- 🔍 Automatically identify failure causes without manual log digging
- 🧠 Democratize SRE expertise — junior engineers debug like seniors
- 🔔 Get alerted on critical failures before manual discovery
- 📚 Build an incident knowledge base for post-mortems and trend analysis
- ⚡ Respond faster to production incidents

## ⬇️ Installation

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

## 📖 Full Setup Guide

For complete setup instructions including:

- AWS IAM configuration
- AWS CLI installation
- Docker installation
- kubectl installation
- eksctl installation
- Creating an EKS cluster
- Running test workloads

See [examples/README.md](./examples/README.md)

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

## 🗄️ AWS Setup (DynamoDB)

1. Create a DynamoDB table named `kubesage-analysis` with `pod_name` as the partition key.
2. Ensure your IAM role has `dynamodb:PutItem` and `dynamodb:Query` permissions.
3. Set environment variable:

```bash
export DYNAMODB_TABLE=kubesage-analysis
```

## 🔔 AWS Setup (SNS Alerts)

1. Create an SNS topic named `kubesage-alerts` in your AWS region.
2. Subscribe your email or phone number to the topic.
3. Confirm the subscription from your inbox.
4. Set environment variable:

```bash
export SNS_TOPIC_ARN=arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:kubesage-alerts
```

> Alerts are automatically triggered when `risk_assessment` is **HIGH**.

## 📁 Code Structure

```
kubesage/
├── k8s/                  # K8s manifest files for testing
├── src/                  # Main source code
│   ├── agent.py
│   ├── aws_utils.py
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
