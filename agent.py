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
from fns import build_agent_context

dotenv.load_dotenv()

parser = argparse.ArgumentParser(
    prog='KubeSage',
    description='Kubernetes Debugging agent',
)

parser.add_argument('-p', '--pod')
parser.add_argument('-ns', '--namespace')

args = parser.parse_args()

pod_name = args.pod
if args.namespace:
    namespace = args.namespace
else:
    namespace = 'default'

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

pod = list_pod_with_logs(pod_name=pod_name, namespace=namespace)
print("[✔] Fetching last 200 log lines...")
logs_context = build_agent_context(pod)
print("[✔] Building diagnostic context...")
prompt = f"""
TASK:
Determine why the pod is failing and recommend safe remediation.

CLUSTER LOGS:
{logs_context}
"""

print("[✔] Running analysis with LLM...")
buffer = io.StringIO()
with redirect_stdout(buffer):
    result = agent(prompt, 
                   structured_output_model=K8sAgentResult)
print("[✔] Completed analysis with LLM...")

result: K8sAgentResult = result.structured_output

print(f"""
───────────────── DIAGNOSIS ───────────────────

Pod: {result.pod_name}
Namespace: {result.namespace}
Status: {result.overall_status}

Root Cause: (Confidence: {result.root_cause.confidence})
{"\n".join(list(map(lambda x: x , result.root_cause.contributing_factors)))}

Evidence:
{"\n".join(list(map(lambda x: x.source + ": " + x.description , result.evidence)))}
""")

# pprint(result.model_dump())
