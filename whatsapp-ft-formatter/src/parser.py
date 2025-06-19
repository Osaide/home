# src/parser.py
import re
import datetime # Corrected import from 'import re, datetime' to separate lines
from typing import List, Dict, Optional
import os # Added for __main__ to construct path to sample.txt

# Regex pattern from the new plan
# PATTERN = r"\[(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2}(:\d{2})?)\] (.*?): (.*)" # Original from plan
# Issues with original:
# 1. Date part \d{2,4} for year can be problematic if year is YY. Using \d{2,4} is fine.
# 2. Time part (\d{1,2}:\d{2}(:\d{2})?) - optional seconds group is not named and might cause issues in m.groups().
#    It's better to make the seconds part of the main time group or handle it carefully.
# 3. Author (.*?) non-greedy might be too broad if names can have colons.
#    The previous parser's [^:]+ was more robust for author.
# 4. Message (.*) is greedy and fine.

# Revised PATTERN based on new plan's structure but with slight robustness improvements:
# Handles [DD/MM/YYYY, HH:MM:SS] Author: Message
# Or [DD/MM/YY, HH:MM] Author: Message
PATTERN_STRING = r"\[(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2}(?::\d{2})?)\]\s*([^:]+):\s*(.*)"
# Groups: 1:Date, 2:Time (with optional :SS), 3:Author, 4:Text
# Example: [01/01/2023, 10:00:00] User1: Hello
# Example: [01/01/23, 10:00] User2: Hi

# Let's try to make the timestamp parsing more flexible for date part (YY or YYYY)
# And time part (HH:MM or HH:MM:SS)
DATE_FORMATS_TO_TRY = [
    "%d/%m/%Y %H:%M:%S", # DD/MM/YYYY HH:MM:SS
    "%d/%m/%y %H:%M:%S", # DD/MM/YY HH:MM:SS
    "%d/%m/%Y %H:%M",    # DD/MM/YYYY HH:MM
    "%d/%m/%y %H:%M",    # DD/MM/YY HH:MM
]

# For lines that are continuations of a previous message (don't have timestamp/author)
# This regex negative lookahead asserts that the line does NOT start with a timestamp pattern.
MESSAGE_CONTINUATION_REGEX_STRING = r"^(?!(?:\[\d{1,2}/\d{1,2}/\d{2,4},\s*\d{1,2}:\d{2}(?::\d{2})?\]\s*[^:]+:\s*)).+"
MESSAGE_CONTINUATION_REGEX = re.compile(MESSAGE_CONTINUATION_REGEX_STRING)
PATTERN = re.compile(PATTERN_STRING)


def parse_datetime_flexible(date_str: str, time_str: str) -> Optional[datetime.datetime]:
    """Attempts to parse date and time using a list of format strings."""
    full_datetime_str = f"{date_str} {time_str}"
    for fmt in DATE_FORMATS_TO_TRY:
        try:
            return datetime.datetime.strptime(full_datetime_str, fmt)
        except ValueError:
            continue
    # print(f"Warning: Could not parse date-time: '{full_datetime_str}' with known formats.")
    return None

def parse_txt(file_paths: List[str]) -> List[Dict]:
    """
    Parses raw TXT chat files (as specified by the new plan) into a list of message dictionaries.
    Handles multi-line messages by appending to the previous message if a line does not start with a timestamp.
    """
    messages = []
    current_file_messages = [] # To store messages for the current file before extending global list
    last_message_data = None   # To handle multi-line messages

    for path in file_paths:
        print(f"Parsing file: {path}")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                for line_number, line_content in enumerate(f, 1):
                    line_content = line_content.strip()
                    if not line_content: # Skip empty lines
                        continue

                    match = PATTERN.match(line_content)
                    if match:
                        date, time, author, text = match.groups()
                        # ts = datetime.datetime.strptime(f"{date} {time}", "%d/%m/%Y %H:%M") # Original plan's parsing
                        ts = parse_datetime_flexible(date, time) # More flexible parsing

                        if ts is None:
                            print(f"Warning: Line {line_number} in {path}: Timestamp '{date} {time}' by '{author}' could not be parsed. Skipping message.")
                            # last_message_data = None # Reset last message context
                            # continue # Or append with None timestamp if desired

                        message_data = {"timestamp": ts, "author": author.strip(), "text": text.strip()}
                        current_file_messages.append(message_data)
                        last_message_data = message_data # For multi-line handling

                    elif last_message_data and MESSAGE_CONTINUATION_REGEX.match(line_content):
                        # This line is a continuation of the previous message
                        last_message_data["text"] += "\n" + line_content

                    else:
                        # Line doesn't match new message format or continuation
                        # Could be a system message, media omission, or other unhandled format
                        # print(f"Info: Line {line_number} in {path}: Unparsed line (no timestamp, not a continuation): '{line_content[:100]}...'")
                        if last_message_data: # If there's a previous message, append as part of its text
                            last_message_data["text"] += "\n[SYSTEM_OR_UNPARSED] " + line_content
                        else: # No context, log as an orphaned line (or create a special message type)
                            print(f"Info: Line {line_number} in {path}: Orphaned unparsed line: '{line_content[:100]}...'")
                        # last_message_data = None # Reset context if it's an unparsed line interrupting flow

            messages.extend(current_file_messages)
            current_file_messages = [] # Reset for next file
            last_message_data = None   # Reset for next file
        except FileNotFoundError:
            print(f"Error: File not found at {path}")
        except Exception as e:
            print(f"Error parsing file {path}: {e}")

    # Filter out messages that ended up with None timestamp if we decided to include them temporarily
    messages = [m for m in messages if m["timestamp"] is not None]

    # Sort all messages from all files by timestamp
    messages.sort(key=lambda x: x["timestamp"])

    print(f"Successfully parsed {len(messages)} messages from {len(file_paths)} file(s).")
    return messages

if __name__ == '__main__':
    # Create dummy chat files for testing
    dummy_chat_content_1 = """
[01/01/2023, 10:00:00] User1: Hello!
This is a multi-line message from User1.
It continues here.
[01/01/2023, 10:00:30] User2: Hi User1. How are you?
I am fine.
[01/01/23, 10:01] User1: I'm fine, thanks! And you?
This message has a YY date and no seconds.
[01/01/2023, 10:02:00] System: This is a system message that might be missed or appended.
[01/01/2023, 10:03:00] User1: Another message.
    """
    dummy_file_1 = "dummy_chat_parser_test_1.txt"
    with open(dummy_file_1, "w", encoding="utf-8") as f:
        f.write(dummy_chat_content_1)

    # Sample from data/raw/sample.txt if it exists and has content
    sample_file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'sample.txt')
    if not os.path.exists(sample_file_path):
         with open(sample_file_path, "w", encoding="utf-8") as f:
            f.write("[01/01/2024, 12:00] SampleUser: This is a sample message for testing from sample.txt.\nAnother line for sample user.")


    test_file_paths = [dummy_file_1, sample_file_path]

    print("--- Testing src/parser.py ---")
    parsed_messages = parse_txt(test_file_paths)

    if parsed_messages:
        print(f"\n--- Parsed Messages ({len(parsed_messages)}) ---")
        for i, msg in enumerate(parsed_messages):
            ts_str = msg['timestamp'].strftime('%Y-%m-%d %H:%M:%S') if msg['timestamp'] else "Invalid Timestamp"
            print(f"{i+1}. Timestamp: {ts_str}, Author: '{msg['author']}', Text: '{msg['text'][:60].replace('\n', ' ')}...'")

        timestamps = [m['timestamp'] for m in parsed_messages if m['timestamp']]
        if not timestamps or timestamps == sorted(timestamps):
            print("\nMessages are sorted chronologically (or no valid timestamps).")
        else:
            print("\nError: Messages are NOT sorted chronologically.")
    else:
        print("No messages were parsed.")

    # Clean up dummy file
    if os.path.exists(dummy_file_1):
        os.remove(dummy_file_1)
    # Do not remove sample.txt as it's part of the structure

    print("--- Finished testing src/parser.py ---")
