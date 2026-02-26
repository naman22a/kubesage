import os
import dotenv
from strands import Agent
from strands.models.ollama import OllamaModel
from strands.models.bedrock import BedrockModel
from .constants import system_prompt

dotenv.load_dotenv()

ollama_model = OllamaModel(
  host="http://localhost:11434",
  model_id=os.environ['MODEL_ID'],
  max_tokens=10_000
)

bedrock_model = BedrockModel(
  model_id=os.environ['MODEL_ID'],
  region_name=os.environ['REGION'],
  max_tokens=10_000
)

agent = Agent(
  model= bedrock_model if os.environ['LLM_PROVIDER'] == 'bedrock' else ollama_model,
  system_prompt=system_prompt
)
