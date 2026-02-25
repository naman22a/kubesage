# KubeSage

> Kubernetes Debugging Agent

## 🤔 Problem Statement

Managing and debugging Kubernetes clusters can be challenging, especially for developers and DevOps engineers in resource-constrained environments. Errors are often hard to trace, and cluster insights are scattered across multiple tools. **Kube Sage** addresses this by providing an intelligent CLI-based debugging agent that simplifies cluster inspection and troubleshooting.

## 💡 Solution Overview

**Kube Sage** is a lightweight, type-safe CLI tool that helps users:

- Inspect and debug Kubernetes clusters quickly.
- Analyze resources and detect potential issues.
- Automate common debugging workflows with reusable functions.
- Use custom risk and action types for safe cluster operations.

Built to be simple yet powerful, Kube Sage allows developers to interact with Kubernetes without leaving the terminal, making debugging faster and more reliable.

## 🐈 Features

- Modular, maintainable codebase.
- Type-safe operations using `custom_types.py`.
- Predefined functions for cluster inspection and task automation.
- Easy-to-use CLI commands.
- Ready for rapid deployment using Conda or pip.

## ⚙️ Tech Stack

- **Programming Language**: Python 3.10
- **CLI Framework**: Typer – for building an interactive and user-friendly command-line interface
- **Kubernetes Interaction**: `kubernetes` Python client – list pods, fetch logs, and run cluster operations
- **AI & Automation**: Custom `agent` module + Strands AI Agent for analyzing logs and recommending debugging actions
- **Logging & Output**: Rich – for styled terminal outputs, panels, tables, progress bars, syntax highlighting
- **Process Management**: `subprocess` + `shlex` – execute `kubectl` commands safely from Python
- **Data Modeling**: Pydantic (`K8sAgentResult`, custom types) – enforce type safety and structured outputs
- **Environment Management**: Conda (`environment.yml`) for reproducible development

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
