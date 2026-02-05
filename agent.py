import io
from contextlib import redirect_stdout
from pprint import pprint

from strands import Agent
from strands.models.ollama import OllamaModel

from k8s import list_pods_with_logs
from constants import system_prompt
from custom_types import K8sAgentResult

ollama_model = OllamaModel(
    host="http://localhost:11434",
    model_id="llama3.2"
)

agent = Agent(
    model=ollama_model,
    system_prompt=system_prompt
)

buffer = io.StringIO()
with redirect_stdout(buffer):
    result = agent(f"Why is my pod dead ? \n Context about my pods is here: \n {list_pods_with_logs()}", 
                   structured_output_model=K8sAgentResult)

result: K8sAgentResult = result.structured_output

pprint(result)