from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.functions import KernelArguments
import os
from dotenv import load_dotenv
import asyncio
kernel = Kernel()

service_id = "default"

load_dotenv()
kernel.add_service(
    AzureChatCompletion(service_id=service_id,
                        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                        deployment_name=os.getenv("AZURE_OPENAI_CHAT_COMPLETION_MODEL"),
                        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    )
)

plugin = kernel.add_plugin(parent_directory="src/plugins/prompt_templates", plugin_name="func")

demo_function = plugin["blocked_reason"]

transcript = """
            Customer ID : 123456
            Date: 16-03-2025 10:23:30

            Call Transcript:
                        
            Agent: how can I help you today? 
            Customer: My card is blocked, could you please help me with that?
            Agent: I am sorry to hear that. Can you please provide me with your name, contact number, email id and address to unblock the card?
            Customer: My name is Vikas, contact number is 1234567890, email id is vsdsdf@gmail.com and address is 1234, 5th Avenue, New York, NY 10001
            Agent: Thank you for providing the details. I have raised a request for this to be looked at immediately. You will receive a confirmation email shortly. Is there anything else I can help you with?
            """ 
            
transcript1 = """
            Customer ID : 136743
            Date: 16-03-2025 10:29:30

            Call Transcript:            
                        
            Agent: how can I help you today? 
            Customer: My account is blocked, could you please help me with that?
            Agent: I am sorry to hear that. Can you please provide me with your name, contact number, email id and address to unblock the account?
            Customer: My name is Vikas, contact number is 1234567890, email id is vsdsdf@gmail.com and address is 1234, 5th Avenue, New York, NY 10001
            Agent: Thank you for providing the details. I have raised a request for this to be looked at immediately. You will receive a confirmation email shortly. Is there anything else I can help you with?
            """
            
async def run_demo():
    return await kernel.invoke(demo_function, KernelArguments(transcript=transcript))

print(asyncio.run(run_demo()))