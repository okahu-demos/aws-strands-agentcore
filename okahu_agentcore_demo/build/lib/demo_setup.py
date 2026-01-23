
# Verify pre-requisites
## Okahu API Key

# setup .bedrock_agentcore.yaml
# Okahu setup
# agentcore deploy
# test agent
# Okahu discovery
import os
import logging
from pathlib import Path
from okahu_api import OkahuAPI
from bedrock_agentcore_starter_toolkit.cli.cli import main as agentcore_main

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
WORKFLOW_NAME = 'aws_agentcore_strands_travel_agent'
APP_NAME = "Agentcore Travel Agent"

def setup_okahu():
    api_key = os.getenv("OKAHU_API_KEY")
    if not api_key:
        raise ValueError("OKAHU_API_KEY environment variable is not set.")
    okahu_api = OkahuAPI(api_key=api_key)
    workflow = okahu_api.create_workflow(name=WORKFLOW_NAME, description="Agentcore travel agent workflow")
    logger.info("Created Okahu Workflow: %s", WORKFLOW_NAME)
    app = okahu_api.create_app(app_name=APP_NAME, description="Agentcore travel agent app", components=[WORKFLOW_NAME])
    logger.info("Created Okahu App: %s", APP_NAME)

def setup_agentcore_config():
    #get path of bedrock_agentcore_template.yaml in the parent directory
    parent = Path(__file__).parent.parent
    src = parent / 'bedrock_agentcore_template.yaml'
    dest = parent / '.bedrock_agentcore.yaml'
    # open the template file and replace <PATH> with the actual path of the parent directory
    actual_path = str(parent.absolute())

    # replace <PATH> in .bedrock_agentcore.yaml with actual path
    with open(src.absolute(), 'r') as file:
        content = file.read()
    content = content.replace('<REPO_PATH>', actual_path)
    with open(dest.absolute(), 'w') as file:
        file.write(content)
    logger.info("Copied bedrock_agentcore_template.yaml to .bedrock_agentcore.yaml")

def deploy_agentcore():
    # invoke agentcore_main with argument deploy to setup agentcore
    base_args =['deploy', '--env' , '{OKAHU_API_KEY=' + os.getenv("OKAHU_API_KEY") + '}', '--env', '{MONOCLE_EXPORT=okahu}']
    if os.getenv("OKAHU_INGESTION_ENDPOINT"):
        base_args.extend(['--env', '{MONOCLE_INGESTION_ENDPOINT=' + os.getenv("OKAHU_INGESTION_ENDPOINT") + '}'])
    agentcore_main(args=base_args)

def run_agent_test():
    pass

def okahu_discovery():
    # invoke agentcore_main with argument discover to setup okahu discovery
    api_key = os.getenv("OKAHU_API_KEY")
    if not api_key:
        raise ValueError("OKAHU_API_KEY environment variable is not set.")
    okahu_api = OkahuAPI(api_key=api_key)
    discovery_response = okahu_api.app_discover(app_name=APP_NAME)
    logger.info("Triggered Okahu Discovery for App: %s", APP_NAME)

if __name__ == "__main__":
    setup_agentcore_config()