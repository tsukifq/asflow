from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

messages = [
    {
        "role": "system", 
        "content": "You are an expert in LLVM Backend."
    },
    {
        "role": "user", 
        "content": (
"""
You are tasked to generate TableGen code of the following RISC-V custom-defined instruction:
ADD - Add

Description:
ADD adds the values in registers rs1 and rs2 and writes the result to register rd.
This instruction is part of the RISC-V Base ISA (RV32I/RV64I).

Syntax:
add rd, rs1, rs2

Operation:
rd = rs1 + rs2

Execution privilege:
Machine mode, Supervisor mode, User mode

Exceptions:
None (ADD does not cause exceptions)

Instruction format:
31-25  24-20  19-15  14-12  11-7   6-0
funct7  rs2    rs1   funct3  rd    opcode
0000000 XXXXX  XXXXX  000   XXXXX 0110011

Encoding details:
funct7 = 0000000
funct3 = 000
opcode = 0110011 (OP)

instruction type:
Base
"""
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
with open("./response.md", "a") as f:
    f.write(f"## Content\n\n{content}")