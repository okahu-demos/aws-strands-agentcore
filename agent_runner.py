from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig, RetrievalConfig
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager
from bedrock_agentcore.runtime import BedrockAgentCoreApp
#from travel_agent import setup_agents
from nba_agent import setup_agents
import os
import logging

app = BedrockAgentCoreApp()
log = app.logger
MEMORY_ID = os.getenv("BEDROCK_AGENTCORE_MEMORY_ID")
REGION = os.getenv("AWS_REGION")
from monocle_apptrace import setup_monocle_telemetry
setup_monocle_telemetry(workflow_name = 'agc_travel_agent_wf')

@app.entrypoint
async def invoke(payload, context):
    session_id:str = getattr(context, 'session_id')
    if MEMORY_ID and session_id:
        session_manager = AgentCoreMemorySessionManager(
            AgentCoreMemoryConfig(
                memory_id=MEMORY_ID,
                session_id=session_id,
                actor_id="okahu",
            ),
            region_name = REGION
        )
    else:
        session_manager = None
    agent = setup_agents(session_manager=session_manager, session_id=session_id)
    response = agent(payload.get("prompt"))
    return response.message['content'][0]['text']

if __name__ == "__main__":
    app.run()