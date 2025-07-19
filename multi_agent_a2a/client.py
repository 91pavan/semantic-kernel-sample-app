import os
import uuid
import httpx
import asyncio
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import (
    AgentCard,
    Message,
    MessageSendParams,
    Part,
    Role,
    SendMessageRequest,
    TextPart,
)

from ioa_observe.sdk import Observe
from ioa_observe.sdk.decorators import graph
from ioa_observe.sdk.instrumentations.a2a import A2AInstrumentor
from ioa_observe.sdk.tracing import session_start

PUBLIC_AGENT_CARD_PATH = "/.well-known/agent.json"
LIGHTS_BASE_URL = "http://localhost:8001"
GITHUB_BASE_URL = "http://localhost:8002"

Observe.init(
    "multi-agent-client", api_endpoint=os.getenv("OTLP_HTTP_ENDPOINT")
)

A2AInstrumentor().instrument()


@graph(name="get_agents")
def get_agents() -> list:
    """Returns a list of agents that we can register with ioa_observe SDK.
    We have three agents:
    - multi-agent-client: The client that sends requests to the servers.
    - multi-agent-lights-server: The server for lights control.
    - multi-agent-github-server: The server for GitHub operations.
    """
    return ["multi-agent-client", "multi-agent-lights-server", "multi-agent-github-server"]


async def get_agent_info(base_url: str, agent_name: str) -> tuple[A2AClient, AgentCard]:
    """Get agent information and create a client"""
    async with httpx.AsyncClient() as httpx_client:
        # Fetch the agent card
        resolver = A2ACardResolver(httpx_client=httpx_client, base_url=base_url)
        try:
            print(f"Fetching {agent_name} agent card from: {base_url}{PUBLIC_AGENT_CARD_PATH}")
            agent_card: AgentCard = await resolver.get_agent_card()
            print(f"{agent_name} agent card fetched successfully:")
            print(f"  Name: {agent_card.name}")
            print(f"  Description: {agent_card.description}")
            print(f"  Skills: {len(agent_card.skills)} available")
            
            # Initialize A2A client with the agent card
            client = A2AClient(httpx_client=httpx_client, agent_card=agent_card)
            return client, agent_card
            
        except Exception as e:
            print(f"Error fetching {agent_name} agent card: {e}")
            return None, None


async def send_message_to_agent(client: A2AClient, message_text: str, agent_name: str):
    """Send a message to a specific agent"""
    try:
        # Build message
        message_payload = Message(
            role=Role.user,
            messageId=str(uuid.uuid4()),
            parts=[Part(root=TextPart(text=message_text))],
        )
        request = SendMessageRequest(
            id=str(uuid.uuid4()),
            params=MessageSendParams(message=message_payload),
        )

        # Send message
        print(f"\nSending message to {agent_name}: '{message_text}'")
        response = await client.send_message(request)

        # Print response
        print(f"{agent_name} Response:")
        
        # First, let's see the full response structure for debugging
        response_dict = response.model_dump()
        
        # Try to extract the message content
        message_found = False
        
        # Check for different possible response structures
        if hasattr(response, 'message') and response.message:
            if hasattr(response.message, 'parts') and response.message.parts:
                for part in response.message.parts:
                    if hasattr(part, 'root') and hasattr(part.root, 'text'):
                        print(f"  {part.root.text}")
                        message_found = True
        
        # If we have a result field
        if hasattr(response, 'result') and response.result:
            if hasattr(response.result, 'message') and response.result.message:
                if hasattr(response.result.message, 'parts') and response.result.message.parts:
                    for part in response.result.message.parts:
                        if hasattr(part, 'root') and hasattr(part.root, 'text'):
                            print(f"  {part.root.text}")
                            message_found = True
        
        # If we have events
        if hasattr(response, 'events') and response.events:
            for event in response.events:
                if hasattr(event, 'message') and event.message:
                    if hasattr(event.message, 'parts') and event.message.parts:
                        for part in event.message.parts:
                            if hasattr(part, 'root') and hasattr(part.root, 'text'):
                                print(f"  {part.root.text}")
                                message_found = True
        
        # If we couldn't extract a message, show the full response for debugging
        if not message_found:
            print("  [Full Response for debugging]:")
            print(f"  {response.model_dump_json(indent=4)}")
            
    except Exception as e:
        print(f"Error sending message to {agent_name}: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()


async def interactive_mode():
    """Run an interactive session where users can choose which agent to talk to"""
    print("\n=== Multi-Agent A2A System ===")
    print("Available agents:")
    print("1. Lights Agent - Control smart lights")
    print("2. GitHub Agent - Query GitHub repositories")
    print("3. Exit")
    
    # Initialize agents
    lights_client, lights_card = await get_agent_info(LIGHTS_BASE_URL, "Lights")
    github_client, github_card = await get_agent_info(GITHUB_BASE_URL, "GitHub")
    
    if not lights_client or not github_client:
        print("Failed to initialize one or more agents. Please ensure both servers are running.")
        return

    session_start()
    get_agents()  # Register agents with observability

    while True:
        try:
            print("\n" + "="*50)
            choice = input("Choose an agent (1-3): ").strip()
            
            if choice == "3":
                print("Goodbye!")
                break
            elif choice == "1":
                message = input("Message for Lights Agent: ").strip()
                if message:
                    async with httpx.AsyncClient() as httpx_client:
                        client = A2AClient(httpx_client=httpx_client, agent_card=lights_card)
                        await send_message_to_agent(client, message, "Lights Agent")
            elif choice == "2":
                message = input("Message for GitHub Agent: ").strip()
                if message:
                    async with httpx.AsyncClient() as httpx_client:
                        client = A2AClient(httpx_client=httpx_client, agent_card=github_card)
                        await send_message_to_agent(client, message, "GitHub Agent")
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
        except EOFError:
            print("\nReceived EOF. Exiting...")
            break
        except KeyboardInterrupt:
            print("\nReceived interrupt. Exiting...")
            break


async def demo_mode():
    """Run a demo with predefined messages to both agents"""
    print("\n=== Multi-Agent A2A Demo ===")
    
    # Initialize agents
    lights_client, lights_card = await get_agent_info(LIGHTS_BASE_URL, "Lights")
    github_client, github_card = await get_agent_info(GITHUB_BASE_URL, "GitHub")
    
    if not lights_client or not github_client:
        print("Failed to initialize one or more agents. Please ensure both servers are running.")
        return

    session_start()
    get_agents()  # Register agents with observability

    # Demo messages
    demo_messages = [
        ("Lights Agent", lights_card, "Show me all the lights and their current state"),
        ("Lights Agent", lights_card, "Turn on the table lamp"),
        ("GitHub Agent", github_card, "Get my GitHub user profile"),
        ("GitHub Agent", github_card, "Show me open issues in microsoft/semantic-kernel repository"),
        ("Lights Agent", lights_card, "Turn off all lights"),
    ]

    for agent_name, agent_card, message in demo_messages:
        async with httpx.AsyncClient() as httpx_client:
            client = A2AClient(httpx_client=httpx_client, agent_card=agent_card)
            await send_message_to_agent(client, message, agent_name)
            await asyncio.sleep(2)  # Small delay between messages


async def main():
    """Main function to choose between demo and interactive mode"""
    import sys
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode == "demo":
            await demo_mode()
            return
        elif mode == "interactive":
            await interactive_mode()
            return
    
    # Default interactive menu
    print("Multi-Agent A2A System")
    print("1. Demo mode (predefined messages)")
    print("2. Interactive mode")
    
    try:
        choice = input("Choose mode (1-2): ").strip()
        
        if choice == "1":
            await demo_mode()
        elif choice == "2":
            await interactive_mode()
        else:
            print("Invalid choice. Running demo mode...")
            await demo_mode()
    except (EOFError, KeyboardInterrupt):
        print("\nExiting...")
        return


if __name__ == "__main__":
    asyncio.run(main())
