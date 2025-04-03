from task import Task
from instr import Instruction
import asyncio

instruction = Instruction()
# # example MULA
# instruction.name = "MULA"
# instruction.type = "C910"

# example MUL
instruction.name = "DIV"
instruction.type = "MExtension"

with open("./data/input/" + instruction.type + "/" + instruction.name, "r") as f:
    instruction.description = f.read()

task = Task(
    f"{instruction.name} + {instruction.description}"
)

if __name__ == "__main__":
    asyncio.run(task.process_task())
