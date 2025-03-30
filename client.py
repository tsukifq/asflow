from config import CONFIG
import os
from dotenv import load_dotenv
from autogen_ext.models.openai import OpenAIChatCompletionClient
load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# client类
class Client:
    def __init__(self):
        self.model_client = OpenAIChatCompletionClient(
            model="deepseek-chat",
            base_url="https://api.deepseek.com",
            api_key=DEEPSEEK_API_KEY,
            model_capabilities={
            "vision": True,
                "function_calling": True,
                "json_output": True,
            },
        )
        
        self.model_client_v3 = OpenAIChatCompletionClient(
            model="deepseek-chat",
            base_url="https://api.deepseek.com",
            api_key=DEEPSEEK_API_KEY,
            model_capabilities={
                "vision": True,
                "function_calling": True,
                "json_output": True,
            },
        )
