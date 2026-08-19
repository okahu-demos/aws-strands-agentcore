import sys
import os
# Include parent folder for agent module
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

import pytest 
import logging
from travel_agent import get_scores
from monocle_test_tools import TraceAssertion

@pytest.mark.asyncio
async def test_tool_invocation(monocle_trace_asserter:TraceAssertion):
    """Test that the correct tool is invoked and returns expected output."""
    get_scores("Book flight from San Jose to Seattle for 22 Nov 2025")

    monocle_trace_asserter.called_tool("book_flight_tool").contains_input("San Jose").contains_input("Seattle")
    monocle_trace_asserter.called_agent("foo_agent").contains_output("San Jose").contains_output("Seattle")

@pytest.mark.asyncio
async def test_sentiment_bias_evaluation(monocle_trace_asserter):
    """v0: Basic sentiment, bias evaluation on trace - only specify eval name and expected value."""
    get_scores("Book a flight from San Jose to Seattle for 27th Nov 2025.")
    # Fact is implicit (trace), only specify eval template name and expected value
    monocle_trace_asserter.with_evaluation("okahu").check_eval("sentiment", "positive")\
        .check_eval("bias", "unbiased")

@pytest.mark.asyncio
async def test_quality_evaluation(monocle_trace_asserter):
    """Demonstrates using multiple evaluators (okahu and bert_score) within a single test."""
    get_scores("Please Book a flight from New York to Hamburg for 1st Dec 2025. Book a flight from Hamburg to Paris on January 1st. " \
               "Then book a hotel room in Paris for 5th Jan 2026.")
    
    # Use okahu evaluator for quality metrics
    # You can chain multiple check_eval calls for different eval templates
    monocle_trace_asserter.with_evaluation("okahu").check_eval("frustration", "ok")\
        .check_eval("hallucination", "no_hallucination")
    
    # Once declared, the evaluator persists for subsequent assertions
    monocle_trace_asserter.with_evaluation("okahu").check_eval("contextual_precision", "high_precision")

@pytest.mark.asyncio
async def test_tool_agent_invocation1(monocle_trace_asserter):
    get_scores("Book a flight from San Francisco to Mumbai for 26th April 2026. Book a two queen room at Marriott Intercontinental at Central Mumbai for 27th April 2026 for 4 nights.")
    
    monocle_trace_asserter.called_tool("book_flight_tool","agc_travel_agent") \
        .contains_input("Mumbai").contains_input("San Francisco") \
        .contains_output("San Francisco to Mumbai").contains_output("success")
    
    monocle_trace_asserter.called_tool("book_flight_tool","agc_travel_agent") \
        .contains_input("Central Mumbai").contains_input("Marriott Intercontinental") \
        .contains_output("booked") \
        .contains_output("Successfully booked a stay at Marriott Intercontinental in Central Mumbai") \
        .contains_output("success")
    
    monocle_trace_asserter.called_agent("agc_travel_agent")

    # example error case: check_eval will return non_toxic. Test will fail as expected since we are checking for toxic. 
    # This is to demonstrate how to use check_eval for error cases as well.
    monocle_trace_asserter.with_evaluation("okahu").check_eval("toxicity", "toxic")   

@pytest.mark.asyncio
async def test_multiple_evaluators_evaluation(monocle_trace_asserter):
    """Demonstrates using multiple evaluators (okahu and bert_score) within a single test."""
    get_scores("Please Book a flight from New York to Hamburg for 1st Dec 2025. Book a flight from Hamburg to Paris on January 1st. " \
               "Then book a hotel room in Paris for 5th Jan 2026.")
    
    # Use okahu evaluator for quality metrics
    # You can chain multiple check_eval calls for different eval templates
    monocle_trace_asserter.with_evaluation("okahu").check_eval("frustration", "ok")\
        .check_eval("hallucination", "no_hallucination")
    
    # Switch to bert_score evaluator by passing options as a dictionary
    # This is an example of how you can use multiple evalauators in a single test. 
    monocle_trace_asserter.with_evaluation("bert_score", {"model_type": "bert-base-uncased"})
    
    # Switch back to okahu evaluator for additional checks
    # Once declared, the evaluator persists for subsequent assertions
    monocle_trace_asserter.with_evaluation("okahu").check_eval("contextual_precision", "high_precision")

if __name__ == "__main__":
    pytest.main([__file__]) 
