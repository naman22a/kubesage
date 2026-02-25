import os
import dotenv
from strands import Agent
from strands.models.ollama import OllamaModel
from .constants import system_prompt

dotenv.load_dotenv()

ollama_model = OllamaModel(
  host="http://localhost:11434",
  model_id=os.environ['MODEL_ID'],
  max_tokens=10_000
)

agent = Agent(
  model=ollama_model,
  system_prompt=system_prompt
)
