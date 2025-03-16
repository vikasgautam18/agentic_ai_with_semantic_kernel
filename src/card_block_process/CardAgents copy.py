from semantic_kernel import Kernel
import os
import asyncio
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from dotenv import load_dotenv
from semantic_kernel.planners import SequentialPlanner
from typing import Annotated
from semantic_kernel.kernel import KernelArguments
from semantic_kernel.functions.kernel_function_decorator import kernel_function
import json


class CardAgentsCopy:
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

    @kernel_function(
        description="This Agent will read the contents of a transcript file and decide if the customer's card is blocked or not. If the card is not blocked, it does nothing.",
        name="ReadTranscriptAgent"
    )
    async def read_transcript(self, transcript_path: Annotated[str, "transcript"]):
        
        with open(transcript_path, "r") as f:
            transcript = f.read()
            return await self.kernel.invoke(self.demo_function, KernelArguments(transcript=transcript))
        
        
    @kernel_function(
        description="""This function will look up the past dues for a customer from a database for the given customer id. 
        """,
        name="LookupPastDuesAgent"
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
    
    # @kernel_function(
    #     description="""This function will return message containing the reason for the blocked card. 
    #     If the customer has past dues, it will return this as the reason for the blocked card. 
    #     If the customer does not have past dues, it will return a message that the card is blocked for some other reason.""",
    #     name="BlockedReasonAgent"
    # )
    # async def blocked_reason(self, past_dues_json: Annotated[str, "past_dues"]):
    #     print(past_dues_json)
    #     past_dues_info = json.loads(past_dues_json)
    #     if past_dues_info["past_dues"]:
    #         return f"Your card is blocked due to past dues. Please clear the dues to unblock the card."
    #     else:
    #         return f"Your card is blocked for some other reason. Please contact customer support for further assistance."
    
    # @kernel_function(
    #     description="This function will draft an email notification to the customer explaining the reason for blocked card. It will be polite in the email to the customer.",
    #     name="DraftEmailAgent"
    # )
    # async def draft_email(self, customerId: Annotated[str, "customer"], past_dues: Annotated[bool, "past_dues"]):
    #     if past_dues:
    #         return f"Dear Customer, Your card is blocked due to past dues. Please clear the dues to unblock the card. Thank you."
    #     else:
    #         return f"Dear Customer, Your card is blocked. Please contact customer support for further assistance. Thank you."
        
            
        