# Architecture

This document describes the architecture of the WhatsApp Chat Finetuning Formatter.

## Overview

The pipeline consists of the following main components:

1.  **Input (`app.py`, `src/io_utils.py`)**: Handles chat file uploads via a Gradio interface and saves them.
2.  **Parsing (`src/parser.py`)**: Parses raw text from chat files into structured message objects.
3.  **Segmentation (`src/segmentation.py`)**: Groups messages into conversation segments using author changes, timeouts, and semantic similarity.
4.  **Role Assignment (`src/roles.py`)**: Assigns roles (client, agent, participant) to message authors.
5.  **NLP Extraction (`src/nlp_extraction.py`)**: Extracts named entities and basic intents from messages using SpaCy.
6.  **Formatting (`src/formatter.py`)**: Constructs the final JSON output objects according to a defined schema. This includes summaries, topics, and final requests.
7.  **Validation (`src/validator.py`)**: Validates the generated JSON objects against `schema.json`.
8.  **GCS Integration (`config/gcs_bucket.py`)**: Handles uploading the processed JSON files to Google Cloud Storage.
9.  **Configuration (`config/settings.py`)**: Manages all application settings and parameters.

## Data Flow

\`\`\`mermaid
graph TD
    A[User uploads .txt chat file] --> B(app.py - Gradio UI);
    B --> C{src/io_utils.py - Save Upload};
    C --> D{src/parser.py - Parse Text};
    D --> E{src/segmentation.py - Segment Conversations};
    E --> F{src/roles.py - Assign Roles};
    E --> G{src/nlp_extraction.py - Extract Entities/Intents};
    F --> H{src/formatter.py - Build JSON};
    G --> H;
    E --> H;
    H --> I{src/validator.py - Validate JSON};
    I -- Valid JSON --> J{config/gcs_bucket.py - Upload to GCS};
    I -- Invalid JSON --> K[Log Error / Output for Review];
    B -- Displays Log & Output --> A;
    J --> L[JSON in GCS];
\`\`\`

Further details on each module can be found in their respective source files.
