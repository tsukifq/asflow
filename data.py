import asyncio
import subprocess
from instr import Instruction
from client import Client
from autogen_core.models import ChatCompletionClient, SystemMessage, UserMessage
from prompts import tablegen_extraction_prompt

class Data:
    def __init__(self):
        self.client = Client()
        self.model_client = self.client.model_client_v3

    # invoke the model to collect data and extract instruction implementation data from LLVM RISCV TableGen code
    async def collect_data(self, instr: Instruction):
        # Retrieve LLVM RISCV TableGen files.
        td_files = ["RISCV.td", "RISCVFeatures.td", "RISCVInstrFormats.td", "RISCVInstrInfo.td"]
        file_content = ""
        for filename in td_files:
            full_path = f"../llvm-project/llvm/lib/Target/RISCV/{filename}"
            result = subprocess.run(["cat", full_path], capture_output=True, text=True)
            if result.returncode == 0:
                file_content += f"--- Contents of {filename} ---\n" + result.stdout + "\n"
            else:
                file_content += f"--- Error reading {filename} ---\n"
        # Build the prompt for extracting instruction implementation data.
        system_prompt = "You are a helpful LLVM RISC-V developer. You will follow the user's instructions to complete the task."
        # Format the template with the actual values
        user_prompt = tablegen_extraction_prompt.format(instr=instr, file_content=file_content)
        # print(user_prompt)
        response = await self.model_client.create(
            [SystemMessage(content=system_prompt), UserMessage(content=user_prompt, source="user")],
        )
        return response

    
data = Data()
instr = Instruction()
instr.name = "LHU"
instr.description = """
The LW instruction loads a 32-bit value from memory into rd. LH loads a 16-bit value from memory,
then sign-extends to 32-bits before storing in rd. LHU loads a 16-bit value from memory but then zero
extends to 32-bits before storing in rd. LB and LBU are defined analogously for 8-bit values. The SW,
SH, and SB instructions store 32-bit, 16-bit, and 8-bit values from the low bits of register rs2 to
memory.
"""
response = asyncio.run(data.collect_data(instr))
with open("./data/instruction/" + instr.name + ".td", "w") as f:
    f.write(instr.description + "\n")
    f.write(response.content)

with open("./data/shots/" + instr.name + ".td", "w") as f:
    f.write(response.content)