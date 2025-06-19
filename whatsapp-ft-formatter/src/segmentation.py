# src/segmentation.py
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer, util
from config import settings # For TIMEOUT_MINUTES, SENTENCE_TRANSFORMER_MODEL, SEMANTIC_SIMILARITY_THRESHOLD
import datetime # For timedelta

# Initialize the Sentence Transformer model
# This can take a few seconds when first called.
print(f"Loading SentenceTransformer model: {settings.SENTENCE_TRANSFORMER_MODEL}...")
try:
    model = SentenceTransformer(settings.SENTENCE_TRANSFORMER_MODEL)
    print("SentenceTransformer model loaded successfully.")
except Exception as e:
    print(f"Error loading SentenceTransformer model '{settings.SENTENCE_TRANSFORMER_MODEL}': {e}")
    print("Segmentation based on semantic similarity will be affected. Ensure the model name is correct and it's installed.")
    # Fallback or raise error: For now, we'll let it proceed, but similarity checks will fail if model is None
    model = None

# Define a Conversation type hint for clarity, though it's just a list of messages for now.
Conversation = List[Dict[str, Any]]

def segment(messages: List[Dict[str, Any]]) -> List[Conversation]:
    """
    Segments messages into conversations based on author change, timeout, and semantic similarity.
    Args:
        messages: A list of message dictionaries, sorted chronologically.
                  Each dict must have 'timestamp', 'author', and 'text'.
    Returns:
        A list of conversations, where each conversation is a list of messages.
    """
    if not messages:
        return []

    if model is None:
        print("Warning: SentenceTransformer model not loaded. Semantic segmentation will be skipped.")

    conversations: List[Conversation] = []
    current_conversation: Conversation = [messages[0]] # Start the first conversation with the first message

    # Use settings for configurable parameters
    timeout_seconds = settings.TIMEOUT_MINUTES * 60
    similarity_threshold = settings.SEMANTIC_SIMILARITY_THRESHOLD

    for i in range(1, len(messages)):
        current_msg = messages[i]
        prev_msg = messages[i-1] # In the same potential segment

        # Ensure messages have the required keys
        if not all(k in current_msg for k in ['timestamp', 'author', 'text']) or \
           not all(k in prev_msg for k in ['timestamp', 'author', 'text']):
            print(f"Warning: Message missing required keys (timestamp, author, text). Skipping message index {i} for segmentation logic.")
            # Decide how to handle this: skip message, add to current segment, or start new?
            # For now, add to current segment if it exists, otherwise skip.
            if current_conversation:
                current_conversation.append(current_msg)
            continue

        # 1. Check for change in author
        author_changed = current_msg["author"] != prev_msg["author"]

        # 2. Check for timeout
        time_diff_seconds = (current_msg["timestamp"] - prev_msg["timestamp"]).total_seconds()
        timeout_exceeded = time_diff_seconds > timeout_seconds

        # 3. Check for semantic similarity (if model is loaded)
        #    A new segment is started if similarity is LOW (i.e., < threshold)
        #    This condition is only relevant if the author is the SAME and timeout is NOT exceeded.
        #    If author changes or timeout exceeded, those usually take precedence to start a new segment.
        semantically_different = False
        if model and not author_changed and not timeout_exceeded and prev_msg["text"] and current_msg["text"]:
            try:
                embedding_prev = model.encode(prev_msg["text"], convert_to_tensor=True)
                embedding_current = model.encode(current_msg["text"], convert_to_tensor=True)
                cosine_similarity = util.cos_sim(embedding_prev, embedding_current).item()

                if cosine_similarity < similarity_threshold:
                    semantically_different = True
                    # print(f"Debug: Semantically different. Prev: '{prev_msg['text'][:30]}', Curr: '{current_msg['text'][:30]}', Sim: {cosine_similarity:.2f}")
            except Exception as e:
                print(f"Error during semantic similarity calculation: {e}")
                # If encoding/similarity fails, assume not different to avoid unintended splits

        # Decision to start a new conversation segment
        if author_changed or timeout_exceeded or semantically_different:
            if current_conversation: # Ensure current_conversation is not empty before appending
                conversations.append(current_conversation)
            current_conversation = [current_msg] # Start new conversation
        else:
            current_conversation.append(current_msg) # Continue current conversation

    # Add the last ongoing conversation
    if current_conversation:
        conversations.append(current_conversation)

    print(f"Segmented {len(messages)} messages into {len(conversations)} conversations.")
    return conversations

if __name__ == '__main__':
    print("\n--- Testing src/segmentation.py ---")

    # Mock messages (ensure they are sorted by timestamp)
    # Note: Timestamps must be datetime objects for timedelta calculations
    mock_messages = [
        {"timestamp": datetime.datetime(2023, 1, 1, 10, 0, 0), "author": "UserA", "text": "Hello, is anyone there?"},
        {"timestamp": datetime.datetime(2023, 1, 1, 10, 0, 30), "author": "UserA", "text": "I need help with my account."}, # Similar, same author, no timeout
        {"timestamp": datetime.datetime(2023, 1, 1, 10, 1, 0), "author": "UserB", "text": "Hi UserA, I can help."}, # Author change
        {"timestamp": datetime.datetime(2023, 1, 1, 10, 1, 30), "author": "UserB", "text": "What seems to be the problem?"}, # Same author, no timeout
        {"timestamp": datetime.datetime(2023, 1, 1, 10, 8, 0), "author": "UserB", "text": "Are you still there?"}, # Timeout (assuming TIMEOUT_MINUTES = 5)
        {"timestamp": datetime.datetime(2023, 1, 1, 10, 8, 30), "author": "UserA", "text": "Yes, sorry. My internet was down."}, # Author change
        {"timestamp": datetime.datetime(2023, 1, 1, 10, 9, 0), "author": "UserA", "text": "Now, about that account issue..."}, # Same author, no timeout
        {"timestamp": datetime.datetime(2023, 1, 1, 10, 9, 5), "author": "UserA", "text": "I want to talk about something completely different now, like the weather."}, # Semantically different (potentially)
        {"timestamp": datetime.datetime(2023, 1, 1, 10, 9, 10), "author": "UserA", "text": "The sky is blue today."}, # Similar to previous one by UserA
    ]

    if model is None:
        print("Skipping segmentation test as SentenceTransformer model could not be loaded.")
    else:
        # Override settings for predictable test if needed
        # settings.TIMEOUT_MINUTES = 5 (already default)
        # settings.SEMANTIC_SIMILARITY_THRESHOLD = 0.7 (already default from new settings.py)

        segmented_conversations = segment(mock_messages)

        print(f"\n--- Segmented Conversations ({len(segmented_conversations)}) ---")
        for i, conv in enumerate(segmented_conversations):
            print(f"Conversation {i+1}:")
            for msg in conv:
                ts_str = msg['timestamp'].strftime('%H:%M:%S')
                print(f"  {ts_str} {msg['author']}: {msg['text']}")
            print("-" * 20)

        # Expected segmentation based on logic:
        # Conv 1: UserA (2 messages) - ends due to author change
        # Conv 2: UserB (1 message) - ends due to author change (prev logic) or timeout (current logic with prev_msg)
        # Conv 3: UserB (1 message) - ends due to timeout
        # Conv 4: UserA (1 message) - ends due to author change
        # Conv 5: UserA (1 message) - ends due to semantic diff
        # Conv 6: UserA (2 messages)
        # This depends heavily on actual similarity scores and exact timeout interpretations.
        # The provided example in the plan:
        # if msg["author"] != prev["author"] or time_diff>TIMEOUT_MINUTES or sim<0.7:
        #    convs.append(current); current = []
        # This implies `prev` is the direct previous message, not the start of the segment. My logic uses messages[i-1].

    print("--- Finished testing src/segmentation.py ---")
