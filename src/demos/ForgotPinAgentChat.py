import asyncio
import os

from semantic_kernel.agents import AgentGroupChat, ChatCompletionAgent
from semantic_kernel.agents.strategies.termination.termination_strategy import TerminationStrategy
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.contents.utils.author_role import AuthorRole
from semantic_kernel.kernel import Kernel
from semantic_kernel.contents.annotation_content import AnnotationContent
from semantic_kernel.contents import ChatHistoryTruncationReducer
from semantic_kernel.functions.kernel_function_from_prompt import KernelFunctionFromPrompt
from semantic_kernel.agents.strategies.selection.kernel_function_selection_strategy import (
    KernelFunctionSelectionStrategy,
)
from semantic_kernel.agents.strategies.termination.kernel_function_termination_strategy import (
    KernelFunctionTerminationStrategy,
)
from semantic_kernel.agents import AgentGroupChat
from semantic_kernel.agents.strategies import TerminationStrategy
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.functions import kernel_function
from semantic_kernel.connectors.ai import FunctionChoiceBehavior

from typing import Annotated
import json
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
load_dotenv()

def _create_kernel_with_chat_completion(service_id: str) -> Kernel:
    kernel = Kernel()
    kernel.add_service(AzureChatCompletion(service_id=service_id, 
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

class ApprovalTerminationStrategy(TerminationStrategy):
    """A strategy for determining when an agent should terminate."""

    async def should_agent_terminate(self, agent, history):
        """Check if the agent should terminate."""
        return "approved" in history[-1].content.lower()
    
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
        
async def main():
    try:
        TRANSCRIPTION_REVIEWER = "CreditCardAgent"
        TRANSCRIPTION_REVIEWER_INSTRUCTIONS = """
        You are a credit card agent who has been tasked with greeting the customer and resolving issues related to credit card forgotten pin.
        Greet the customer and ask them what is the issue with the credit card.
        If the customer has forgotten the pin, proceed ahead. Else exit the chat.
        Ask the user exactly once  for customer id , account id , email , phone number and otp.
        Get the customer id.
        Get account id .
        Get email.
        Get phone number.
        Once these details are shared get otp from the customer .
        Provide all these user details to the Orchestrator. 
        If customer does not provide the above details , exit the chat .
        """

        ANALYST_NAME = "BusinessAnalyst"
        ANALYST_INSTRUCTIONS = """
        You are a highly skilled business analyst with extensive experience in writing and executing SQL queries. Fix errors in the SQL queries and ensure they are correct.
        Do not make any assumptions about query results. You need to execute necessary SQL queries to determine the reason for a blocked card.
        You have access to a PostgreSQL database that contains information about customers and their credit card transactions.
        The database contains information about customers in the table customerdata and their credit card transactions in the table credit_card_transactions.
        The table customerdata has the following columns: customer_id: , card_blocked, payment_due, card_type and credit_card_no.
        The table credit_card_transactions has the following columns: credit_card_no, date, amount, authentication_passed and location.

        You have been provided with a customer id by the Orchestrator and you need to query the database to determine if it is a valid customer.
        If it is a valid customer proceed ahead, otherwise exit the chat.
        Verify the account id, email id,phone from the accounts table of customer.
        Verify that the otp is equal to 1001.Do not check otp with the database.
        If all above conditions are satisfied ,inform the Orchestrator to draft a note for resetting the pin.

        """

        ORCHESTRATOR_NAME = "Orchestrator"
        ORCHESTRATOR_INSTRUCTIONS = """
        You are an orchestrator who has been tasked with coordinating the work of the credit card agent and the business analyst.
        You will receive the customer id ,account id ,email ,phone and otp from the credit card agent and pass it to the business analyst and ask it to verify the details.
        If the business analyst provides a response saying the draft a note you will draft an note to the customer with a test link to reset the password.
        Following is the note template:
        Hello <customer_name>,
        Your request to reset your credit card pin has been approved. Please click on the link below to reset your pin.
        <test_link>
        Thank you for your patience.
        Regards,
        <XYZ>
        Provide response as "Approved" only if the email is drafted successfully. 
        """


        agent_creditcard= ChatCompletionAgent(
        kernel=_create_kernel_with_chat_completion("creditcardagent"),
        name=TRANSCRIPTION_REVIEWER,
        instructions=TRANSCRIPTION_REVIEWER_INSTRUCTIONS,
        )

        analyst_kernel = _create_kernel_with_chat_completion_and_plugin("business_analyst")
        settings = analyst_kernel.get_prompt_execution_settings_from_service_id(service_id="business_analyst")
        settings.function_choice_behavior = FunctionChoiceBehavior.Auto()
        agent_analyst = ChatCompletionAgent(
        kernel=analyst_kernel,
        name=ANALYST_NAME,
        instructions=ANALYST_INSTRUCTIONS,
        )
        agent_orchestrator = ChatCompletionAgent(
        kernel=_create_kernel_with_chat_completion("orchestrator"),
        name=ORCHESTRATOR_NAME,
        instructions=ORCHESTRATOR_INSTRUCTIONS,
        )

        TERMINATION_KEYWORD = "Approved"
        selection_function = KernelFunctionFromPrompt(
        function_name="selection",
        prompt=f"""
        Determine which participant takes the next turn in a conversation based on the the most recent participant.
        State only the name of the participant to take the next turn.
        No participant should take more than one turn in a row.

        Choose only from these participants:
        - {TRANSCRIPTION_REVIEWER}
        - {ANALYST_NAME}
        - {ORCHESTRATOR_NAME}

        Always follow these rules when selecting the next participant:
        - {TRANSCRIPTION_REVIEWER} will greet the user and enquire about the issue faced by the customer.
        - After user input, it is {TRANSCRIPTION_REVIEWER}'s turn.
        - Only {TRANSCRIPTION_REVIEWER} can ask for customer details.
        - {TRANSCRIPTION_REVIEWER} will get the customer details from the user and pass it to {ORCHESTRATOR_NAME}.
        - It will be {ORCHESTRATOR_NAME}'s turn only once customer details are provided.
        - After {ORCHESTRATOR_NAME} provides details, it is {ANALYST_NAME}'s turn.
        - If  {ANALYST_NAME} responds , it is {ORCHESTRATOR_NAME}'s turn.
        - Terminate only when  {ORCHESTRATOR_NAME} responds as {TERMINATION_KEYWORD}

        History:
        {{{{$history}}}}
        """,
        )

       

        termination_function = KernelFunctionFromPrompt(
            function_name="termination",
            prompt=f"""
            Examine the RESPONSE by Orchestrator agent and determine the response.
            If APPROVED, respond with a single word without explanation: {TERMINATION_KEYWORD}.
            

            RESPONSE:
            {{{{$history}}}}
            """,
        )

        history_reducer = ChatHistoryTruncationReducer(target_count=1)


        # 4. Place the agents in a group chat with a custom termination strategy
        group_chat = AgentGroupChat(
        agents=[
            agent_creditcard,
            agent_analyst,
            agent_orchestrator 
        
               ],
        termination_strategy=ApprovalTerminationStrategy(
        agents=[agent_orchestrator,agent_analyst,agent_creditcard],
        maximum_iterations=1,
            ),
        )  

    
       
        is_complete: bool = False
        while not is_complete:
            user_input = input("User:> ")
            if not user_input:
                continue

            if user_input.lower() == "exit":
                is_complete = True
                break

            if user_input.lower() == "reset":
                await group_chat.reset()
                print("[Conversation has been reset]")
                continue

            await group_chat.add_chat_message(ChatMessageContent(role=AuthorRole.USER, content=user_input))

            async for response in group_chat.invoke():
                print(f"# {response.role} - {response.name or '*'}: '{response.content}'")

            if group_chat.is_complete:
                is_complete = True
                break
    finally:
        #await agent_writer.delete()
        print("Finally")


if __name__ == "__main__":
    asyncio.run(main())