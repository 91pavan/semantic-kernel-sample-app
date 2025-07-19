# Multi-Agent A2A System

This is a multi-agent system built using the Agent-to-Agent (A2A) protocol that includes two specialized agents, and instrumented using the IOA Observe SDK for observability.

1. **Lights Agent** - Controls smart lights using Semantic Kernel and the LightsPlugin
2. **GitHub Agent** - Queries GitHub repositories using Semantic Kernel and the GitHubPlugin

## Architecture

The system follows the A2A protocol pattern:

- **Agent Executors**: Handle the core logic for each agent
- **Servers**: A2A-compliant servers that expose agent capabilities
- **Client**: A unified client that can communicate with both agents

## Prerequisites

1. **Environment Variables**:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `GITHUB_ACCESS_TOKEN`: Your GitHub Personal Access Token
   - `OTLP_HTTP_ENDPOINT`: (Optional) Observability endpoint

2. **Configuration Setup**:
   ```bash
   # Copy the example configuration
   cp .env.example .env
   
   # Edit .env with your actual API keys
   nano .env  # or use your preferred editor
   ```
## Features

### Current Capabilities ✨
- **Lights Agent**: Processes natural language commands to control smart lights
- **GitHub Agent**: Responds to specific GitHub queries and requests
- Both agents use Semantic Kernel with function calling to provide intelligent responses

### Usage Notes
The system currently works as a demonstration of A2A protocol implementation with Semantic Kernel integration. Each agent showcases its capabilities and provides examples of what it can do.

## Running the System

### Quick Start (Recommended)

Install the required dependencies and set up your environment:

```bash
cd semantic-kernel-app
uv venv
source venv/bin/activate 
# Install dependencies
uv sync
```

Use the launcher script for easy setup:

```bash
cd multi_agent_a2a
python launcher.py
```

The launcher offers several options:
1. Start both servers and run demo
2. Start both servers and run interactive client  
3. Start only lights server
4. Start only GitHub server
5. Run client only (servers must be running)

### Manual Setup

Install the required dependencies and set up your environment:

```bash
cd semantic-kernel-app
uv venv
source venv/bin/activate 
# Install dependencies
uv sync
```

Then, follow these steps to run the agents:

#### Step 1: Start the Lights Agent Server

```bash
cd multi_agent_a2a
python lights_server.py
```

The lights agent will be available at `http://localhost:8001`

#### Step 2: Start the GitHub Agent Server (in a new terminal)

```bash
cd multi_agent_a2a
python github_server.py
```

The GitHub agent will be available at `http://localhost:8002`

#### Step 3: Run the Client (in a new terminal)

```bash
cd multi_agent_a2a
python client.py
```

The client offers two modes:
- **Demo mode**: Runs predefined messages to showcase both agents
- **Interactive mode**: Allows you to choose which agent to talk to and send custom messages

## Agent Capabilities

### Lights Agent
- Get current state of all lights
- Turn specific lights on/off
- Control individual lights by ID or name
- Available lights:
  - Table Lamp (ID: 1)
  - Porch light (ID: 2)  
  - Chandelier (ID: 3)

Example messages:
- "Show me all lights"
- "Turn on the table lamp"
- "Turn off the porch light"
- "What lights are currently on?"

### GitHub Agent
- Get user profile information
- Query repository details
- List issues in repositories
- Get specific issue details
- Default repository: microsoft/semantic-kernel

Example messages:
- "Get my GitHub profile"
- "Show me issues in microsoft/semantic-kernel"
- "Get repository information for microsoft/semantic-kernel"
- "Find open issues in the repository"

## A2A Protocol Features

Each agent server exposes:
- Agent card metadata at `/.well-known/agent.json`
- Skills and capabilities information
- Standardized message handling
- Observability integration

## Observability

The system includes observability features using the IOA Observe SDK:
- Agent execution tracing
- Request/response monitoring
- Performance metrics
