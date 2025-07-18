import asyncio
import os
import sys
from datetime import datetime

from semantic_kernel.agents import ChatCompletionAgent, ChatHistoryAgentThread
from semantic_kernel.connectors.ai import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.functions import KernelArguments
from semantic_kernel.kernel import Kernel

from github import GitHubPlugin, GitHubSettings

from ioa_observe.sdk import Observe
from ioa_observe.sdk.decorators import agent as agent_decorator, tool, graph
from ioa_observe.sdk.tracing import session_start

Observe.init("github_agent", api_endpoint=os.getenv("OTLP_HTTP_ENDPOINT"))

from ioa_observe.sdk.decorators import agent as agent_decorator

@agent_decorator(name="github_agent", description="An agent to interact with GitHub repositories")
class DecoratedChatCompletionAgent(ChatCompletionAgent):
    pass

def get_agent(kernel, settings):
    current_time = datetime.now().isoformat()
    agent = DecoratedChatCompletionAgent(
        kernel=kernel,
        name="SampleAssistantAgent",
        instructions=f"""
            You are an agent designed to query and retrieve information from a single GitHub repository in a read-only
            manner.
            You are also able to access the profile of the active user.

            Use the current date and time to provide up-to-date details or time-sensitive responses.

            The repository you are querying is a public repository with the following name: microsoft/semantic-kernel

            The current date and time is: {current_time}.
            """,
        arguments=KernelArguments(settings=settings),
    )
    return agent

@graph(name="github_agent_graph")
def get_graph():
    return ["github_agent"]

async def main():
    kernel = Kernel()

    # Add the AzureChatCompletion AI Service to the Kernel
    service_id = "agent"
    kernel.add_service(OpenAIChatCompletion(api_key=os.environ["OPENAI_API_KEY"], ai_model_id="gpt-4o-mini", service_id=service_id))

    settings = kernel.get_prompt_execution_settings_from_service_id(service_id=service_id)
    # Configure the function choice behavior to auto invoke kernel functions
    settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

    # Set your GitHub Personal Access Token (PAT) value here
    gh_settings = GitHubSettings(token=os.getenv("GITHUB_ACCESS_TOKEN"))  # nosec
    kernel.add_plugin(plugin=GitHubPlugin(gh_settings), plugin_name="GithubPlugin")

    thread: ChatHistoryAgentThread = None
    is_complete: bool = False
    while not is_complete:
        user_input = input("User:> ")
        if not user_input:
            continue

        if user_input.lower() == "exit":
            is_complete = True
            break

        arguments = KernelArguments(now=datetime.now().strftime("%Y-%m-%d %H:%M"))

        session_start()

        get_graph()
        # Create the agent
        agent = get_agent(kernel, settings)  # called here after session_start() so that each session is traced correctly

        async for response in agent.invoke(messages=user_input, thread=thread, arguments=arguments):
            print(f"{response.content}")
            thread = response.thread


if __name__ == "__main__":
    asyncio.run(main())