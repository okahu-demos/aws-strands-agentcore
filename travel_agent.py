from datetime import datetime, timedelta
import json
import os
import time
from uuid import UUID
import dotenv
from strands_tools.code_interpreter import AgentCoreCodeInterpreter

from strands import tool
from strands.models.bedrock import BedrockModel
from strands.session.file_session_manager import FileSessionManager
import boto3
from strands import Agent
#Enable Monocle Tracing
from monocle_apptrace import setup_monocle_telemetry


@tool
def book_flight_tool(from_airport: str, to_airport: str, date:str):
    """
    Args:
        from_airport: Airport name or code for the from airport
        to_airport: Airport name or code for the destination airport
        date: Date for the start of travel
    """
    return f"Successfully booked a flight from {from_airport} to {to_airport}."

@tool
def book_hotel_tool(hotel_name:str, start_date:str, number_of_nights:str):
    """
    Args:
        hotel_name: name of the hotel
        start_date: date of reservation
        number_of_night: Number of nights to book the room
    """
    return f"Successfully booked a stay at {hotel_name}."

def setup_agents(session_manager = None, session_id= None) -> Agent:
    boto_session = boto3.Session()
    model = BedrockModel(boto_session=boto_session, streaming=False)

    # Create code interpreter
    code_interpreter = AgentCoreCodeInterpreter(
        session_name=session_id,
        auto_create=True,
        persist_sessions=True
    )

    travel_agent = Agent(name="agc_travel_agent", model=model,
                system_prompt= """
                    You are a travel booking agent. You handle flight and hotel booking requests from user. 
                    If anything else is asked then just say 'sorry I can't help with that'
                    """,
                    tools = [code_interpreter, book_flight_tool, book_hotel_tool],
                    description="Travel agent", callback_handler=None,
                    session_manager=session_manager
                )
    return travel_agent

def get_scores(message: str):
    travel_agent = setup_agents()
    response = travel_agent(message)
    return response.message['content'][0]['text']

if __name__ == "__main__":
    dotenv.load_dotenv()
    setup_monocle_telemetry(workflow_name = 'aws_strands_travel_agent')
    nba_agent = setup_agents()
    while True:
        try:
            user_request = input("\nHey, How can I help you with travel booking? ")
        except EOFError:
            user_request = "exit"
        if user_request.lower() in ["exit", "quit", ""]:
            print("Exiting the Travel scores agent. Goodbye!")
            break
        response = nba_agent(prompt=user_request)
        #get list of all environment variables
        envs:str = ""


        print(response.message['content'][0]['text'] + envs)