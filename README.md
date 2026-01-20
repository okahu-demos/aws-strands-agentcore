# AWS Strands agent 
Agent example to provide travel booking implemented with AWS Strands

## Pre-requesits
- A Sagemaker resource with the large language deployed. This example is tested with Claud Sonnet 4. If you don't have a resource the process of creating one is documented in AWS resource [deployment guide](https://docs.aws.amazon.com/sagemaker/latest/dg/how-it-works-deployment.html)
- Sagemaker configuration details
  - AWS credentials- This value can be obtained by running AWS CLI commend aws sts get-session-token
  - Sagemaker API Endpoint - This value can be found in the configuration section of Sagemaker in AWS portal.

## Setup environment to run the agent
- Copy env.template to .env
- Set the AWS credentials and sagemaker end point values in .env
- Install python dependencies
  - ` pip install -r requirements.txt
- Run the demo app
  - `python travel_agent.py
  - When prompted for questions, ask travel booking questions
    - `Book a flight from San Jose to Seattle for 20 Jan 2026`
    - `Book a room at Seattle airport Hyatt on 20 Jan 2026 for two nights`

## Debug the agent with Monocle
[Monocle](monocle2ai.org) is a GenAI-native community driven open source project created to simplify instrumentation of AI apps so app developers can built high impact, safe and reliable AI apps.

### Install Monocle
`pip install monocle_apptrace`
You can generate monocle telemetry by using the monocle_apptrace module in python command line (no code change) or enable monocle tracing by just calling one API in app code

### Run agent app with monocle with no code change
`python -m monocle_apptrace travel_agent.py`

### Run agent app with monocle with a simple code change
```python
from monocle_apptrace import setup_monocle_telemetry
setup_monocle_telemetry(workflow_name = 'aws_strands_travel_agent')
```
from datetime import datetime, timedelta

## Visualize the telemetry to understand the agent execution
- Install extension `Okahu Trace Visualizer` from marketplace for VSCode or Cursor
- This will add the extension [icon](media/okahu-favicon.png) in the list of extension (left pane for VSCode or extension dropdown in Cursor).
- Click on the extension icon. It'll open a new pane on left that will list the traces for each agent turn in the descending order of execution time.
- When you click on any of the trace list, it will open a new windows with the trace visualization.
