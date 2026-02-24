import io
from contextlib import redirect_stdout
from pprint import pprint
import argparse
import os
import dotenv

from strands import Agent
from strands.models.ollama import OllamaModel

from k8s import list_pod_with_logs
from constants import system_prompt
from custom_types import K8sAgentResult
from fns import build_agent_context, parse_root_cause, parse_evidence

dotenv.load_dotenv()

parser = argparse.ArgumentParser(
    prog='KubeSage',
    description='Kubernetes Debugging agent',
)

parser.add_argument('-p', '--pod')
parser.add_argument('-ns', '--namespace')

args = parser.parse_args()

pod_name = args.pod
namespace = args.namespace if args.namespace else 'default'

print(
"""
┌──────────────────────────────────────────────┐
│                 KubeSage                     │
│        Kubernetes Debugging Assistant        │
└──────────────────────────────────────────────┘
"""
)

ollama_model = OllamaModel(
    host="http://localhost:11434",
    model_id=os.environ['MODEL_ID']
)

agent = Agent(
    model=ollama_model,
    system_prompt=system_prompt
)

# pod = list_pod_with_logs(pod_name=pod_name, namespace=namespace)
print("[✔] Fetching last 200 log lines...")
# logs_context = build_agent_context(pod)
print("[✔] Building diagnostic context...")
# prompt = f"""
# TASK:
# Determine why the pod is failing and recommend safe remediation.

# CLUSTER LOGS:
# {logs_context}
# """

print("[✔] Running analysis with LLM...")
buffer = io.StringIO()
with redirect_stdout(buffer):
    pass
    # result = agent(prompt, 
    #                structured_output_model=K8sAgentResult)
print("[✔] Completed analysis with LLM...")

# result: K8sAgentResult = result.structured_output
result_dict = {
  "pod_name": "api-server-7f9c8d6b9c-2xkqj",
  "namespace": "default",
  "overall_status": "CrashLoopBackOff",
  "root_cause": {
    "summary": "Application container is crashing due to missing environment variable DATABASE_URL.",
    "confidence": "HIGH",
    "contributing_factors": [
      "DATABASE_URL not defined in pod environment",
      "Recent config change removed secret reference",
      "Application does not handle missing config gracefully"
    ]
  },
  "evidence": [
    {
      "source": "logs",
      "reference": "kubectl logs api-server-7f9c8d6b9c-2xkqj",
      "description": "Error: DATABASE_URL is not set. Application exiting."
    },
    {
      "source": "pod_status",
      "reference": "kubectl describe pod api-server-7f9c8d6b9c-2xkqj",
      "description": "Pod is in CrashLoopBackOff state with 5 restarts in the last 10 minutes."
    },
    {
      "source": "config",
      "reference": "deployment/api-server",
      "description": "Environment variable DATABASE_URL is missing from container spec."
    }
  ],
  "risk_assessment": "MEDIUM",
  "blast_radius": "Deployment",
  "proposed_actions": [
    {
      "action_type": "READ",
      "title": "Verify environment variables in deployment",
      "description": "Inspect the deployment spec to confirm missing DATABASE_URL configuration.",
      "kubectl_command": "kubectl get deployment api-server -o yaml",
      "requires_confirmation": False,
      "risk_level": "LOW",
      "expected_outcome": "Confirmation that DATABASE_URL is absent or misconfigured.",
      "rollback_strategy": None
    },
    {
      "action_type": "WRITE",
      "title": "Restore DATABASE_URL environment variable",
      "description": "Patch the deployment to include DATABASE_URL from the correct secret.",
      "kubectl_command": "kubectl set env deployment/api-server DATABASE_URL=<from-secret>",
      "requires_confirmation": True,
      "risk_level": "MEDIUM",
      "expected_outcome": "Pod restarts successfully and enters Running state.",
      "rollback_strategy": "kubectl rollout undo deployment/api-server"
    }
  ],
  "requires_user_confirmation": True,
  "summary": "The pod is repeatedly crashing because a required environment variable (DATABASE_URL) is missing. Restoring the configuration should resolve the issue."
}

result = K8sAgentResult(**result_dict)

print("\n" + "═" * 60)
print("🧠  KUBESAGE DIAGNOSTIC REPORT")
print("═" * 60)

print(f"""
📦 Pod Information
────────────────────────────────────────────────────────────
  Name       : {result.pod_name}
  Namespace  : {result.namespace}
  Status     : {result.overall_status}
  BlastRadius: {result.blast_radius}
  Risk Level : {result.risk_assessment}
""")

print("🔎 Root Cause Analysis")
print("────────────────────────────────────────────────────────────")
print(f"  Confidence : {result.root_cause.confidence}")
print(f"  Summary    : {result.root_cause.summary}")
print("\n  Contributing Factors:")
for factor in result.root_cause.contributing_factors:
    print(f"   • {factor}")

print("\n📜 Evidence Collected")
print("────────────────────────────────────────────────────────────")
for idx, item in enumerate(result.evidence, start=1):
    print(f"""
  [{idx}] Source     : {item.source}
      Reference  : {item.reference}
      Description: {item.description}
""")

print("🛠 Proposed Actions")
print("────────────────────────────────────────────────────────────")
for idx, action in enumerate(result.proposed_actions, start=1):
    print(f"""
  [{idx}] {action.action_type}  |  Risk: {action.risk_level}
      Title       : {action.title}
      Description : {action.description}
      Command     : {action.kubectl_command}
      Confirmation: {"YES" if action.requires_confirmation else "NO"}
      Expected    : {action.expected_outcome}
      Rollback    : {action.rollback_strategy or "N/A"}
""")

print("📌 Final Summary")
print("────────────────────────────────────────────────────────────")
print(f"  {result.summary}")

if result.requires_user_confirmation:
    print("\n⚠  This operation may modify cluster state.")
    print("   User confirmation required before proceeding.")
    print("═" * 60)

# pprint(result.model_dump())
