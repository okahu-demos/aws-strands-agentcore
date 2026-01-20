
import pytest 
import logging
from travel_agent import get_scores
from monocle_test_tools import TraceAssertion
import os
@pytest.mark.asyncio
async def test_tool_invocation(monocle_trace_asserter:TraceAssertion):
    """Test that the correct tool is invoked and returns expected output."""
    get_scores("Book flight from San Jose to Seattle for 22 Nov 2025")

    monocle_trace_asserter.called_tool("book_flight_tool").contains_input("San Jose").contains_input("Seattle")
    monocle_trace_asserter.called_agent("agc_travel_agent").contains_output("San Jose").contains_output("Seattle")

if __name__ == "__main__":
    pytest.main([__file__]) 
