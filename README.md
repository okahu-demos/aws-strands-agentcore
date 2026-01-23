# AWS Strands agent in AWS Agentcore
This demo includes a mock travel agent that accepts flight and travel booking requests. The agent code is implemented using AWS Strands agentic framework. The demo scripts helps you to deploy this agent in AWS Agentcore service. The agent is enabled to generate [Monocle](monocle2ai.org) traces and send those to [Okahu cloud](www.okahu.ai).

## Pre-requesits
- AWS [Bedrock] with LLM deployed (https://docs.aws.amazon.com/bedrock/latest/userguide/getting-started.html).
- AWS [Agentcore](https://aws.amazon.com/bedrock/agentcore/) enabled for you tenant.
  - Please chyeck to AWS portal and documentation to confirm that the service is available for your tenant and the region.
- AWS credentials configured locally.
  - Run `aws sts get-caller-identity` to check if you already have configured AWS credentials for AWS CLI tools
    - The output of that command should show Userid if the auth is configured.
  - If not then, these value can be obtained by running AWS CLI commend `aws sts get-session-token` or `aws login`. Please refer to these [AWS CLI configuration steps](https://docs.aws.amazon.com/cli/v1/userguide/cli-configure-files.html).
- Okahu cloud account
  - Sign up for Okahu on portal.okahu.co to get limited capacity single user account for free.
- Okahu API key
  - Login to portal.okahu.co
  - goto https://portal.okahu.co/settings
  - Generate API key and copy it

## Setup demo environment
- Install dependencies in your python environment
  - `pip install -r requirements.txt`
- Run Okahu demo setup tool. This will deploy demo agent to AWS Agentcore and setup Okahu tenant for consuming traces from that deployment.
  - ```okahu_agentcore_demo_setup --key <OKAHU-API-KEY>```
  - Verify that you see `Demo setup completed successfully` at the end

## Test the agent

### Test in Agentcore Sandbox in cloud
- Goto Agentcore [Sandbox](https://us-east-1.console.aws.amazon.com/bedrock-agentcore/playground)
- Enter the test prompt in the `Input` field - `Book a flight from San Jose to Seattle for 30 March 2026`
  - ![Bedrock Sandbox](media/agentcore_playground.png)
### Test locally using Agentcore CLI tool
- Start command shell and source python env
- Run Agentcore CLI command
  - `agentcore invoke '{"prompt": "<prompt>"}'`

## View agent traces in Okahu
- Login to [Okahu portal](portal.okahu.co)
- Click on the `AgentCore Travel Agent` application tab
- Click on the `Traces` tab
- From the `Breakdown` dropdown list, select `GenAI` and then click on search
  - ![GenAI traces](media/genai_search.png)
- View the traces
  - ![Traces ](media/traces.png)

## Try out tests framework example for the travel agent app
- Source python env
- Install python dependencies
  - `pip install -r test/requirements.txt`
- Run pytest
  - `pytest -vv test/test_travel_agent.py

## Visualize the telemetry to understand the agent execution
- Install extension `Okahu Trace Visualizer` from marketplace for your Kiro IDE (or VSCode, Cursor, Antigravity)
- This will add the Okahu extension in the list of extension (left pane for VSCode or extension dropdown in Cursor).
- Click on the extension icon. It'll open a new pane on left that will list the traces for each agent turn in the descending order of execution time.
- When you click on any of the trace list, it will open a new windows with the trace visualization.
