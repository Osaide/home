# src/roles.py
import re
from typing import List, Dict, Set, Any
# Assuming Conversation is List[Dict[str, Any]] as defined in segmentation.py
from src.segmentation import Conversation # Or define it here if preferred

# More specific patterns can be added here or loaded from a config
# For example, if 'Tu' or 'You' is always the agent in a specific setup
AGENT_PATTERNS = [
    re.compile(r"^(You|Tu)$", re.IGNORECASE),
    # Add other specific agent names or patterns if known
    # re.compile(r"^(Support|Agent X)$", re.IGNORECASE),
]

# Client patterns often involve phone numbers or guest-like names
CLIENT_PATTERNS = [
    re.compile(r"^\+?\d[\d\s\-\(\)]+$"), # Matches phone numbers
    # Add other patterns like "Guest" or specific client identifiers
    # re.compile(r"^Guest\s*\d*$", re.IGNORECASE),
]

def assign_roles(conversations: List[Conversation]) -> Dict[str, str]:
    """
    Assigns roles to authors based on predefined patterns.
    Roles: 'client', 'agent', 'participant'.

    Args:
        conversations: A list of conversations, where each conversation is a list of messages.
                       Each message dictionary should have an 'author' key.

    Returns:
        A dictionary mapping unique author names to their assigned roles.
    """
    if not conversations:
        return {}

    authors: Set[str] = set()
    for conv in conversations:
        for msg in conv:
            if "author" in msg and msg["author"]: # Ensure author key exists and is not empty
                authors.add(msg["author"])
            # else:
                # print(f"Warning: Message found without author or empty author: {msg}")


    role_mapping: Dict[str, str] = {}
    print(f"Found authors for role assignment: {authors}")

    for author_name in authors:
        assigned_role = "participant" # Default role

        # Check for Agent
        for pattern in AGENT_PATTERNS:
            if pattern.match(author_name):
                assigned_role = "agent"
                break
        if assigned_role == "agent":
            role_mapping[author_name] = assigned_role
            continue # Move to next author

        # Check for Client
        for pattern in CLIENT_PATTERNS:
            if pattern.match(author_name):
                assigned_role = "client"
                break
        # No continue here, so if not agent and not client, it remains participant or gets overwritten by client

        role_mapping[author_name] = assigned_role # Assigns client or participant

    print(f"Role mapping complete: {role_mapping}")
    return role_mapping

if __name__ == '__main__':
    import datetime
    print("\n--- Testing src/roles.py ---")

    # Mock conversations (structure from segmentation.py)
    mock_conversations_for_roles: List[Conversation] = [
        [ # Conversation 1
            {"timestamp": datetime.datetime(2023,1,1,10,0,0), "author": "+11234567890", "text": "Hello"},
            {"timestamp": datetime.datetime(2023,1,1,10,0,30), "author": "SupportAgent", "text": "Hi there!"},
            {"timestamp": datetime.datetime(2023,1,1,10,1,0), "author": "+11234567890", "text": "I need help."},
        ],
        [ # Conversation 2
            {"timestamp": datetime.datetime(2023,1,1,10,5,0), "author": "Tu", "text": "What is your issue?"}, # 'Tu' should be agent
            {"timestamp": datetime.datetime(2023,1,1,10,5,30), "author": "Another User", "text": "I have a question too."},
            {"timestamp": datetime.datetime(2023,1,1,10,6,0), "author": "00393331234567", "text": "My phone number is Italian"},
        ],
        [ # Conversation 3 (empty author or missing)
            {"timestamp": datetime.datetime(2023,1,1,10,7,0), "author": "", "text": "Empty author"},
            {"timestamp": datetime.datetime(2023,1,1,10,7,30), "text": "Missing author"}, # No author key
        ]
    ]

    # Adjust AGENT_PATTERNS for this test if 'SupportAgent' is not covered by default
    AGENT_PATTERNS.append(re.compile(r"^SupportAgent$", re.IGNORECASE))

    assigned_roles_map = assign_roles(mock_conversations_for_roles)

    print("\n--- Assigned Roles ---")
    if assigned_roles_map:
        for author, role in assigned_roles_map.items():
            print(f"Author: '{author}', Assigned Role: '{role}'")
    else:
        print("No roles assigned (or no authors found).")

    # Expected:
    # +11234567890: client
    # SupportAgent: agent
    # Tu: agent
    # Another User: participant
    # 00393331234567: client
    # "" (empty string author) might be 'participant' if not filtered, or not present if filtered.

    print("--- Finished testing src/roles.py ---")
