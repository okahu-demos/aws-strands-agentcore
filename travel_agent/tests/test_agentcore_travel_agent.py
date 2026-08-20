"""Test the travel agent that is deployed in AWS AgentCore.

Nothing here imports the agent. The test only has its AgentCore ARN, and sends
prompts to it over the AWS API -- so the agent runs inside AWS, and the traces of
what it did are produced there too, by its own Monocle instrumentation.

The test still gets those traces. Every call is sent with a session id. The
deployed agent stamps that id on every span it produces, and Monocle looks the
spans up by it and loads them into this test. That is why the assertions below
read the same as the ones in test_travel_agent.py, which runs the agent locally.

Needs AGENTCORE_RUNTIME_URL (the deployed agent's ARN) and OKAHU_API_KEY (the key
of the tenant that agent sends its traces to). Without the ARN, these tests skip.
"""
import os
import uuid

import pytest
from dotenv import load_dotenv

from monocle_test_tools import TraceAssertion

load_dotenv()

AGENTCORE_RUNTIME_URL = os.getenv("AGENTCORE_RUNTIME_URL")

# The name the deployed agent reports its traces under: travel_agent.py passes it
# to setup_monocle_telemetry, and Monocle needs it to find that agent's traces.
# It belongs to this demo rather than to your machine, so it is set here instead
# of being asked for in .env.
os.environ.setdefault("AGENTCORE_TRACE_WORKFLOW", "aws_agentcore_strands_travel_agent")

# A checkout without a deployment has nothing to test against, so skip rather
# than fail against someone else's runtime.
pytestmark = pytest.mark.skipif(
    not AGENTCORE_RUNTIME_URL,
    reason="AGENTCORE_RUNTIME_URL is not set; run okahu_agentcore_demo_setup to deploy the agent.",
)


def _session_id() -> str:
    """A new session id for one test.

    AgentCore requires at least 33 characters, which the prefix plus a uuid4 hex
    gives. A fresh one per test keeps each test's traces separate.
    """
    return f"travel_agent_test_{uuid.uuid4().hex}"


def test_deployed_agent_books_a_flight(monocle_trace_asserter: TraceAssertion):
    """The deployed agent answers the booking request."""
    response = monocle_trace_asserter.run_agent(
        AGENTCORE_RUNTIME_URL,
        "agentcore",
        "Book a flight from San Jose to Seattle for 22 Nov 2026",
        session_id=_session_id(),
    )

    assert "San Jose" in response
    assert "Seattle" in response


def test_deployed_agent_invokes_the_flight_tool(monocle_trace_asserter: TraceAssertion):
    """The same assertions as the local test, on traces made inside AWS."""
    session_id = _session_id()

    monocle_trace_asserter.run_agent(
        AGENTCORE_RUNTIME_URL,
        "agentcore",
        "Book a flight from San Jose to Seattle for 22 Nov 2026",
        session_id=session_id,
    )

    monocle_trace_asserter.called_tool("book_flight_tool").contains_input("San Jose").contains_input("Seattle")
    monocle_trace_asserter.called_agent("agc_travel_agent").contains_output("San Jose").contains_output("Seattle")
    # The traces carry the session this test invoked with. Worth asserting even
    # though the lookup used that id: when the agent returns its traces in the
    # response instead (MONOCLE_ENABLE_TRACE_RETURN), nothing filters by session,
    # and this is the only check that the agent recorded the right one.
    monocle_trace_asserter.has_scope("agentic.session", session_id)


def test_deployed_agent_books_a_hotel(monocle_trace_asserter: TraceAssertion):
    """The agent's other tool, so the test does not only cover flights."""
    monocle_trace_asserter.run_agent(
        AGENTCORE_RUNTIME_URL,
        "agentcore",
        "Book me 3 nights at the Fairmont Olympic starting 22 Nov 2026",
        session_id=_session_id(),
    )

    monocle_trace_asserter.called_tool("book_hotel_tool")
    monocle_trace_asserter.called_agent("agc_travel_agent")


def test_deployed_agent_refuses_off_topic(monocle_trace_asserter: TraceAssertion):
    """The system prompt limits the deployed agent to travel booking too.

    called_agent comes first on purpose: if no traces had been loaded, "this tool
    was not called" would pass for the wrong reason.
    """
    response = monocle_trace_asserter.run_agent(
        AGENTCORE_RUNTIME_URL,
        "agentcore",
        "What is the capital of France?",
        session_id=_session_id(),
    )

    assert "sorry" in response.lower(), f"expected a refusal, got: {response!r}"
    monocle_trace_asserter.called_agent("agc_travel_agent")
    monocle_trace_asserter.does_not_call_tool("book_flight_tool")
    monocle_trace_asserter.does_not_call_tool("book_hotel_tool")


def test_deployed_agent_carries_context_across_turns(monocle_trace_asserter: TraceAssertion):
    """Two turns on one session, which only the deployed agent can answer.

    The second turn never says the date -- it says "the same day as my flight" --
    so booking it at all means the agent remembered the first turn. Reusing the
    session id is what ties the two turns together in AWS.

    The hotel is named because book_hotel_tool needs a name: asked for "a hotel
    there", the agent sensibly asks which one and calls no tool, which would make
    this a test of the prompt rather than of session memory.
    """
    session_id = _session_id()

    monocle_trace_asserter.run_agent(
        AGENTCORE_RUNTIME_URL,
        "agentcore",
        "Book a flight from Boston to Denver on 4 July 2026",
        session_id=session_id,
    )
    response = monocle_trace_asserter.run_agent(
        AGENTCORE_RUNTIME_URL,
        "agentcore",
        "Book me 3 nights at the Brown Palace starting the same day as my flight",
        session_id=session_id,
    )

    assert "Brown Palace" in response, f"hotel was not booked: {response!r}"
    # The date could only have come from the first turn.
    assert "July" in response, f"session context was not carried over: {response!r}"
    monocle_trace_asserter.called_tool("book_hotel_tool").contains_input("Brown Palace")
    monocle_trace_asserter.has_scope("agentic.session", session_id)


if __name__ == "__main__":
    pytest.main([__file__])
