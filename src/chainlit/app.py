import chainlit as cl
import semantic_kernel as sk
from semantic_kernel.connectors.ai import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import (
    OpenAIChatCompletion,
    OpenAIChatPromptExecutionSettings,
)
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.functions import KernelArguments, kernel_function
from semantic_kernel.contents import ChatHistory, FunctionCallContent, FunctionResultContent
from dotenv import load_dotenv
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
import os, json, logging, psycopg2
from psycopg2.extras import RealDictCursor

from typing import Annotated

load_dotenv()
# Disable verbose connection logs
logger = logging.getLogger("azure.core.pipeline.policies.http_logging_policy")
logger.setLevel(logging.INFO)

request_settings = OpenAIChatPromptExecutionSettings(
    function_choice_behavior=FunctionChoiceBehavior.Auto(filters={"excluded_plugins": ["ChatBot"]})
)

# Example Native Plugin (Tool)
class WeatherPlugin:
    @kernel_function(name="get_weather", description="Gets the weather for a city")
    def get_weather(self, city: str) -> str:
        """Retrieves the weather for a given city."""
        if "paris" in city.lower():
            return f"The weather in {city} is 20°C and sunny."
        elif "london" in city.lower():
            return f"The weather in {city} is 15°C and cloudy."
        else:
            return f"Sorry, I don't have the weather for {city}."

from decimal import Decimal

class DatabaseConnector:
    def __init__(self):
        self.create_connection()

    @kernel_function(description="Create a connection object to the postgres database.")
    def create_connection(self):
        print("create_connection function called... ")
        connection = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        self.connection = connection
        self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)

    @kernel_function(description="Fetches data based on the query provided.")
    def query_database(self, query: Annotated[str, "query to be executed"]) -> Annotated[str, "Returns the queried information as a json"]:
        """
        Fetches the information from the required table in PostgreSQL database.

        :param query (str): the query to be executed.
        :return: fetched information as a JSON string.
        :rtype: str
        """
        print("query_database function called... query: ", query)
        try:
            # if(self.connection != True):
            #     self.create_connection()
            
            #connection = self.connection
            cursor = self.cursor
            cursor.execute(query=query)
            result_record = cursor.fetchone()
            if result_record:
                # Convert Decimal values to strings
                for key, value in result_record.items():
                    if isinstance(value, Decimal):
                        result_record[key] = str(value)
                return json.dumps({"result_record": result_record})
            else:
                return json.dumps({"error": "An error occured while fetching the data."})
        except Exception as e:
            return json.dumps({"error": str(e)})
        # finally:
        #     if connection:
        #         self.close_connection()
        
    
    @kernel_function(description="Closes the connection to the database.")
    def close_connection(self) -> Annotated[str, "Returns a message indicating the status of the connection closure."]:
        """
        Closes the connection to the PostgreSQL database.

        :return: Message indicating the status of the connection closure.
        :rtype: str
        """
        print("close_connection function called... ")
        try:
            if self.connection:
                self.cursor.close()
                self.connection.close()
            return "Connection closed successfully."
        except Exception as e:
            return str(e)

@cl.on_chat_start
async def on_chat_start():
    service_id = "agent" 
    # Setup Semantic Kernel
    kernel = sk.Kernel()

    # Add AI Chat Completion service
    ai_service = AzureChatCompletion(service_id=service_id, 
                                        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                                        deployment_name=os.getenv("AZURE_OPENAI_CHAT_COMPLETION_MODEL"),
                                        endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
                                        )
    kernel.add_service(ai_service)
   
    # Import the WeatherPlugin
    kernel.add_plugin(DatabaseConnector(), plugin_name="db_plugin")
    settings = kernel.get_prompt_execution_settings_from_service_id(service_id=service_id)
    settings.function_choice_behavior = FunctionChoiceBehavior.Auto()


    agent = ChatCompletionAgent(
        kernel=kernel,
        name="Host",
        instructions="""You are a helpful Software Engineer with expertise in SQL queries. Answer the user question by retrieving required information from database tables. 
        Account information is stored in the 'accounts' table and the schema is as follows:
        account_id: int, name: text, balance: decimal, email: text, phone: text, address: text
        
        The user will ask questions about the account information by providing the account_id.
        
        Write the response in a clear and concise manner in a short paragraph.
        Remember to create the connection first and then query the database as needed. 
        After the customer confirms there are no more questions, close the Database connection""",
        arguments=KernelArguments(settings=settings),
    )

    chat_history = ChatHistory()
    
    # Instantiate and add the Chainlit filter to the kernel
    # This will automatically capture function calls as Steps
    cl.SemanticKernelFilter(kernel=kernel)

    cl.user_session.set("current_agent", agent)
    cl.user_session.set("kernel", kernel)
    cl.user_session.set("ai_service", ai_service)
    cl.user_session.set("chat_history", chat_history)

@cl.on_message
async def on_message(message: cl.Message):
    #kernel = cl.user_session.get("kernel") # type: sk.Kernel
    #ai_service = cl.user_session.get("ai_service") # type: OpenAIChatCompletion
    chat_history = cl.user_session.get("chat_history") # type: ChatHistory
    agent = cl.user_session.get("current_agent") # type: ChatCompletionAgent

    # Add user message to history
    chat_history.add_user_message(message.content)

    # Create a Chainlit message for the response stream
    answer = cl.Message(content="")

    async for msg in agent.invoke_stream(messages=chat_history):
        if str(msg.content.content):
            await answer.stream_token(msg.content.content)
        
        print(f"# {msg.name}: ", end="")
        if (
            not any(isinstance(item, (FunctionCallContent, FunctionResultContent)) for item in msg.items)
            and msg.content
        ):
            # We only want to print the content if it's not a function call or result
            print(f"{msg.content}", end="", flush=True)
    # Add the full assistant response to history
    chat_history.add_assistant_message(answer.content)

    # Send the final message
    await answer.send()