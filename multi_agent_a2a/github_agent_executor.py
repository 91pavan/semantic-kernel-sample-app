import asyncio
import os
from datetime import datetime
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.functions import KernelArguments
from semantic_kernel.kernel import Kernel
from semantic_kernel.contents.chat_history import ChatHistory
from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message

from ioa_observe.sdk.decorators import agent

# Import the existing GitHub plugin
import sys
sys.path.append('..')
from github import GitHubPlugin, GitHubSettings


class GithubAgentCore:
    """An AI agent that can query GitHub repositories using Semantic Kernel and GitHubPlugin"""

    def __init__(self):
        self.kernel = None
        self.chat_completion = None
        self.settings = None
        self._setup_kernel()

    def _setup_kernel(self):
        """Initialize the Semantic Kernel with GitHubPlugin"""
        self.kernel = Kernel()

        # Add OpenAI chat completion
        service_id = "github_agent"
        self.chat_completion = OpenAIChatCompletion(
            api_key=os.environ["OPENAI_API_KEY"], 
            ai_model_id="gpt-4o-mini", 
            service_id=service_id
        )
        self.kernel.add_service(self.chat_completion)

        # Configure function choice behavior
        self.settings = self.kernel.get_prompt_execution_settings_from_service_id(service_id=service_id)
        self.settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

        # Set up GitHub plugin
        gh_settings = GitHubSettings(token=os.getenv("GITHUB_ACCESS_TOKEN"))
        self.kernel.add_plugin(plugin=GitHubPlugin(gh_settings), plugin_name="GithubPlugin")

    async def invoke(self, user_input: str) -> str:
        """Process user input and return response about GitHub queries"""
        try:
            current_time = datetime.now().isoformat()
            
            # Create a specialized GitHub agent
            agent = ChatCompletionAgent(
                kernel=self.kernel,
                name="GithubAssistantAgent",
                instructions=f"""
                You are an agent designed to query and retrieve information from GitHub repositories in a read-only
                manner. You are also able to access the profile of the active user.

                Use the current date and time to provide up-to-date details or time-sensitive responses.

                The default repository you can query is: microsoft/semantic-kernel
                You can also query other public repositories if the user specifies them.

                The current date and time is: {current_time}.
                """,
            )

            # Create arguments with current time
            arguments = KernelArguments(now=datetime.now().strftime("%Y-%m-%d %H:%M"))

            # Process the user input
            response_generator = agent.invoke(
                messages=user_input, 
                thread=None, 
                arguments=arguments
            )
            
            # Collect all response parts
            full_response = ""
            async for response in response_generator:
                if response.content:
                    full_response += str(response.content)

            return full_response if full_response else "No response generated from GitHub agent"
            
        except Exception as e:
            return f"Error processing GitHub request: {str(e)}"


@agent(name="github_agent")
class GithubAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = GithubAgentCore()

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
                user_message = "Get my GitHub user profile"
                
            print(f"GitHub Agent processing: '{user_message}'")
            
            # Process the actual user message
            result = await self.agent.invoke(user_message)
            await event_queue.enqueue_event(new_agent_text_message(result))
            
        except Exception as e:
            error_msg = f"Error in GitHub agent: {str(e)}"
            print(f"GitHub Agent Error: {error_msg}")
            await event_queue.enqueue_event(new_agent_text_message(error_msg))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        raise Exception("Cancel not supported for GitHub agent")
