import asyncio
import os
import json
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (
    AzureChatPromptExecutionSettings,
)
from semantic_kernel.contents.chat_history import ChatHistory
from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message

from ioa_observe.sdk.decorators import agent

# Import the existing LightsPlugin
import sys
sys.path.append('..')
from lights_plugin import LightsPlugin


class LightsAgentCore:
    """An AI agent that can control smart lights using Semantic Kernel and LightsPlugin"""

    def __init__(self):
        self.kernel = None
        self.chat_completion = None
        self.execution_settings = None
        self._setup_kernel()

    def _setup_kernel(self):
        """Initialize the Semantic Kernel with LightsPlugin"""
        self.kernel = Kernel()

        # Add OpenAI chat completion
        self.chat_completion = OpenAIChatCompletion(
            api_key=os.environ["OPENAI_API_KEY"],
            ai_model_id="gpt-4o-mini",
        )
        self.kernel.add_service(self.chat_completion)

        # Add the LightsPlugin
        self.kernel.add_plugin(
            LightsPlugin(),
            plugin_name="Lights",
        )

        # Enable planning
        self.execution_settings = AzureChatPromptExecutionSettings()
        self.execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

    async def invoke(self, user_input: str) -> str:
        """Process user input and return response about lights control"""
        try:
            # Create a history for this single interaction
            history = ChatHistory()
            
            # Add system message to guide the agent
            history.add_system_message(
                "You are a smart lights control agent. You can get the current state of lights "
                "and change their on/off state. Available lights are: Table Lamp (id: 1), "
                "Porch light (id: 2), and Chandelier (id: 3). When users ask about lights, "
                "use the available functions to help them."
            )
            
            # Add user input to the history
            history.add_user_message(user_input)

            # Get the response from the AI
            result = await self.chat_completion.get_chat_message_content(
                chat_history=history,
                settings=self.execution_settings,
                kernel=self.kernel,
            )

            return str(result)
        except Exception as e:
            return f"Error processing lights request: {str(e)}"


@agent(name="lights_agent")
class LightsAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = LightsAgentCore()

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        # Extract user message from context.message
        user_message = ""
        
        try:
            if context.message and context.message.parts:
                # Extract text from all message parts
                for part in context.message.parts:
                    if hasattr(part, 'root') and hasattr(part.root, 'text'):
                        user_message += part.root.text + " "
                        
            user_message = user_message.strip()
            
            # If no message found, use default
            if not user_message:
                user_message = "Show me the current state of all lights"
                
            print(f"Lights Agent processing: '{user_message}'")
            
            # Process the actual user message
            result = await self.agent.invoke(user_message)
            await event_queue.enqueue_event(new_agent_text_message(result))
            
        except Exception as e:
            error_msg = f"Error in lights control system: {str(e)}"
            print(f"Lights Agent Error: {error_msg}")
            await event_queue.enqueue_event(new_agent_text_message(error_msg))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        raise Exception("Cancel not supported for lights agent")
