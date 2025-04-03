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
You are tasked to generate the instruction TableGen description of the following custom extended instruction.
VSETVLI - Set Vector Length Immediate

Description:
VSETVLI configures the vector unit by setting the vector length based on the immediate value and updates the vl and vtype CSRs. 
This instruction is part of the RISC-V Vector Extension (RVV).

Syntax:
vsetvli rd, rs1, vtypei

Operation:
vtype = encode(vtypei)
vl = minimum(rs1, VLMAX(vtype))
rd = vl

Execution privilege:
Machine mode, Supervisor mode, User mode

Exceptions:
Illegal instruction exception (if the vector extension is not implemented or the configuration is invalid)

Instruction format:
31-30  29-25  24-20  19-15  14-12  11-7   6-0
 0 0  zimm[10:6] zimm[4:0]  rs1   1 1 1   rd   1010111

Encoding details:
rs1 = source register containing the requested vector length (or x0 to use the maximum possible vector length)
rd = destination register for the new vector length (or x0 to not write the result)
zimm = the immediate value that encodes vtype settings:
  - vsew[2:0] (bits 5:3): Element width (SEW = 8×2^vsew bits)
  - vlmul[1:0] (bits 2:1): Vector register group multiplier (LMUL = 2^vlmul)
  - vma (bit 0): Vector mask agnostic
  - vta (bit 7): Vector tail agnostic
  - reserved (bits 10:8): Must be zero

opcode = 1010111 (VECTOR)

instruction type:
Vector extension
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