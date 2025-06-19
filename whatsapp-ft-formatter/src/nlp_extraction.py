# src/nlp_extraction.py
import spacy
from spacy.tokens import Doc
from typing import Dict, Any, List
from config import settings

# Load the SpaCy model
# This can take a moment when first called.
NLP_MODEL_NAME = settings.SPACY_MODEL
print(f"Loading SpaCy model: {NLP_MODEL_NAME}...")
try:
    nlp = spacy.load(NLP_MODEL_NAME)
    print(f"SpaCy model '{NLP_MODEL_NAME}' loaded successfully.")
except OSError as e:
    print(f"Error loading SpaCy model '{NLP_MODEL_NAME}': {e}")
    print(f"Please ensure the model is downloaded (e.g., python -m spacy download {NLP_MODEL_NAME})")
    # Fallback to a blank model or raise an error
    # Using a blank model will limit entity extraction capabilities significantly.
    nlp = spacy.blank(NLP_MODEL_NAME.split('_')[0]) # e.g., spacy.blank('en')
    print(f"Fell back to a blank SpaCy model for language '{NLP_MODEL_NAME.split('_')[0]}'. Entity extraction will be minimal.")


def extract_entities(text: str) -> Dict[str, Any]:
    """
    Extracts named entities, and provides a basic intent structure from text using SpaCy.

    Args:
        text (str): The input message text.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - "intent": An empty string (or a very basic derived intent if logic is added).
            - "entities": A dictionary of extracted entities (label: text).
            - "confidence": A dummy confidence score (1.0).
                          (Actual confidence scoring for intent/entities is complex).
    """
    if not text or not nlp:
        return {"intent": "", "entities": {}, "confidence": 0.0}

    doc: Doc = nlp(text)

    entities: Dict[str, List[str]] = {} # Changed to List[str] to store multiple entities of the same type
    for ent in doc.ents:
        if ent.label_ not in entities:
            entities[ent.label_] = []
        entities[ent.label_].append(ent.text)

    # Basic intent detection (example placeholder - can be significantly expanded)
    # This is a very naive example. Real intent detection requires more sophisticated methods.
    intent_keywords = {
        "greeting": ["hello", "hi", "hey"],
        "farewell": ["bye", "goodbye"],
        "balance_inquiry": ["balance", "how much", "account status"],
        "problem_report": ["problem", "issue", "not working", "error"]
    }
    detected_intent = ""
    # Default confidence, can be adjusted based on rules or model if a proper intent model is used
    confidence = 0.5

    # Simple keyword-based intent (first match wins)
    # For multiple entities of the same type, they are now collected in a list.
    # For intent, we'll just take the first one found for simplicity.
    for intent_label, keywords in intent_keywords.items():
        if any(keyword in text.lower() for keyword in keywords):
            detected_intent = intent_label
            confidence = 0.75 # Higher confidence for keyword match
            break

    # If no specific intent found, but there are entities, maybe it's an "inform" intent
    if not detected_intent and entities:
        detected_intent = "inform"
        confidence = 0.6
    elif not detected_intent and not entities: # No intent, no entities
        detected_intent = "general_statement" # Or ""
        confidence = 0.4


    return {
        "intent": detected_intent,
        "entities": entities,
        "confidence": confidence
    }

if __name__ == '__main__':
    print("\n--- Testing src/nlp_extraction.py ---")

    sample_texts = [
        "Hello, I would like to know my account balance for tomorrow.",
        "I have an issue with my card, it's not working since last Tuesday.",
        "What is the weather like on 25th December 2024?",
        "The meeting is scheduled for 3 PM next Friday.",
        "Can you process a payment of 500 euros?",
        "Thanks, goodbye!",
        "Just a random statement without obvious entities.",
        "The quick brown fox jumps over the lazy dog." # No entities, general statement
    ]

    if nlp.meta.get("name", "generic") == "generic" and not nlp.pipe_names: # Check if it's a truly blank model
        print("SpaCy model is blank. Entity extraction will be very limited or non-existent in tests.")

    for text_input in sample_texts:
        extraction_result = extract_entities(text_input)
        print(f"\nInput Text: \"{text_input}\"")
        print(f"  Intent: {extraction_result['intent']} (Confidence: {extraction_result['confidence']:.2f})")
        print(f"  Entities: {extraction_result['entities']}")

    # Test with a known problematic case or specific entity types
    test_specific = "My phone number is +1-555-123-4567 and I want to book a flight for two people on August 15th."
    print(f"\nInput Text: \"{test_specific}\"")
    result_specific = extract_entities(test_specific)
    print(f"  Intent: {result_specific['intent']} (Confidence: {result_specific['confidence']:.2f})")
    print(f"  Entities: {result_specific['entities']}")
    # Note: SpaCy's en_core_web_sm might not pick up phone numbers as a distinct entity without custom rules.
    # It should pick up "two" as CARDINAL and "August 15th" as DATE.

    print("\n--- Finished testing src/nlp_extraction.py ---")
