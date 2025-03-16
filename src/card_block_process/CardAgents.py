from semantic_kernel import Kernel
import os
import asyncio
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from dotenv import load_dotenv
from semantic_kernel.planners import SequentialPlanner
from typing import Annotated, Any, Callable, Set

from semantic_kernel.kernel import KernelArguments
from semantic_kernel.functions.kernel_function_decorator import kernel_function

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import FunctionTool, ToolSet

class CardAgents:
    def __init__(self):
        self.kernel = Kernel()
        self.service_id = "default"
        load_dotenv()
        self.kernel.add_service(
            AzureChatCompletion(service_id=self.service_id,
                                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                                deployment_name=os.getenv("AZURE_OPENAI_CHAT_COMPLETION_MODEL"),
                                endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
            )
        )
        self.plugin = self.kernel.add_plugin(parent_directory="src/plugins/prompt_templates", plugin_name="func")
        self.demo_function = self.plugin["blocked_reason"]
        
        self.project_client = AIProjectClient.from_connection_string(
        credential=DefaultAzureCredential(),
        conn_str=os.getenv("AI_PROJECT_CONNECTION_STRING")
        )

    async def lookup_past_dues(self, inputs: Annotated[str, "customer"]):
        print(f" lookup_past_dues :: inputs: {inputs}")
        customerId = inputs.split(":")[1].strip()
        print(f" lookup_past_dues :: customerId: {customerId}")
        
        past_dues = {
            "123456": True,
            "136743": False,
            "112233": True,
            "445566": False
        }
        
        if(past_dues.get(customerId, False)):
            return "Customer has past dues"
        else:
            return "Customer does not have past dues"
    

    @kernel_function(
        description="This Agent will read the contents of a transcript file and decide if the customer's card is blocked or not. If the card is not blocked, it does nothing.",
        name="ReadTranscriptAgent"
    )
    async def read_transcript(self, transcript_path: Annotated[str, "transcript"]):
        
        with open(transcript_path, "r") as f:
            transcript = f.read()
            return await self.kernel.invoke(self.demo_function, KernelArguments(transcript=transcript))
        
        
    @kernel_function(
       description="This function will use an azure ai agent to look up the past dues for a given customer",
         name="LookupPastDuesAgent"
   )
    def LookupPastDuesAgent(
        self,
        customer: Annotated[str, "The customer for which dues are to be looked up"],
        
    ) -> Annotated[bool, "the response from the LookupPastDuesAgent which indicates if the customer has past dues or not"]:
        final_response: bool = False
        print(f"Looking up the past dues for the customer:: {customer}")
        agent = self.project_client.agents.create_agent(
        model=os.getenv("AZURE_OPENAI_CHAT_COMPLETION_MODEL"),
        name="LookupPastDuesAgent",
        instructions="""You are a helpful assistant that is meant to look up the past dues for a given customer. You will be given the name of the customer for which you need to look up the past dues.
        Look up the past dues for the given customer and return if the customer has past dues or not.""",

        )
        thread = self.project_client.agents.create_thread()
            
        message = self.project_client.agents.create_message(
                thread_id=thread.id,
                role="user",
                content=f"""Look up the past dues for the customer {customer}""",
            )
        
        user_functions: Set[Callable[..., Any]] = {
            self.lookup_past_dues
        }
        functions = FunctionTool(user_functions)
    
        toolset = ToolSet()
        toolset.add(functions)
            
        run = self.project_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id, toolset=toolset)
            
        messages = self.project_client.agents.list_messages(thread_id=thread.id)
            
        print(messages.data[0].content[0].text.value)
            
        final_response = messages.data[0].content[0].text.value
            
            
        return final_response