import chainlit as cl
import semantic_kernel as sk
from semantic_kernel.connectors.ai import FunctionChoiceBehavior
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.functions import KernelArguments, kernel_function
from semantic_kernel.contents import ChatHistory, FunctionCallContent, FunctionResultContent
from dotenv import load_dotenv
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

import os

load_dotenv()

# Example Native Plugin (Tool)
class WeatherPlugin:
    @kernel_function(name="get_weather", description="Gets the weather for a city")
    def get_weather(self, city: str) -> str:
        """Retrieves the weather for a given city."""
        if "paris" in city.lower():
            return f"The weather in {city} is 20°C and sunny."
        elif "london" in city.lower():
            return f"The weather in {city} is 15°C and cloudy."
        elif "berlin" in city.lower():
            return f"The weather in {city} is 18°C and rainy."
        elif "new york" in city.lower():
            return f"The weather in {city} is 25°C and sunny."
        elif "tokyo" in city.lower():
            return f"The weather in {city} is 22°C and rainy."
        else:
            return f"Sorry, I don't have the weather for {city}."



@cl.on_chat_start
async def on_chat_start():
    service_id = "agent"
    
    # Setup the brain (Core)
    kernel = sk.Kernel()

    # Add AI Chat Completion service
    ai_service = AzureChatCompletion(service_id=service_id, 
                                        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                                        deployment_name=os.getenv("AZURE_OPENAI_CHAT_COMPLETION_MODEL"),
                                        endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
                                        )
    kernel.add_service(ai_service)
   
    # Import the WeatherPlugin
    kernel.add_plugin(WeatherPlugin(), plugin_name="weather_plugin")
    settings = kernel.get_prompt_execution_settings_from_service_id(service_id=service_id)
    settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

    # provide the agent a purpose, persona and situational awareness
    agent = ChatCompletionAgent(
        kernel=kernel,
        name="Host",
        instructions="""You are a helpful assistant that helps users with their queries.
        You have access to a plugin that provides weather information for various cities.
        Use the plugin to fetch weather details when the user asks about the weather in a specific city.
        If the user asks for weather information, call the 'get_weather' function from the 'weather_plugin'.
        If the user asks you to email them the weather information, politely inform them that you cannot send emails but please draft the email content for them.
        If the user asks something unrelated to weather, respond politely that you can only help with weather-related queries.
        """,
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