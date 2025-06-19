# src/formatter.py
from typing import List, Dict, Any, Set
from src.segmentation import Conversation # Assumes List[Dict[str, Any]]
from config import settings # For MAX_SUMMARY_LENGTH

def get_text_from_message(message: Dict[str, Any]) -> str:
    """Safely retrieves text from a message dictionary."""
    return message.get("text", "") if isinstance(message, dict) else ""

def build_json(
    conversations: List[Conversation],
    roles_mapping: Dict[str, str],
    all_extractions: List[Dict[str, Any]] # Assume this is a flat list of NLP results, one per original message
) -> List[Dict[str, Any]]:
    """
    Constructs final JSON objects from processed conversation data.

    Args:
        conversations: List of segmented conversations. Each conversation is a list of message dicts.
        roles_mapping: Dictionary mapping author names to roles (e.g., 'client', 'agent').
        all_extractions: A flat list of NLP extraction results, corresponding to each message
                         across all conversations in their original order.

    Returns:
        List of dictionaries, each conforming to schema.json.
    """
    output_json_objects: List[Dict[str, Any]] = []
    extraction_idx = 0 # To iterate through the flat list of all_extractions

    for dialog_idx, conv_segment in enumerate(conversations):
        if not conv_segment: # Skip empty conversation segments
            continue

        formatted_messages: List[Dict[str, Any]] = []
        conversation_texts_for_summary: List[str] = []

        # Potential topics from entities (simple approach: collect all entity values)
        # More sophisticated topic modeling could be used here.
        dialog_topics: Set[str] = set()

        for message_dict in conv_segment:
            author = message_dict.get("author")
            text = get_text_from_message(message_dict)

            role = roles_mapping.get(author, "participant") # Default to participant if author not in map

            # Get corresponding NLP extraction for this message
            # This assumes 'all_extractions' is perfectly aligned with messages as they appear
            # in 'conversations' when flattened.
            current_extraction = {}
            if extraction_idx < len(all_extractions):
                current_extraction = all_extractions[extraction_idx]
                extraction_idx += 1
            else:
                print(f"Warning: Ran out of NLP extractions. Message by '{author}' will have empty NLP fields.")
                current_extraction = {"intent": "", "entities": {}, "confidence": 0.0} # Default empty extraction

            # Collect entities for topics
            if isinstance(current_extraction.get("entities"), dict):
                for entity_type, entity_values in current_extraction["entities"].items():
                    if isinstance(entity_values, list):
                        for val in entity_values:
                            dialog_topics.add(str(val)) # Add individual entity values as topics
                    elif isinstance(entity_values, str): # if entities are str not list of str
                         dialog_topics.add(entity_values)


            formatted_messages.append({
                "role": role,
                "text": text,
                "intent": current_extraction.get("intent", ""),
                "entities": current_extraction.get("entities", {})
                # "confidence" from NLP could be added here if desired in schema
            })
            conversation_texts_for_summary.append(text)

        # Create a simple summary (first N characters/tokens of concatenated texts)
        full_conversation_text = " ".join(conversation_texts_for_summary)
        summary = full_conversation_text[:settings.MAX_SUMMARY_LENGTH]
        if len(full_conversation_text) > settings.MAX_SUMMARY_LENGTH:
            summary += "..."

        # Determine final_request (placeholder logic - e.g., last message from a 'client' role)
        # This is highly dependent on specific business logic.
        final_request_text = ""
        for msg in reversed(conv_segment): # Look from last message
            msg_author = msg.get("author")
            if msg_author and roles_mapping.get(msg_author) == "client": # Example: last client message
                final_request_text = get_text_from_message(msg)
                break
        if not final_request_text and conv_segment: # Fallback to last message of segment
             final_request_text = get_text_from_message(conv_segment[-1])


        output_json_objects.append({
            "dialog_id": dialog_idx,
            "messages": formatted_messages,
            "summary": summary,
            "topics": sorted(list(dialog_topics)), # Sorted list of unique topics
            "final_request": final_request_text[:settings.MAX_SUMMARY_LENGTH] # Also cap length
        })

    if extraction_idx < len(all_extractions):
        print(f"Warning: {len(all_extractions) - extraction_idx} NLP extractions were not used. Message count mismatch?")

    print(f"Formatted {len(output_json_objects)} dialog objects.")
    return output_json_objects

if __name__ == '__main__':
    import datetime
    print("\n--- Testing src/formatter.py ---")

    # Mock data based on previous modules' outputs
    mock_conversations: List[Conversation] = [
        [ # Conversation 1
            {"timestamp": datetime.datetime(2023,1,1,10,0,0), "author": "UserA", "text": "Hello, I need help."},
            {"timestamp": datetime.datetime(2023,1,1,10,0,30), "author": "AgentX", "text": "Hi UserA, what's up?"}
        ],
        [ # Conversation 2
            {"timestamp": datetime.datetime(2023,1,1,10,5,0), "author": "UserA", "text": "My card is not working."},
            {"timestamp": datetime.datetime(2023,1,1,10,5,30), "author": "UserA", "text": "I tried it yesterday."},
            {"timestamp": datetime.datetime(2023,1,1,10,6,0), "author": "AgentX", "text": "Okay, what card is it?"}
        ]
    ]

    mock_roles_mapping = {
        "UserA": "client",
        "AgentX": "agent"
    }

    # Flat list of NLP extractions, one for each message in mock_conversations
    # Msg1: UserA: Hello, I need help.
    # Msg2: AgentX: Hi UserA, what's up?
    # Msg3: UserA: My card is not working.
    # Msg4: UserA: I tried it yesterday.
    # Msg5: AgentX: Okay, what card is it?
    mock_all_extractions = [
        {"intent": "problem_report", "entities": {"problem": ["help"]}, "confidence": 0.8},
        {"intent": "greeting", "entities": {}, "confidence": 0.9},
        {"intent": "problem_report", "entities": {"item": ["card"], "status": ["not working"]}, "confidence": 0.85},
        {"intent": "inform", "entities": {"DATE": ["yesterday"]}, "confidence": 0.7},
        {"intent": "query", "entities": {"item": ["card"]}, "confidence": 0.75}
    ]

    # Override settings for predictable test if needed
    settings.MAX_SUMMARY_LENGTH = 50

    formatted_output = build_json(mock_conversations, mock_roles_mapping, mock_all_extractions)

    print("\n--- Formatted JSON Objects ---")
    if formatted_output:
        for i, json_obj in enumerate(formatted_output):
            print(f"Dialog {json_obj['dialog_id']}:")
            print(f"  Summary: {json_obj['summary']}")
            print(f"  Topics: {json_obj['topics']}")
            print(f"  Final Request: {json_obj['final_request']}")
            print(f"  Messages ({len(json_obj['messages'])}):")
            for msg in json_obj['messages']:
                print(f"    Role: {msg['role']}, Text: '{msg['text'][:30]}...', Intent: {msg.get('intent')}, Entities: {msg.get('entities')}")
            print("-" * 20)

            # Basic check against schema structure (not full validation)
            assert "dialog_id" in json_obj
            assert "messages" in json_obj
            assert isinstance(json_obj["messages"], list)
            if json_obj["messages"]:
                assert "role" in json_obj["messages"][0]
                assert "text" in json_obj["messages"][0]

    else:
        print("No JSON objects were formatted.")

    print("--- Finished testing src/formatter.py ---")
