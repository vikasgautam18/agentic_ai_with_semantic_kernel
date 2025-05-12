import chainlit as cl
import semantic_kernel as sk
from semantic_kernel.connectors.ai import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import (
    OpenAIChatPromptExecutionSettings,
)
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel import Kernel
from semantic_kernel.functions import KernelArguments, kernel_function
from semantic_kernel.contents import ChatHistory, FunctionCallContent, FunctionResultContent
from semantic_kernel.agents import AgentGroupChat
from semantic_kernel.agents.strategies import TerminationStrategy, KernelFunctionSelectionStrategy, KernelFunctionTerminationStrategy
from semantic_kernel.functions import KernelFunctionFromPrompt
from dotenv import load_dotenv
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
import os, json, logging, psycopg2
from psycopg2.extras import RealDictCursor

from typing import Annotated

load_dotenv()
# Disable verbose connection logs
#logger = logging.getLogger("azure.core.pipeline.policies.http_logging_policy")
#logger.setLevel(logging.ERROR)

# request_settings = OpenAIChatPromptExecutionSettings(
#     function_choice_behavior=FunctionChoiceBehavior.Auto(filters={"excluded_plugins": ["ChatBot"]})
# )

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

class ApprovalTerminationStrategy(TerminationStrategy):
    """A strategy for determining when an agent should terminate."""

    async def should_agent_terminate(self, agent, history):
        """Check if the agent should terminate."""
        return "approved" in history[-1].content.lower()
    
def _create_kernel_with_chat_completion(service_id: str) -> Kernel:
    kernel = Kernel()
    kernel.add_service(
        AzureChatCompletion(service_id=service_id, 
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            deployment_name=os.getenv("AZURE_OPENAI_CHAT_COMPLETION_MODEL"),
            endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        ))
    return kernel

def _create_kernel_with_chat_completion_and_plugin(service_id: str) -> Kernel:
    kernel = Kernel()
    kernel.add_service(AzureChatCompletion(service_id=service_id, 
                                        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                                        deployment_name=os.getenv("AZURE_OPENAI_CHAT_COMPLETION_MODEL"),
                                        endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
                                        ))

    kernel.add_plugin(DatabaseConnector(), plugin_name="db_connector")
    return kernel


ANALYST_NAME = "BusinessAnalyst"
ANALYST_INSTRUCTIONS = """
You are a highly skilled business analyst with extensive experience in writing and executing SQL queries. Fix errors in the SQL queries and ensure they are correct.
Do not make any assumptions about query results. You need to execute necessary SQL queries to determine the reason for a blocked card.
You have access to a PostgreSQL database that contains information about customers and their credit card transactions.
The database contains information about customers in the table customerdata and their credit card transactions in the table credit_card_transactions.
The table customerdata has the following columns: customer_id: , card_blocked, payment_due, card_type and credit_card_no.
The table credit_card_transactions has the following columns: credit_card_no, date, amount, authentication_passed and location.

You have been provided with a customer id by the Orchestrator and you need to query the database to determine the reason for the blocked card.
You need to check the card_blocked column in the customerdata table to determine if the card is blocked. 
If so, you need to check the credit_card_transactions table to determine if the card is blocked due to more than 3 authentication failures. 
If there were more than 3 authentication failures recently, the card is blocked because of that. 
If not, the card is blocked due to some other reason. 
You need to provide the reason (authentication failure or unknown reason) to the Orchestrator.
Respond to the other agents with their names -- like @TriageAgent -- when you interact with them.
"""

ORCHESTRATOR_NAME = "TriageAgent"
ORCHESTRATOR_INSTRUCTIONS = """
"You are a helpful triaging agent. You can use your tools to delegate questions to other appropriate agents."
"Use the response from other agents to answer the question. Do not rely on your own knowledge."
"Other than greetings, do not answer any questions yourself."
"If a user explicitly asks for a human agent or live support, transfer them to the Live Agent."
"If a user is asking the same question more than two times, transfer them to the Live Agent."
"# Very Important Notes"
"- Never respond to the user with any PII data such as password, ID number, etc."
"reach out to the other agents with their names -- like @BusinessAnalyst -- to get the information you need."
"Always ask the customer for the customer ID to identify the customer and provide this ID to the Business Analyst."
You can ask the business analyst agent to determine the reason for the blocked card by executing the necessary SQL queries.
If the reviwer provides a response stating that the card is not blocked, you will conclude that the transcript is being skipped as it is not related to Card Blocking.
After the analysis is provided by Business Analyst, you will draft an email to the customer with the analysis provided by the business analyst.
After you have drafted the email, you MUST approve the analysis by using keywords such as "approved" or "not approved". 
"""

TASK = "Determine the reason for blocked card"

# 4. Create a Kernel Function to determine which agent should take the next turn
selection_function = KernelFunctionFromPrompt(
    function_name="selection",
    prompt=f"""
    Determine which participant takes the next turn in a conversation based on the the most recent participant.
    State only the name of the participant to take the next turn.
    No participant should take more than one turn in a row.
    
    Choose only from these participants:
    - {ORCHESTRATOR_NAME}
    - {ANALYST_NAME}
    
    Always follow these rules when selecting the next participant:
    - After user input, it is {ORCHESTRATOR_NAME}'s turn.
    - After {ORCHESTRATOR_NAME} replies the first time, user may need to provide the customer ID.
    - After user provides the customer ID, it is {ANALYST_NAME}'s turn to determine the reason for the blocked card.
    - if the {ANALYST_NAME} determines that the card is not blocked, it is {ORCHESTRATOR_NAME}'s turn ask the user to check the card again and end the conversation
    - After {ANALYST_NAME} provides the analysis, it is {ORCHESTRATOR_NAME}'s turn to draft an email to the customer.
    - After {ORCHESTRATOR_NAME} drafts the email, it is {ORCHESTRATOR_NAME}'s turn to approve the analysis.


    History:
    {{{{$history}}}}
    """,
)

# 3. Create a Kernel Function to determine if the copy has been approved
termination_function = KernelFunctionFromPrompt(
    function_name="termination",
    prompt="""
    Determine if the analysis has been approved by the Triage Agent.  
    If so, respond with a single word: yes

    History:
    {{$history}}
    """,
)

service_id = "agent" 
filter = cl.SemanticKernelFilter()
# Setup the analyst agent
analyst_kernel = _create_kernel_with_chat_completion_and_plugin("business_analyst")
filter.add_to_kernel(analyst_kernel)
settings = analyst_kernel.get_prompt_execution_settings_from_service_id(service_id="business_analyst")
settings.function_choice_behavior = FunctionChoiceBehavior.Auto()
agent_analyst = ChatCompletionAgent(
    kernel=analyst_kernel,
    name=ANALYST_NAME,
    instructions=ANALYST_INSTRUCTIONS,
    
)

# 3. Create the reviewer agent based on the chat completion service
triage_kernel = _create_kernel_with_chat_completion("Triage Agent")
filter.add_to_kernel(triage_kernel)
agent_orchestrator = ChatCompletionAgent(
    kernel=triage_kernel,
    name=ORCHESTRATOR_NAME,
    instructions=ORCHESTRATOR_INSTRUCTIONS,
)


@cl.on_chat_start
async def on_chat_start():
    
    chat_history = ChatHistory()

    # 4. Place the agents in a group chat with a custom termination strategy
    group_chat = AgentGroupChat(
        agents=[
            agent_analyst,
            agent_orchestrator 
            
        ],
        chat_history=chat_history,
        termination_strategy=KernelFunctionTerminationStrategy(
            agents=[agent_orchestrator],
            function=termination_function,
            kernel=_create_kernel_with_chat_completion_and_plugin("termination"),
            result_parser=lambda result: str(result.value[0]).lower() == "yes",
            history_variable_name="history",
            maximum_iterations=10,
        ),
        selection_strategy=KernelFunctionSelectionStrategy(
            function=selection_function,
            kernel=_create_kernel_with_chat_completion_and_plugin("selection"),
            initial_agent=agent_orchestrator,
            result_parser=lambda result: str(result.value[0]) if result.value is not None else ANALYST_NAME,
            agent_variable_name="agents",
            history_variable_name="history",
        )
    )

    await cl.Message(
        content="Welcome to the Card Blocking Triage Agent. "
                "I will be your assistant today. Please provide customer ID to continue.", author=ORCHESTRATOR_NAME
    ).send()

    #cl.user_session.set("current_agent", agent_orchestrator)
    cl.user_session.set("chat_history", chat_history)
    cl.user_session.set("group_chat", group_chat)

@cl.on_message
async def on_message(message: cl.Message):
    group_chat = cl.user_session.get("group_chat")
    chat_history = cl.user_session.get("chat_history")

    
    # add message to chat history
    chat_history.add_user_message(message.content)
    # Create a Chainlit message for the response stream
    #answer = cl.Message(content="")
    async for msg in group_chat.invoke():
        
        #if str(msg.content):
            #await answer.stream_token(msg.content)
        
        print(f"# {msg.name}: {msg.content}", end="")
        await cl.Message(
            content=f"{msg.name}: {msg.content}", author=msg.name
        ).send()

        chat_history.add_assistant_message(msg.content)

