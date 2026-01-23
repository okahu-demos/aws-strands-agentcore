import os
import logging
from pathlib import Path
import sys

from requests import HTTPError
from .okahu_api import OkahuAPI
from bedrock_agentcore_starter_toolkit.cli.cli import main as agentcore_main

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
WORKFLOW_NAME = 'aws_agentcore_strands_travel_agent'
APP_NAME = "Agentcore Travel Agent"
TEST_PROMPT_1 = "Book a flight from New York to San Francisco on 25th Dec 2026"
TEST_PROMPT_2 = "Book a hotel stay at San Francisco Hilton for 3 nights for the same dates"

def setup_okahu():
    api_key = os.getenv("OKAHU_API_KEY")
    if not api_key:
        raise ValueError("OKAHU_API_KEY environment variable is not set.")
    okahu_api = OkahuAPI(api_key=api_key)
    try:
        workflow = okahu_api.create_workflow(name=WORKFLOW_NAME, description="Agentcore travel agent workflow")
        logger.info("Created Okahu Workflow: %s", WORKFLOW_NAME)
    except HTTPError as e:
        if e.response.status_code == 409:
            logger.info("Workflow %s already exists. Skipping creation.", WORKFLOW_NAME)
        else:
            raise
    try:
        app = okahu_api.create_app(app_name=APP_NAME, description="Agentcore travel agent app", components=[WORKFLOW_NAME])
        logger.info("Created Okahu App: %s", APP_NAME)
    except HTTPError as e:
        if e.response.status_code == 409:
            logger.info("App %s already exists. Skipping creation.", APP_NAME)
        else:
            raise

def setup_agentcore_config():

    src = 'bedrock_agentcore_template.yaml'
    dest = '.bedrock_agentcore.yaml'
    # open the template file and replace <PATH> with the actual path of the parent directory
    actual_path = str(Path('.').absolute()) + "/travel_agent"

    # replace <PATH> in .bedrock_agentcore.yaml with actual path
    with open(src, 'r') as file:
        content = file.read()
    content = content.replace('<REPO_PATH>', actual_path)
    with open(dest, 'w') as file:
        file.write(content)
    logger.info("Copied bedrock_agentcore_template.yaml to .bedrock_agentcore.yaml")

def update_dot_env():
    template = "env_template"
    dest = '.env'
    # open the .env file and replace or add OKAHU_API_KEY with the actual value from environment variable
    api_key = os.getenv("OKAHU_API_KEY")
    if not api_key:
        return
    if os.path.exists(dest):
        with open(dest, 'r') as file:
            lines = file.readlines()
    else:
        with open(template, 'r') as file:
            lines = file.readlines()

    with open(dest, 'w') as file:
        found = False
        for line in lines:
            if line.startswith('OKAHU_API_KEY='):
                file.write(f'OKAHU_API_KEY={api_key}\n')
                found = True
            else:
                file.write(line)
        if not found:
            file.write(f'OKAHU_API_KEY={api_key}\n')

def deploy_agentcore():
    # invoke agentcore_main with argument deploy to setup agentcore
    base_args =['deploy', '--auto-update-on-conflict', '--env' , 'OKAHU_API_KEY=' + os.getenv("OKAHU_API_KEY") , '--env', 'MONOCLE_EXPORTER=okahu']
    if os.getenv("OKAHU_INGESTION_ENDPOINT"):
        base_args.extend(['--env', 'OKAHU_INGESTION_ENDPOINT=' + os.getenv("OKAHU_INGESTION_ENDPOINT")])
    # invoke agentcore_main with base_args
    sys.argv = ['agentcore'] + base_args
    try:
        agentcore_main()
    except SystemExit as e:
        if e.code != 0:
            raise

def run_agent_test():
    for prompt in [TEST_PROMPT_1, TEST_PROMPT_2]:
        prompt_str = '{"prompt": "' + prompt + '"}'
        sys.argv = ['agentcore', 'invoke', prompt_str]
        try:
            agentcore_main()
        except SystemExit as e:
            if e.code != 0:
                raise

def okahu_discovery():
    # invoke agentcore_main with argument discover to setup okahu discovery
    api_key = os.getenv("OKAHU_API_KEY")
    if not api_key:
        raise ValueError("OKAHU_API_KEY environment variable is not set.")
    okahu_api:OkahuAPI = OkahuAPI(api_key=api_key)
    discovery_response = okahu_api.app_discover(app_name=APP_NAME)
    logger.info("Triggered Okahu Discovery for App: %s", APP_NAME)

def get_trace_url():
    okahu_api:OkahuAPI = OkahuAPI(api_key=os.getenv("OKAHU_API_KEY"))
    return okahu_api.get_traces_view_url(app_name=APP_NAME)

if __name__ == "__main__":
    setup_agentcore_config()