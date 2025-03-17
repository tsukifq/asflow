import asyncio
import json  # added to load config
from moa import WorkerAgent, OrchestratorAgent, UserTask, AgentId
from autogen_core import SingleThreadedAgentRuntime
from autogen_ext.models.openai import OpenAIChatCompletionClient
from client import Client

# Task类
class Task:
    def __init__(self, task: str):
        self.task = task
        from config import CONFIG
        self.worker_agent_num = CONFIG["worker_agent_num"]
        self.num_layers = CONFIG["num_layers"]

    def __str__(self):
        return self.task
    
    async def process_task(self):
        runtime = SingleThreadedAgentRuntime()
        model_client = Client()
        await WorkerAgent.register(
            runtime, "worker", lambda: WorkerAgent(    
                model_client=model_client
            )
        )

        await OrchestratorAgent.register(
            runtime,
            "orchestrator",
            lambda: OrchestratorAgent(
                model_client=model_client,
                worker_agent_types=["worker"] * self.worker_agent_num, 
                num_layers=self.num_layers
            ),
        )

        runtime.start()
        result = await runtime.send_message(UserTask(task=self.task), AgentId("orchestrator", "default"))
        await runtime.stop_when_idle()
        print(f"{'-'*80}\nFinal result:\n{result.result}")

