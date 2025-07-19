# semantic-kernel-sample-app

Sample demo app using Microsoft Semantic Kernel with OpenAI and Observe SDK.

## Installation

1. **Install Python 3.10 or higher**
   Make sure you have Python 3.10+ installed.

2. **Install dependencies**
   Run the following command::
   ```bash
   pip install .
   ```

## Environment Variables

Set the following environment variables before running the scripts:
- `OPENAI_API_KEY` – Your OpenAI API key.
- `GITHUB_ACCESS_TOKEN` – Your GitHub personal access token (for `github_agent.py`).
- `OTLP_HTTP_ENDPOINT` – The endpoint for Observe SDK.

Example (Unix/macOS):
```bash
export OPENAI_API_KEY=your_openai_key
export GITHUB_ACCESS_TOKEN=your_github_token
export OTLP_HTTP_ENDPOINT=https://your-otel-collector-http-endpoint
```

## Running the Scripts

### 1. Multi-Agent A2A System

To run the multi-agent system, navigate to the `multi_agent_a2a` directory and use the launcher script:
```bash
cd multi_agent_a2a
python launcher.py
```

### 2. Code Interpreter Agent

To run the code interpreter agent:
```bash
python code_interpreter.py
```

### 3. GitHub Agent

To run the GitHub agent:
```bash
python github_agent.py
```

---
