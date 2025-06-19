import pytest
from src import nlp_extraction

def test_extract_entities_basic():
    text = "Hello, meeting is at 3 PM on December 25th. My budget is 500 euros."
    if nlp_extraction.nlp.meta.get("name", "generic") == "generic" and not nlp_extraction.nlp.pipe_names:
         pytest.skip("SpaCy model is blank, NLP extraction test will be minimal.")

    result = nlp_extraction.extract_entities(text)
    assert isinstance(result, dict)
    assert "intent" in result
    assert "entities" in result
    assert "confidence" in result

    assert "TIME" in result["entities"] or any("3 PM" in t for t in result["entities"].get("TIME",[])) # Varies by model
    assert "DATE" in result["entities"] or any("December 25th" in d for d in result["entities"].get("DATE",[]))
    assert "MONEY" in result["entities"] or any("500 euros" in m for m in result["entities"].get("MONEY",[])) or "CARDINAL" in result["entities"] # en_core_web_sm might pick up "500" as CARDINAL

    # Test simple intent
    text_problem = "I have an issue."
    result_problem = nlp_extraction.extract_entities(text_problem)
    assert result_problem["intent"] == "problem_report"
