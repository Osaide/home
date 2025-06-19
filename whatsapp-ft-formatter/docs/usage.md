# Usage Guide

This guide explains how to set up, run, and use the WhatsApp Chat Finetuning Formatter.

## Prerequisites

*   Python 3.9+
*   Git
*   Google Cloud SDK (optional, for GCS integration)
*   Access to a Google Cloud Storage bucket (optional)

## Setup

1.  **Clone the Repository:**
    \`\`\`bash
    # Replace with your repository URL if you've cloned it elsewhere
    git clone <repository_url>
    cd whatsapp-ft-formatter
    \`\`\`

2.  **Install Dependencies:**
    \`\`\`bash
    pip install -r requirements.txt
    python -m spacy download en_core_web_sm
    \`\`\`

3.  **Configure Google Cloud Storage (Optional):**
    *   Ensure you have a `credentials.json` file for a GCP service account with Storage permissions.
    *   Set the following environment variables (e.g., in your shell or a \`.env\` file if you adapt the app to load it):
        \`\`\`bash
        export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/credentials.json"
        export GCS_BUCKET_NAME="your-gcs-bucket-name"
        \`\`\`
    *   Alternatively, these can be set as secrets in your Hugging Face Space. The `GCS_BUCKET_NAME` can also be set in `config/settings.py` as a default, but environment variables take precedence.

## Running Locally

1.  **Navigate to the project directory.**
2.  **Ensure environment variables are set if using GCS.**
3.  **Run the Gradio application:**
    \`\`\`bash
    python app.py
    \`\`\`
4.  Open your web browser and go to the local address provided by Gradio (usually `http://127.0.0.1:7860`).
5.  Upload your WhatsApp chat `.txt` files and click "Process Chats".

## Deployment on Hugging Face Spaces

1.  **Create a new Space on Hugging Face.**
    *   Choose "Gradio" as the SDK.
    *   Connect your GitHub repository (or upload files manually).
2.  **Configure Secrets:**
    *   In your Space settings, add the following secrets if you intend to use GCS:
        *   `GOOGLE_APPLICATION_CREDENTIALS`: Paste the content of your `credentials.json` file.
        *   `GCS_BUCKET_NAME`: Your GCS bucket name.
3.  The application should build and deploy. Access it via the public URL provided by Hugging Face.

## Output

*   **Logs:** The Gradio interface will display processing logs.
*   **JSON Output:** The structured JSON data will be displayed in the interface.
*   **Local File:** A JSON file containing the output is saved to the `data/processed/` directory locally.
*   **GCS:** If configured and validation passes, the JSON files (one per dialog) will be uploaded to the specified GCS bucket in a timestamped folder.
