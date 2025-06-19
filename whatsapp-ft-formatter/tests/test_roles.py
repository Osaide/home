import pytest
from src import roles

@pytest.fixture
def sample_conversations_for_roles(): # Simplified mock, not from file for this unit test
    return [
        [ # Conversation 1
            {"author": "User1", "text": "..." },
            {"author": "+1234567890", "text": "..."}
        ],
        [ # Conversation 2
            {"author": "Tu", "text": "..."},
            {"author": "Some Random Name", "text": "..."}
        ]
    ]

def test_assign_roles_basic(sample_conversations_for_roles):
    roles_map = roles.assign_roles(sample_conversations_for_roles)
    assert isinstance(roles_map, dict)
    assert len(roles_map) == 4 # User1, +1234567890, Tu, Some Random Name

    assert roles_map.get("User1") == "participant" # Default
    assert roles_map.get("+1234567890") == "client"
    assert roles_map.get("Tu") == "agent"
    assert roles_map.get("Some Random Name") == "participant"
