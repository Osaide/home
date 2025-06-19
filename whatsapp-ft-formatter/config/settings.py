# config/settings.py
import os

# Timeout for segmentation in minutes
TIMEOUT_MINUTES = int(os.environ.get('TIMEOUT_MINUTES', '5'))

# Minimum message length to be considered valid
MIN_MESSAGE_LENGTH = int(os.environ.get('MIN_MESSAGE_LENGTH', '2'))

# Google Cloud Storage bucket name
# This can be overridden by an environment variable GCS_BUCKET_NAME
GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME", "<YOUR_BUCKET>")

# Path to Google Cloud credentials JSON file
# This can be overridden by an environment variable GOOGLE_APPLICATION_CREDENTIALS
GCP_CREDENTIALS_PATH = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json") # Path relative to project root

# Default SpaCy model for NLP tasks
SPACY_MODEL = os.environ.get("SPACY_MODEL", "en_core_web_sm")

# Default Sentence Transformer model for semantic segmentation
SENTENCE_TRANSFORMER_MODEL = os.environ.get("SENTENCE_TRANSFORMER_MODEL", "all-MiniLM-L6-v2")

# Threshold for semantic similarity in segmentation (0.0 to 1.0)
SEMANTIC_SIMILARITY_THRESHOLD = float(os.environ.get('SEMANTIC_SIMILARITY_THRESHOLD', '0.7')) # As per new plan's segmentation example

# Path to the JSON schema for validation (relative to project root)
SCHEMA_PATH = os.environ.get("SCHEMA_PATH", "schema.json")

# Raw data directory (relative to project root)
RAW_DATA_DIR = os.environ.get("RAW_DATA_DIR", "data/raw/")

# Processed data directory (relative to project root)
PROCESSED_DATA_DIR = os.environ.get("PROCESSED_DATA_DIR", "data/processed/")

# Maximum number of tokens/characters for summary (adjust as needed)
MAX_SUMMARY_LENGTH = int(os.environ.get('MAX_SUMMARY_LENGTH', '150')) # Character length for simple summary

# Ensure data directories exist
if not os.path.exists(RAW_DATA_DIR):
    os.makedirs(RAW_DATA_DIR)
if not os.path.exists(PROCESSED_DATA_DIR):
    os.makedirs(PROCESSED_DATA_DIR)

print(f"Settings loaded: GCS_BUCKET_NAME='{GCS_BUCKET_NAME}', TIMEOUT_MINUTES='{TIMEOUT_MINUTES}'")
