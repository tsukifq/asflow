import asyncio
from dataclasses import dataclass
from typing import List

from autogen_core import AgentId, MessageContext, RoutedAgent, SingleThreadedAgentRuntime, message_handler
from autogen_core.models import ChatCompletionClient, SystemMessage, UserMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from logger import log_process, log_debug
from prompts import pure_system_prompt, instr_formatting_prompt, files_searching_prompt

@dataclass
class WorkerTask:
    task: str
    type: str
    shots: List[str]
    files: List[str]
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
        if message.type == "format":
            formatted = await self.format_instruction(message)
            # Use the formatted task for further processing.
            log_debug(f"Formatted instruction: {formatted}")
            log_process(f"{'-'*80}\nWorker-{self.id}:\n{formatted}")
            return WorkerTaskResult(result=formatted)
        
        # Search the repository for relevant files.
        elif message.type == "search":
            files = await self.search_repository(message)
            log_process(f"{'-'*80}\nWorker-{self.id}:\n{files}")
            return WorkerTaskResult(result=files)
        
        # Find similar instructions in the few-shot examples.
        elif message.type == "shots":
            shots = await self.find_similar_instructions(message)
            log_process(f"{'-'*80}\nWorker-{self.id}:\n{shots}")
            return WorkerTaskResult(result=shots)

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
        system_prompt = pure_system_prompt
        user_prompt = instr_formatting_prompt.format(task=message.task)
        model_result = await self._model_client.create([SystemMessage(content=system_prompt), UserMessage(content=user_prompt, source="user")])
        assert isinstance(model_result.content, str)
        log_process(f"{'-'*80}\nWorker-{self.id} (Formatted Instruction):\n{model_result.content}")
        return model_result.content

    # Search the repository for relevant files.
    async def search_repository(self, message: WorkerTask) -> str:
        log_debug(f"search_repository worker {self.id}")

        # List all the files in the LLVM RISC-V backend
        proc = await asyncio.create_subprocess_shell(
            "find ../llvm-project/llvm/lib/Target/RISCV -name '*.td'",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()

        all_td_files = []

        if proc.returncode == 0:
            all_td_files = [path for path in stdout.decode().strip().split('\n') if path]
            log_debug(f"Found {len(all_td_files)} TableGen files")
        else:
            log_debug(f"Error listing files in the RISC-V backend: {stderr.decode()}")
            all_td_files = []

        # Construct a prompt to search for relevant files.
        system_prompt = pure_system_prompt
        user_prompt = files_searching_prompt.format(files="\n".join(all_td_files), instr=message.task)
        log_debug(f"Search prompt: {user_prompt}")
        model_result = await self._model_client.create([SystemMessage(content=system_prompt), UserMessage(content=user_prompt, source="user")])
        assert isinstance(model_result.content, str)
        log_process(f"{'-'*80}\nWorker-{self.id} (Search Results):\n{model_result.content}")
        relevant_files = model_result.content
        return relevant_files

    # Find similar instructions in the few-shot examples.
    async def find_similar_instructions(self, message: WorkerTask) -> str:
        log_debug(f"find_similar_instructions worker {self.id}")


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
            type="",
            shots=[],
            files=[],
            previous_results=[]
        )
        # TODO: decide the layers to be active.
        for i in range(self._num_layers):
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
                worker_task.type = "format"
                results = await asyncio.gather(*[self.send_message(worker_task, worker_id) for worker_id in worker_ids])
                worker_task.task = results[0].result
                log_process(f"{'-'*80}\nOrchestrator-{self.id}:\nReceived results from workers at layer {i}")

            # Second layer: search the repository for relevant files.
            elif i == 1:
                worker_task.type = "search"
                results = await asyncio.gather(*[self.send_message(worker_task, worker_id) for worker_id in worker_ids])
                # Parse the search results into a list of files
                file_list = results[0].result.strip().split('\n')
                worker_task.files = [file.strip() for file in file_list if file.strip()]
                log_process(f"{'-'*80}\nOrchestrator-{self.id}:\nReceived results from workers at layer {i}")

            # Third layer: finding similar instructions in the few-shot examples.
            elif i == 2:
                worker_task.type = "shots"
                results = await asyncio.gather(*[self.send_message(worker_task, worker_id) for worker_id in worker_ids])
                worker_task.shots = [r.result for r in results]
                log_process(f"{'-'*80}\nOrchestrator-{self.id}:\nReceived results from workers at layer {i}")

            # Fourth layer: generate the tablegen snippet according to the few-shot examples.
            elif i == 3:
                worker_task.type = "generate"
                worker_task = WorkerTask(task=worker_task.task, shots=[], files=[], previous_results=[r.result for r in results])


            # Fifth layer: generate the tablegen snippet according to the few-shot examples.
            else:
                worker_task = WorkerTask(task=worker_task.task, shots=[], files=[], previous_results=[r.result for r in results])
        log_process(f"{'-'*80}\nOrchestrator-{self.id}:\nPerforming final aggregation")
        
        return FinalResult(result=model_result.content)
