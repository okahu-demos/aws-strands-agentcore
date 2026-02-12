import os
import json
import boto3
import uuid
from typing import Dict, Any, Optional
import dotenv
dotenv.load_dotenv()

class AgentCoreClient:

    def __init__(self, runtime_url: Optional[str] = None, session_id: Optional[str] = None,
                 region: Optional[str] = None):
        """
        Initialize the AgentCore client
        Args:
            runtime_url: The runtime ARN for the AgentCore app (defaults to env var AGENTCORE_RUNTIME_URL)
            session_id: Optional session ID for maintaining conversation context (must be at least 33 chars)
            region: AWS region (defaults to env var AWS_REGION or us-east-1)
        """
        self.runtime_url = runtime_url or os.getenv("AGENTCORE_RUNTIME_URL")
        self.session_id = session_id or f"session-{str(uuid.uuid4())}"
        self.region = region or os.getenv("AWS_REGION", "us-east-1")

        if not self.runtime_url:
            raise ValueError(
                "AGENTCORE_RUNTIME_URL must be set in environment or passed as parameter"
            )

        # Parse the ARN to extract runtime ARN and qualifier
        self.runtime_arn, self.qualifier = self._parse_runtime_arn()

        # Initialize boto3 client for bedrock-agentcore
        self.client = boto3.client('bedrock-agentcore', region_name=self.region)

    def _parse_runtime_arn(self):
        """
        Parse the runtime URL to extract runtime ARN and qualifier
        ARN format: arn:aws:bedrock-agentcore:region:account:runtime/agent-id/runtime-endpoint/DEFAULT
        Returns: (runtime_arn, qualifier)
        """
        if '/runtime-endpoint/' in self.runtime_url:
            parts = self.runtime_url.split('/runtime-endpoint/')
            runtime_arn = parts[0]  # Everything before /runtime-endpoint/
            qualifier = parts[1] if len(parts) > 1 else 'DEFAULT'  # Everything after
            return runtime_arn, qualifier
        else:
            return self.runtime_url, 'DEFAULT'

    def invoke(self, prompt: str, session_id: Optional[str] = None) -> str:
        """
        Invoke the AgentCore agent with a prompt
        Args:
            prompt: The user's travel booking request
            session_id: Optional session ID to override the default
        Returns:
            The agent's response text
        """
        sid = session_id or self.session_id
        payload = {
            "prompt": prompt
        }
        try:
            response = self.client.invoke_agent_runtime(
                agentRuntimeArn=self.runtime_arn,
                qualifier=self.qualifier,
                runtimeSessionId=sid,
                payload=json.dumps(payload).encode('utf-8')
            )

            # Parse the response
            if 'response' in response:
                return response['response']._raw_stream.data

            # If no payload, return full response for debugging
            return f"Unexpected response format: {json.dumps(response, default=str, indent=2)}"

        except Exception as e:
            import traceback
            return f"Error invoking AgentCore app: {str(e)}\n{traceback.format_exc()}"

def main():

    client = AgentCoreClient()
    print("AWS AgentCore Agent Client")
    print("=" * 50)
    print(f"Connected to: {client.runtime_url}")
    print(f"Session ID: {client.session_id}")
    print("=" * 50)
    
    while True:
        try:
            user_input = input("\nWhat can I help you with today? (or 'exit' to quit): ")
        except EOFError:
            break

        if user_input.lower() in ["exit", "quit", ""]:
            print("Goodbye!")
            break

        print("\nProcessing your request...")
        response = client.invoke(user_input)
        print(f"\nAgent: {response}")

if __name__ == "__main__":
    main()