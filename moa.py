import asyncio
from dataclasses import dataclass
from typing import List

from autogen_core import AgentId, MessageContext, RoutedAgent, SingleThreadedAgentRuntime, message_handler
from autogen_core.models import ChatCompletionClient, SystemMessage, UserMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from logger import log_process, log_debug

@dataclass
class WorkerTask:
    task: str
    task_type: str
    few_shots: List[str]
    previous_results: List[str]


@dataclass
class WorkerTaskResult:
    result: str


@dataclass
class UserTask:
    task: str


@dataclass
class FinalResult:
    result: str


class WorkerAgent(RoutedAgent):
    def __init__(
        self,
        model_client: ChatCompletionClient,
    ) -> None:
        super().__init__(description="Worker Agent")
        self._model_client = model_client

    @message_handler
    async def handle_task(self, message: WorkerTask, ctx: MessageContext) -> WorkerTaskResult:
        log_debug(f"handle_task worker {self.id}")
        # If the instruction is not formatted, standardize it first.
        if message.task_type == "format":
            formatted = await self.format_instruction(message)
            # Use the formatted task for further processing.
            log_debug(f"Formatted instruction: {formatted}")
            log_process(f"{'-'*80}\nWorker-{self.id}:\n{formatted}")
            return WorkerTaskResult(result=formatted)
        elif message.task_type == "search":
            # Search the repository for similar instructions.
            few_shots = await self.search_repository(message)
        else:
            if message.previous_results:
                system_prompt = "You have been provided with a set of responses from various open-source models regarding the custom LLVM extension instruction. Your task is to synthesize these responses into a high-quality, normalized LLVM tablegen compliant definition. Critically evaluate the provided responses and generate a refined output."
                system_prompt += "\n" + "\n\n".join([f"{i+1}. {r}" for i, r in enumerate(message.previous_results)])
                model_result = await self._model_client.create(
                    [SystemMessage(content=system_prompt), UserMessage(content=message.task, source="user")]
                )
            else:
                model_result = await self._model_client.create(
                    [SystemMessage(content="Format the custom extended instruction into a valid LLVM tablegen snippet."), UserMessage(content=message.task, source="user")]
                )
            assert isinstance(model_result.content, str)
            log_process(f"{'-'*80}\nWorker-{self.id}:\n{model_result.content}")
            return WorkerTaskResult(result=model_result.content)

    # Format the instruction.
    async def format_instruction(self, message: WorkerTask) -> str:
        log_debug(f"format_instruction worker {self.id}")
        # Construct a prompt to normalize the custom extended instruction input.
        system_prompt = "You are a helpful assistant."
        prompt = (
            "Please convert the following custom extended instruction input into a standardized instruction format. \n\n"
            "The instruction should be in the following format: \n"
            "{"
            "    name: <name of the instruction>,"
            "    description: <description of the instruction>,"
            "    syntax: <syntax of the instruction>,"
            "    Operation: <operation of the instruction>,"
            "    arguments: <arguments of the instruction>,"
            "    encodings: <encodings of the instruction>,"
            "    examples: <examples of the instruction>"
            "}"
            "Input:\n" + message.task
        )
        model_result = await self._model_client.create([SystemMessage(content=system_prompt), UserMessage(content=prompt, source="user")])
        assert isinstance(model_result.content, str)
        log_process(f"{'-'*80}\nWorker-{self.id} (Formatted Instruction):\n{model_result.content}")
        return model_result.content

    # Search the repository for similar instructions.
    async def search_repository(self, message: WorkerTask) -> List[str]:
        log_debug(f"search_repository worker {self.id}")
        
        return []


class OrchestratorAgent(RoutedAgent):
    def __init__(
        self,
        model_client: ChatCompletionClient,
        workers_per_layer: list,  # added parameter
        num_layers: int,
    ) -> None:
        super().__init__(description="Aggregator Agent")
        self._model_client = model_client
        self._workers_per_layer = workers_per_layer  # store custom worker counts
        self._num_layers = num_layers

    @message_handler
    async def handle_task(self, message: UserTask, ctx: MessageContext) -> FinalResult:
        log_debug(f"handle_task")
        log_process(f"{'-'*80}\nOrchestrator-{self.id}:\nReceived task: {message.task}")
        # Create task for the first layer.
        worker_task = WorkerTask(
            task=message.task,
            task_type="",
            few_shots=[],
            previous_results=[]
        )
        # TODO: decide the layers to be active.
        for i in range(self._num_layers - 1):
            log_debug(f"handle_task layer {i}")
            num_workers = self._workers_per_layer[i]
            log_debug(f"num_workers: {num_workers}")
            worker_ids = [
                AgentId("worker", f"{self.id.key}/layer_{i}/worker_{j}")
                for j in range(num_workers)
            ]
            log_process(f"{'-'*80}\nOrchestrator-{self.id}:\nDispatch to workers at layer {i}")
            # First layer: format the instruction.
            if i == 0:
                worker_task.task_type = "format"
                results = await asyncio.gather(*[self.send_message(worker_task, worker_id) for worker_id in worker_ids])
                worker_task.task = results[0].result
                log_process(f"{'-'*80}\nOrchestrator-{self.id}:\nReceived results from workers at layer {i}")
            # Second layer: search the repository for similar instructions.
            elif i == 1:
                worker_task = WorkerTask(task=worker_task.task, task_format=True, few_shots=[], previous_results=[r.result for r in results])
            # Third layer: finding similar instructions in the few-shot examples.
            elif i == 2:
                worker_task = WorkerTask(task=worker_task.task, task_format=True, few_shots=[], previous_results=[r.result for r in results])
            # Fourth layer: generate the tablegen snippet according to the few-shot examples.
            elif i == 3:
                worker_task = WorkerTask(task=worker_task.task, task_format=True, few_shots=[], previous_results=[r.result for r in results])
            # Fifth layer: generate the tablegen snippet according to the few-shot examples.
            else:
                worker_task = WorkerTask(task=worker_task.task, task_format=True, few_shots=[], previous_results=[r.result for r in results])
        log_process(f"{'-'*80}\nOrchestrator-{self.id}:\nPerforming final aggregation")
        system_prompt = "You have been provided with a set of responses from various open-source models to the latest user query. Your task is to synthesize these responses into a single, high-quality response. It is crucial to critically evaluate the information provided in these responses, recognizing that some of it may be biased or incorrect. Your response should not simply replicate the given answers but should offer a refined, accurate, and comprehensive reply to the instruction. Ensure your response is well-structured, coherent, and adheres to the highest standards of accuracy and reliability.\n\nResponses from models:"
        system_prompt += "\n" + "\n\n".join([f"{i+1}. {r}" for i, r in enumerate(worker_task.previous_results)])
        model_result = await self._model_client.create(
            [SystemMessage(content=system_prompt), UserMessage(content=message.task, source="user")]
        )
        assert isinstance(model_result.content, str)
        return FinalResult(result=model_result.content)
