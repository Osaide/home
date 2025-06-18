# config/settings.py

# Timeout for segmentation in minutes
TIMEOUT_MINUTES = 5

# Minimum message length to be considered valid (e.g., for parser or NLP)
MIN_MESSAGE_LENGTH = 2

# Google Cloud Storage bucket name
# This can be overridden by an environment variable GCS_BUCKET_NAME
GCS_BUCKET_NAME = "<YOUR_BUCKET>"  # Replace with your actual bucket name or leave as a placeholder

# Path to Google Cloud credentials JSON file
# This can be overridden by an environment variable GOOGLE_APPLICATION_CREDENTIALS
GCP_CREDENTIALS_PATH = "credentials.json"

# Default SpaCy model for NLP tasks
SPACY_MODEL = "en_core_web_sm" # Consider making this configurable if multiple languages are needed

# Default Sentence Transformer model for semantic segmentation
SENTENCE_TRANSFORMER_MODEL = "all-MiniLM-L6-v2"

# Threshold for semantic similarity in segmentation
SEMANTIC_SIMILARITY_THRESHOLD = 0.5 # This might need tuning

# Path to the JSON schema for validation
SCHEMA_PATH = "schema.json"

# Raw data directory
RAW_DATA_DIR = "data/raw/"

# Processed data directory
PROCESSED_DATA_DIR = "data/processed/"

# Maximum number of tokens for summary
MAX_SUMMARY_TOKENS = 150
