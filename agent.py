import io
from contextlib import redirect_stdout
from pprint import pprint

from strands import Agent
from strands.models.ollama import OllamaModel

from k8s import list_pods_with_logs
from constants import system_prompt
from custom_types import K8sAgentResult
from fns import build_agent_context

ollama_model = OllamaModel(
    host="http://localhost:11434",
    model_id="qwen3-coder"
)

agent = Agent(
    model=ollama_model,
    system_prompt=system_prompt
)

pods = list_pods_with_logs()
logs_context = build_agent_context(pods)
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