from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

instruction = "LW"
with open("./data/input/Base/" + instruction, "r") as f:
    data = f.read()

messages = [
    {
        "role": "system", 
        "content": "You are an expert in LLVM Backend."
    },
    {
        "role": "user", 
        "content": (
"""
You are tasked to generate the instruction TableGen description of the following custom extended instruction.
"""
        + data
        )
    }
]

response = client.chat.completions.create(
    model="deepseek-reasoner",
    messages=messages
)

# reasoning_content = response.choices[0].message.reasoning_content
content = response.choices[0].message.content

# store the reasoning content and content in a markdown file
with open("./data/output/LLM/Base.md", "a") as f:
    f.write(f"## Content\n\n{content}")