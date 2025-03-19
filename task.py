import asyncio
import json  # added to load config
from moa import WorkerAgent, OrchestratorAgent, UserTask, AgentId
from autogen_core import SingleThreadedAgentRuntime
from autogen_ext.models.openai import OpenAIChatCompletionClient
from client import Client
from logger import log_result, log_debug  # added
from datetime import datetime

# Task类
class Task:
    def __init__(self, task: str):
        self.task = task
        from config import CONFIG
        self.worker_agent_num = CONFIG["worker_agent_num"]
        self.num_layers = CONFIG["num_layers"]
        self.workers_per_layer = CONFIG["workers_per_layer"]  # added

    def __str__(self):
        return self.task
    
    async def process_task(self):
        runtime = SingleThreadedAgentRuntime()
        # Log current timestamp before starting runtime.
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_debug(f"Program run started at: {current_time}")
        await WorkerAgent.register(
            runtime, 
            "worker", 
            lambda: WorkerAgent(
                model_client=Client().model_client
            )
        )

        await OrchestratorAgent.register(
            runtime,
            "orchestrator",
            lambda: OrchestratorAgent(
                model_client=Client().model_client,
                workers_per_layer=self.workers_per_layer,  # passed custom counts
                num_layers=self.num_layers
            ),
        )

        runtime.start()
        result = await runtime.send_message(UserTask(task=self.task), AgentId("orchestrator", "default"))
        await runtime.stop_when_idle()
        log_result(f"{'-'*80}\nFinal result:\n{result.result}")

