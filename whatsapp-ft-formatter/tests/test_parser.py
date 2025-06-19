import pytest
import os
from src import parser
from config import settings # To locate sample file

SAMPLE_FILE_PATH = os.path.join(settings.RAW_DATA_DIR, "sample.txt")

def test_parse_txt_sample_file():
    assert os.path.exists(SAMPLE_FILE_PATH), f"Sample file not found at {SAMPLE_FILE_PATH}"
    messages = parser.parse_txt([SAMPLE_FILE_PATH])
    assert isinstance(messages, list)
    assert len(messages) > 0, "Parser returned no messages from sample file."

    # Check structure of the first message
    first_msg = messages[0]
    assert "timestamp" in first_msg
    assert "author" in first_msg
    assert "text" in first_msg
    assert first_msg["author"] == "User1"
    assert "Hello there!" in first_msg["text"]
    # Expected number of messages from sample.txt
    # 1. User1: Hello there! ...
    # 2. User2: I'm doing great ...
    # 3. User1: Glad to hear it.
    # 4. User1: I have another question ...
    # 5. User3: And I am User3 ...
    # 6. User2: The answer is 20.
    # 7. User3: Thanks! Goodbye ...
    assert len(messages) == 7, f"Expected 7 messages from sample.txt, got {len(messages)}"
