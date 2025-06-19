# src/validator.py
import json
import jsonschema # For schema validation
from jsonschema import validate, ValidationError, SchemaError
from typing import List, Dict, Any
from config import settings # For SCHEMA_PATH

# Load the schema once when the module is loaded
SCHEMA = None
try:
    with open(settings.SCHEMA_PATH, 'r') as f:
        SCHEMA = json.load(f)
    print(f"JSON schema '{settings.SCHEMA_PATH}' loaded successfully for validator.")
except FileNotFoundError:
    print(f"Error: Schema file not found at '{settings.SCHEMA_PATH}'. Validation will fail.")
    SCHEMA = None # Ensure SCHEMA is None if loading fails
except json.JSONDecodeError as e:
    print(f"Error: Could not decode JSON from schema file '{settings.SCHEMA_PATH}': {e}. Validation will fail.")
    SCHEMA = None
except Exception as e:
    print(f"An unexpected error occurred while loading schema '{settings.SCHEMA_PATH}': {e}. Validation will fail.")
    SCHEMA = None


def validate_json(json_objs: List[Dict[str, Any]], schema_path: str = None) -> bool:
    """
    Validates a list of JSON objects against the predefined JSON schema.

    Args:
        json_objs (List[Dict[str, Any]]): The list of JSON objects to validate.
        schema_path (str, optional): Path to the schema file. If None, uses SCHEMA_PATH from settings.
                                     This allows overriding the default schema for specific calls if needed.

    Returns:
        bool: True if all objects are valid, False otherwise.
               Prints validation errors if any.
    """
    current_schema = SCHEMA
    if schema_path: # If a specific schema path is provided for this call
        try:
            with open(schema_path, 'r') as f:
                current_schema = json.load(f)
            print(f"Using custom schema for this validation: '{schema_path}'")
        except Exception as e:
            print(f"Error loading custom schema from '{schema_path}': {e}. Falling back to preloaded schema (if any).")
            # If custom schema fails to load, current_schema remains the preloaded one (or None)

    if not current_schema:
        print("Error: JSON Schema is not loaded. Cannot perform validation.")
        return False

    all_valid = True
    for i, obj in enumerate(json_objs):
        try:
            validate(instance=obj, schema=current_schema)
            # print(f"Object {i} (Dialog ID: {obj.get('dialog_id', 'N/A')}) is valid against the schema.")
        except SchemaError as e:
            print(f"Error: Invalid schema itself. Path: {schema_path or settings.SCHEMA_PATH}. Details: {e}")
            all_valid = False # Schema error means no validation can be trusted
            break # Stop validation if schema is broken
        except ValidationError as e:
            all_valid = False
            dialog_id = obj.get('dialog_id', f'at index {i}')
            print(f"Validation Error for Dialog ID '{dialog_id}':")
            print(f"  Message: {e.message}")
            print(f"  Path in JSON: {list(e.path)}")
            # print(f"  Violated Schema Rule: {e.schema_path}") # More detailed
            # print(f"  Problematic Instance Part: {e.instance}") # Can be large
            print("-" * 20)
        except Exception as e:
            all_valid = False
            dialog_id = obj.get('dialog_id', f'at index {i}')
            print(f"An unexpected error occurred during validation of Dialog ID '{dialog_id}': {e}")
            print("-" * 20)


    if all_valid and json_objs:
        print(f"All {len(json_objs)} JSON objects validated successfully against the schema.")
    elif not json_objs:
        print("No JSON objects provided to validate.")
        return True # Or False, depending on desired behavior for empty list

    return all_valid

if __name__ == '__main__':
    print("\n--- Testing src/validator.py ---")

    # Ensure schema.json exists and is loaded (SCHEMA should be populated)
    if SCHEMA is None:
        print("Cannot run validator tests: Schema is not loaded. Check schema.json path and content.")
    else:
        # 1. Test with valid objects
        valid_json_objects = [
            {
                "dialog_id": 1,
                "messages": [
                    {"role": "client", "text": "Hello", "intent": "greeting", "entities": {}},
                    {"role": "agent", "text": "Hi there", "intent": "greeting", "entities": {}}
                ],
                "summary": "A short greeting exchange.",
                "topics": ["greeting"],
                "final_request": "None"
            },
            {
                "dialog_id": 2,
                "messages": [
                    {"role": "client", "text": "Need help with product X.", "intent": "problem_report", "entities": {"product": ["X"]}}
                ],
                "summary": "Client needs help with product X.",
                "topics": ["product X", "help"],
                "final_request": "Need help with product X."
            }
        ]
        print("\nTesting with VALID objects:")
        is_valid_run1 = validate_json(valid_json_objects)
        print(f"Validation result for valid objects: {is_valid_run1}")
        assert is_valid_run1 == True

        # 2. Test with invalid objects
        invalid_json_objects = [
            { # Missing dialog_id (required)
                "messages": [{"role": "user", "text": "Test"}],
                "summary": "...", "topics": [], "final_request": ""
            },
            { # Messages is not an array
                "dialog_id": 3,
                "messages": {"role": "client", "text": "This should be a list"},
                "summary": "...", "topics": [], "final_request": ""
            },
            { # Message item missing 'role' (required)
                "dialog_id": 4,
                "messages": [{"text": "I forgot my role."}],
                "summary": "...", "topics": [], "final_request": ""
            }
        ]
        print("\nTesting with INVALID objects:")
        is_valid_run2 = validate_json(invalid_json_objects)
        print(f"Validation result for invalid objects: {is_valid_run2}")
        assert is_valid_run2 == False

        # 3. Test with an empty list
        print("\nTesting with an EMPTY list of objects:")
        is_valid_run3 = validate_json([])
        print(f"Validation result for empty list: {is_valid_run3}")
        # assert is_valid_run3 == True # Or False, based on strictness for empty inputs

        # 4. Test with a valid object but a non-existent custom schema path
        # (This tests the fallback mechanism, assuming SCHEMA is loaded)
        print("\nTesting with a non-existent custom schema path (should use preloaded schema):")
        is_valid_run4 = validate_json([valid_json_objects[0]], schema_path="non_existent_schema.json")
        print(f"Validation result for non-existent custom schema: {is_valid_run4}")
        assert is_valid_run4 == True

        # 5. Test with a schema that itself is invalid (e.g. malformed JSON)
        # Create a temporary malformed schema file
        malformed_schema_content = "{'type': 'object', 'properties': {'name': {'type': 'string'}" # Missing closing brace
        malformed_schema_path = "temp_malformed_schema.json"
        with open(malformed_schema_path, "w") as f_malformed:
            f_malformed.write(malformed_schema_content)

        print("\nTesting with a MALFORMED custom schema file:")
        # This will cause json.JSONDecodeError when trying to load the malformed schema
        # And then should fall back to the globally loaded SCHEMA (if any) or fail if that's also bad
        is_valid_run5 = validate_json([valid_json_objects[0]], schema_path=malformed_schema_path)
        print(f"Validation result for malformed custom schema: {is_valid_run5}")
        # If global SCHEMA is valid, and custom fails to load, it should validate against global.
        # The behavior here depends on how strictly we want to handle schema loading failures.
        # Current code prints error and uses global SCHEMA.
        assert is_valid_run5 == True if SCHEMA else False # Should be true if global SCHEMA is fine

        import os
        if os.path.exists(malformed_schema_path):
            os.remove(malformed_schema_path)

    print("--- Finished testing src/validator.py ---")
