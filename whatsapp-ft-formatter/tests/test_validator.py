import pytest
import os
from src import validator
from config import settings # For SCHEMA_PATH

# Ensure schema.json is loaded by validator module
if validator.SCHEMA is None:
    pytest.skip("Schema not loaded in validator module, skipping validator tests.", allow_module_level=True)

@pytest.fixture
def valid_dialog_object():
    return {
        "dialog_id": 1,
        "messages": [
            {"role": "client", "text": "Hello", "intent": "greeting", "entities": {}},
            {"role": "agent", "text": "Hi there", "intent": "greeting", "entities": {}}
        ],
        "summary": "A short greeting exchange.",
        "topics": ["greeting"],
        "final_request": "None"
    }

@pytest.fixture
def invalid_dialog_object(): # Missing required 'messages'
    return {
        "dialog_id": 2,
        # "messages": [], # This field is required by schema.json
        "summary": "Test",
        "topics": [],
        "final_request": ""
    }

def test_validate_json_valid(valid_dialog_object):
    assert validator.validate_json([valid_dialog_object]) == True

def test_validate_json_invalid(invalid_dialog_object):
    assert validator.validate_json([invalid_dialog_object]) == False

def test_validate_json_empty_list():
    assert validator.validate_json([]) == True # Empty list is considered valid (no objects to fail)
