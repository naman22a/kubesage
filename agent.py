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

ollama_model = OllamaModel(
    host="http://localhost:11434",
    model_id=os.environ['MODEL_ID']
)

agent = Agent(
    model=ollama_model,
    system_prompt=system_prompt
)

pod = list_pod_with_logs(pod_name=pod_name, namespace=namespace)
logs_context = build_agent_context(pod)
prompt = f"""
TASK:
Determine why the pod is failing and recommend safe remediation.

CLUSTER LOGS:
{logs_context}
"""

buffer = io.StringIO()
with redirect_stdout(buffer):
    result = agent(prompt, 
                   structured_output_model=K8sAgentResult)

result: K8sAgentResult = result.structured_output

pprint(result)