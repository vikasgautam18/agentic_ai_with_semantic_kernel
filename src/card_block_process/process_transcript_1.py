from semantic_kernel import Kernel
import os
import asyncio
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from dotenv import load_dotenv
from semantic_kernel.planners import SequentialPlanner
from typing import Annotated
from semantic_kernel.kernel import KernelArguments
from semantic_kernel.functions.kernel_function_decorator import kernel_function
import CardAgents

load_dotenv()
azure_openai_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
azure_openai_deployment_name = os.getenv("AZURE_OPENAI_CHAT_COMPLETION_MODEL")

kernel = Kernel()
service_id = "default"
kernel.add_service(
    AzureChatCompletion(service_id=service_id,
                        api_key=azure_openai_key,
                        deployment_name=azure_openai_deployment_name,
                        endpoint = azure_openai_endpoint
    )
)


planner = SequentialPlanner(
    kernel,
    service_id
)

agents_plugin = kernel.add_plugin(CardAgents.CardAgents(), "CardAgents")

goal = f"""
        Determine why the card is blocked using different agents. 
        Use ReadTranscriptAgent to read the transcript and determine if the card is blocked or not. 
        If the card is not blocked, then do nothing.
        if the card is blocked, then use LookupPastDuesAgent to look up the past dues for the customer.
        If the customer has past dues, this is the reason for the blocked card.
        if the customer does not have past dues, return a message that the card is blocked for some other reason.
    """

# if the card is blocked, then look up the past dues for the customer.
#     if the customer has past dues, return this as the reason for the blocked card.
#     if the customer does not have past dues, return a message that the card is blocked for some other reason.

async def call_planner():
    return await planner.create_plan(goal)

sequential_plan = asyncio.run(call_planner())

print("The plan's steps are:")
for step in sequential_plan._steps:
    print(
        f"- {step.description.replace('.', '') if step.description else 'No description'} using {step.metadata.fully_qualified_name} with parameters: {step.parameters}"
    )

async def generate_answer(transcript_path: str = "resources/transcripts/transcript1.txt"):
    return await sequential_plan.invoke(kernel, KernelArguments(transcript_path=transcript_path))

result = asyncio.run(generate_answer())

print(result)