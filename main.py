from task import Task
import asyncio

task = Task(
    "I have 432 cookies, and divide them 3:4:2 between Alice, Bob, and Charlie. How many cookies does each person get?"
)
if __name__ == "__main__":
    asyncio.run(task.process_task())
    