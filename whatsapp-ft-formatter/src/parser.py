# src/parser.py

import re
from typing import List, Dict, Optional
from datetime import datetime

# Regex to capture WhatsApp messages.
# It looks for a date, time, author, and message.
# Handles different date formats (dd/mm/yyyy and mm/dd/yyyy) and author names.
# Assumes author names do not contain ':' except for the one separating author from message.
# It also handles multi-line messages.
# Example: [DD/MM/YYYY, HH:MM:SS] Author Name: Message text
# Example: MM/DD/YYYY, HH:MM - Author Name: Message text (older format, less common for exports)

# More robust regex:
# - Allows for optional seconds.
# - Allows for AM/PM in time.
# - Author can contain spaces.
# - Message can be multi-line.
WHATSAPP_MESSAGE_REGEX = re.compile(
    r"^(?P<timestamp_bracket>\[?(?P<date>\d{1,2}/\d{1,2}/\d{2,4}),\s*(?P<time>\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?)]?\s*)?"  # Optional timestamp bracket and content
    r"(?P<author>[^:]+):\s"  # Author: anything up to the first colon-space
    r"(?P<text>.+)",  # Message: the rest of the line
    re.MULTILINE # Ensure ^ matches start of each line for messages that might not have timestamps
)

# Regex for lines that are continuations of a previous message (don't have timestamp/author)
MESSAGE_CONTINUATION_REGEX = re.compile(
    r"^(?!(\[?\d{1,2}/\d{1,2}/\d{2,4},\s*\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?]?\s*[^:]+:\s)).+"
)


def parse_whatsapp_date(date_str: str, time_str: str) -> Optional[datetime]:
    """
    Parses date and time strings into a datetime object.
    Tries common WhatsApp date formats.
    """
    full_datetime_str = f"{date_str} {time_str}"
    formats_to_try = [
        "%d/%m/%Y %H:%M:%S",  # DD/MM/YYYY HH:MM:SS
        "%d/%m/%y %H:%M:%S",  # DD/MM/YY HH:MM:SS
        "%m/%d/%Y %H:%M:%S",  # MM/DD/YYYY HH:MM:SS (less common for exports)
        "%m/%d/%y %H:%M:%S",  # MM/DD/YY HH:MM:SS
        "%d/%m/%Y %H:%M",     # DD/MM/YYYY HH:MM (if seconds are missing)
        "%d/%m/%y %H:%M",     # DD/MM/YY HH:MM
        "%m/%d/%Y %H:%M",     # MM/DD/YYYY HH:MM
        "%m/%d/%y %H:%M",     # MM/DD/YY HH:MM
        # Potentially formats with AM/PM if your regex captures it and it's needed
        "%d/%m/%Y %I:%M:%S %p", # DD/MM/YYYY HH:MM:SS AM/PM
        "%d/%m/%y %I:%M:%S %p",
        "%d/%m/%Y %I:%M %p",    # DD/MM/YYYY HH:MM AM/PM
        "%d/%m/%y %I:%M %p",
    ]
    for fmt in formats_to_try:
        try:
            return datetime.strptime(full_datetime_str, fmt)
        except ValueError:
            continue
    print(f"Warning: Could not parse date-time: {full_datetime_str} with known formats.")
    return None

def parse_txt(file_paths: List[str]) -> List[Dict]:
    """
    Parses raw TXT chat files into a list of message dictionaries.

    Args:
        file_paths (List[str]): List of paths to .txt chat files.

    Returns:
        List[Dict{"timestamp": datetime, "author": str, "text": str}]:
        A list of dictionaries, each representing a message, sorted chronologically.
    """
    all_messages = []
    last_message_data = None

    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                print(f"Parsing file: {file_path}")
                current_file_messages = []
                for line_number, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:  # Skip empty lines
                        continue

                    match = WHATSAPP_MESSAGE_REGEX.match(line)
                    if match:
                        data = match.groupdict()
                        timestamp_str = data.get("timestamp_bracket")
                        author = data['author'].strip()
                        text = data['text'].strip()

                        dt_object = None
                        if timestamp_str: # Timestamp is present
                            dt_object = parse_whatsapp_date(data['date'], data['time'])
                            if dt_object is None:
                                # If parsing fails, store raw timestamp or skip
                                print(f"Line {line_number}: Could not parse timestamp for message by {author}")
                                # Decide: skip message, or add with raw/None timestamp?
                                # For now, we'll add with None timestamp if parsing fails but regex matched structure

                        message_data = {"timestamp": dt_object, "author": author, "text": text, "raw_timestamp": timestamp_str or ""}
                        current_file_messages.append(message_data)
                        last_message_data = message_data

                    elif last_message_data and MESSAGE_CONTINUATION_REGEX.match(line):
                        # This line is a continuation of the previous message
                        last_message_data["text"] += "\n" + line # Using \n to represent newline in text
                    else:
                        # Line doesn't match new message format or continuation
                        # Could be a system message (e.g., "You created this group") or media omission
                        # For now, we'll try to append it to the last known message if it exists,
                        # or log it as an unparsed line.
                        if last_message_data:
                             # Prepending a special marker to indicate it's a system/unstructured line
                            last_message_data["text"] += "\n[UNPARSED_LINE] " + line
                        else:
                            print(f"Line {line_number}: Unparsed line (doesn't match message format or continuation): '{line[:100]}...'")

                all_messages.extend(current_file_messages)
                last_message_data = None # Reset for next file

        except FileNotFoundError:
            print(f"Error: File not found at {file_path}")
        except Exception as e:
            print(f"Error parsing file {file_path}: {e}")

    # Sort messages by timestamp, handling None timestamps by placing them earlier or later
    # Here, messages without a valid timestamp are placed at the beginning.
    # You might want a different strategy (e.g. attempt to infer based on order in file).
    all_messages.sort(key=lambda x: x["timestamp"] if x["timestamp"] else datetime.min)

    # Clean up messages that might be empty after processing (e.g. only a timestamp)
    # And ensure all required keys are present, even if text is empty.
    processed_messages = []
    for msg in all_messages:
        if msg.get("text") or (msg.get("author") and msg.get("timestamp")): # Keep if text or if it's a structured entry
            processed_messages.append({
                "timestamp": msg["timestamp"],
                "author": msg["author"],
                "text": msg.get("text", "").strip(), # Ensure text is not None
                "raw_timestamp": msg.get("raw_timestamp", "")
            })

    print(f"Successfully parsed {len(processed_messages)} messages from {len(file_paths)} file(s).")
    return processed_messages

if __name__ == '__main__':
    # Create dummy chat files for testing
    dummy_chat_content_1 = """
[01/01/2023, 10:00:00] User1: Hello!
This is a multi-line message.
[01/01/2023, 10:00:30] User2: Hi User1.
How are you?
[01/01/2023, 10:01:00] User1: I'm fine, thanks!
And you?
This message has a timestamp.
Another line for the same message.
This is a system message that will be appended.
[02/02/2023, 11:00:00] User3: A message from another user.
    """
    dummy_chat_content_2 = """
1/3/23, 14:30 - TestUser: Message with a different date format and no seconds.
[03/03/2023, 15:00:15] AnotherUser: Just a simple message.
This line has no timestamp and should be part of AnotherUser's message.
[INVALID_DATE, 10:00:00] UserErr: This message has an invalid date.
User With Colon: In Name: This is a tricky one.
[03/03/2023, 15:01:00] AnotherUser: Message after the one with no timestamp.
    """

    dummy_file_1 = "dummy_chat_1.txt"
    dummy_file_2 = "dummy_chat_2.txt"

    with open(dummy_file_1, "w", encoding="utf-8") as f:
        f.write(dummy_chat_content_1)
    with open(dummy_file_2, "w", encoding="utf-8") as f:
        f.write(dummy_chat_content_2)

    test_file_paths = [dummy_file_1, dummy_file_2]

    print("Testing parser.py...")
    parsed_messages = parse_txt(test_file_paths)

    if parsed_messages:
        print(f"\n--- Parsed Messages ({len(parsed_messages)}) ---")
        for i, msg in enumerate(parsed_messages):
            ts = msg['timestamp'].strftime('%Y-%m-%d %H:%M:%S') if msg['timestamp'] else "No Timestamp"
            print(f"{i+1}. Timestamp: {ts}, Author: '{msg['author']}', Text: '{msg['text'][:60]}...'")

        # Check chronological order (basic check)
        timestamps = [m['timestamp'] for m in parsed_messages if m['timestamp']]
        if timestamps == sorted(timestamps):
            print("\nMessages are sorted chronologically.")
        else:
            print("\nWarning: Messages may not be perfectly sorted chronologically.")
            # for ts_obj in timestamps: print(ts_obj)


    # Clean up dummy files
    os.remove(dummy_file_1)
    os.remove(dummy_file_2)
    print("\nFinished testing parser.py.")
