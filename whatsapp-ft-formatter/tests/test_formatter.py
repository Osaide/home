import pytest
import datetime
from src import formatter
from config import settings

@pytest.fixture
def sample_data_for_formatter():
    conversations = [
        [ # Conv 1
            {"timestamp": datetime.datetime(2023,1,1,10,0,0), "author": "UserA", "text": "Hello there."},
            {"timestamp": datetime.datetime(2023,1,1,10,0,30), "author": "AgentB", "text": "Hi! How can I help?"}
        ]
    ]
    roles_mapping = {"UserA": "client", "AgentB": "agent"}
    # Extractions should be a flat list, one per message
    all_extractions = [
        {"intent": "greeting", "entities": {" saluto": ["Hello"]}, "confidence": 0.9}, # For "Hello there."
        {"intent": "query_help", "entities": {}, "confidence": 0.8}  # For "Hi! How can I help?"
    ]
    return conversations, roles_mapping, all_extractions

def test_build_json_basic(sample_data_for_formatter):
    conversations, roles_mapping, all_extractions = sample_data_for_formatter

    # Override summary length for predictable test output
    original_summary_length = settings.MAX_SUMMARY_LENGTH
    settings.MAX_SUMMARY_LENGTH = 20

    json_objects = formatter.build_json(conversations, roles_mapping, all_extractions)

    settings.MAX_SUMMARY_LENGTH = original_summary_length # Restore

    assert isinstance(json_objects, list)
    assert len(json_objects) == 1

    obj = json_objects[0]
    assert "dialog_id" in obj and obj["dialog_id"] == 0
    assert "messages" in obj and isinstance(obj["messages"], list) and len(obj["messages"]) == 2
    assert "summary" in obj
    assert "topics" in obj and isinstance(obj["topics"], list)
    assert "final_request" in obj

    # Check message structure
    msg1 = obj["messages"][0]
    assert msg1["role"] == "client"
    assert msg1["text"] == "Hello there."
    assert msg1["intent"] == "greeting"
    assert " saluto" in msg1["entities"] # Match the key with leading space from mock data

    # Check summary (simple concatenation and slicing)
    assert obj["summary"].startswith("Hello there. Hi! Ho") # Max 20 chars + ...
