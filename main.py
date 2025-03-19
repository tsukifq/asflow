from task import Task
import asyncio



MULS = "The detailed information of MULS instruction\n\nMULS——乘累减指令\n语法:\nmuls rd, rs1, rs2\n操作:\nrd ← rd- (rs1 * rs2)[63:0]\n执行权限:\nM mode/S mode/U mode\n异常:\n非法指令异常\n指令格式:\n31-27: 00100\n26-25: 01\n24-20: rs2\n19-15: rs1\n14-12: 001\n11-7:  rd\n6-0: 0001011"
MULA = "The detailed information of MULA instruction\n\nMULA——乘累加指令\n语法：\nmula rd, rs1, rs2\n操作：\nrd ← rd+ (rs1 * rs2)[63:0]\n执行权限：\nM mode/S mode/U mode\n异常：\n非法指令异常\n指令格式：\n31-27bits: 00100\n26-25bits: 00\n24-20bits: rs2\n19-15bits: rs1\n14-12bits: 001\n11-7bits:  rd\n6-0bits: 0001011"

task = Task(
    f"{MULA}"
)

if __name__ == "__main__":
    asyncio.run(task.process_task())
