import os
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from lights_agent_executor import LightsAgentExecutor

from ioa_observe.sdk import Observe
from ioa_observe.sdk.instrumentations.a2a import A2AInstrumentor

Observe.init(
    "multi-agent-lights-server", api_endpoint=os.getenv("OTLP_HTTP_ENDPOINT")
)

A2AInstrumentor().instrument()


def main():
    # Define the skill metadata for lights control
    skill = AgentSkill(
        id="lights_control",
        name="Smart Lights Controller",
        description="Controls smart lights - can get current state and turn lights on/off",
        tags=["lights", "smart-home", "control", "automation"],
        examples=[
            "Turn on the table lamp",
            "Show me all lights",
            "Turn off the porch light",
            "What lights are currently on?",
            "Switch the chandelier off"
        ],
    )

    # Define the agent metadata
    agent_card = AgentCard(
        name="Lights Control Agent",
        description="An AI agent that can control smart lights in your home. Can check light status and turn lights on or off.",
        url="http://localhost:8001/",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[skill],
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )

    # Configure the request handler with our lights agent executor
    request_handler = DefaultRequestHandler(
        agent_executor=LightsAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    # Create the A2A app server
    server = A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card,
    )

    # Run the server
    uvicorn.run(server.build(), host="0.0.0.0", port=8001)


if __name__ == "__main__":
    main()
