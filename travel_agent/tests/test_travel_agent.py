"""Test the travel agent running locally, in this process.

`test_agentcore_travel_agent.py` makes the same kind of assertions against the
agent deployed to AgentCore, where the spans are produced inside AWS instead.
"""
import sys
import os
# Include parent folder for agent module
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

import pytest
from travel_agent import get_scores
from monocle_test_tools import TraceAssertion

@pytest.mark.asyncio
async def test_tool_invocation(monocle_trace_asserter:TraceAssertion):
    """Test that the correct tool is invoked and returns expected output."""
    get_scores("Book flight from San Jose to Seattle for 22 june 2026")

    monocle_trace_asserter.called_tool("book_flight_tool").contains_input("San Jose").contains_input("Seattle")
    monocle_trace_asserter.called_agent("agc_travel_agent").contains_output("San Jose").contains_output("Seattle")


@pytest.mark.asyncio
async def test_hotel_tool_invocation(monocle_trace_asserter:TraceAssertion):
    """The agent's second tool, so the suite does not only cover flights."""
    get_scores("Book me 3 nights at the Fairmont Olympic starting 22 june 2026")

    monocle_trace_asserter.called_tool("book_hotel_tool").contains_input("Fairmont Olympic")
    monocle_trace_asserter.called_agent("agc_travel_agent").contains_output("Fairmont Olympic")


@pytest.mark.asyncio
async def test_off_topic_request_is_refused(monocle_trace_asserter:TraceAssertion):
    """The system prompt limits the agent to travel booking.

    `called_agent` is asserted first: it proves spans were collected, which is
    what makes the two `does_not_call_tool` assertions meaningful. Without it
    they would also pass on an empty trace.
    """
    response = get_scores("What is the capital of France?")

    assert "sorry" in response.lower(), f"expected a refusal, got: {response!r}"
    monocle_trace_asserter.called_agent("agc_travel_agent")
    monocle_trace_asserter.does_not_call_tool("book_flight_tool")
    monocle_trace_asserter.does_not_call_tool("book_hotel_tool")


if __name__ == "__main__":
    pytest.main([__file__])
