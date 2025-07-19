import os
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from github_agent_executor import GithubAgentExecutor

from ioa_observe.sdk import Observe
from ioa_observe.sdk.instrumentations.a2a import A2AInstrumentor

Observe.init(
    "multi-agent-github-server", api_endpoint=os.getenv("OTLP_HTTP_ENDPOINT")
)

A2AInstrumentor().instrument()


def main():
    # Define the skill metadata for GitHub operations
    skill = AgentSkill(
        id="github_operations",
        name="GitHub Repository Assistant",
        description="Queries GitHub repositories, user profiles, issues, and repository information",
        tags=["github", "repository", "issues", "development", "api"],
        examples=[
            "Get my GitHub profile",
            "Show me issues in microsoft/semantic-kernel",
            "Get repository information for microsoft/semantic-kernel",
            "Find open issues in the repository",
            "Get details about issue #123",
            "Show recent issues assigned to a specific user"
        ],
    )

    # Define the agent metadata
    agent_card = AgentCard(
        name="GitHub Assistant Agent",
        description="An AI agent that can query GitHub repositories and retrieve information about users, repositories, and issues.",
        url="http://localhost:8002/",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[skill],
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )

    # Configure the request handler with our GitHub agent executor
    request_handler = DefaultRequestHandler(
        agent_executor=GithubAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    # Create the A2A app server
    server = A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card,
    )

    # Run the server
    uvicorn.run(server.build(), host="0.0.0.0", port=8002)


if __name__ == "__main__":
    main()
