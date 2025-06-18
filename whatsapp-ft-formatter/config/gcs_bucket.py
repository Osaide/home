# config/gcs_bucket.py

import os
from google.cloud import storage
from google.oauth2 import service_account
from config import settings # Assuming settings.py is in the same directory or accessible via PYTHONPATH

def get_gcs_client():
    """Initializes and returns a GCS client, trying credentials in order."""
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", settings.GCP_CREDENTIALS_PATH)

    if os.path.exists(credentials_path):
        credentials = service_account.Credentials.from_service_account_file(credentials_path)
        client = storage.Client(credentials=credentials)
        print(f"Using credentials from: {credentials_path}")
    else:
        # Fallback to default credentials if the JSON file is not found
        # This works in environments like Cloud Run, GKE, or local gcloud auth.
        client = storage.Client()
        print("Using default GCS credentials (e.g., from environment or gcloud auth).")
    return client

def create_bucket_if_not_exists(bucket_name: str, client: storage.Client = None):
    """
    Creates a Google Cloud Storage bucket if it does not already exist.

    Args:
        bucket_name (str): The name of the bucket to create.
        client (storage.Client, optional): GCS client. If None, a new one is initialized.
    """
    if not client:
        client = get_gcs_client()

    try:
        bucket = client.get_bucket(bucket_name)
        print(f"Bucket '{bucket_name}' already exists.")
    except storage.exceptions.NotFound:
        print(f"Bucket '{bucket_name}' not found. Creating new bucket...")
        # You might want to specify location, storage class, etc. for bucket creation
        # For simplicity, using default settings here.
        bucket = client.create_bucket(bucket_name)
        print(f"Bucket '{bucket_name}' created successfully.")
    except Exception as e:
        print(f"Error checking or creating bucket '{bucket_name}': {e}")
        raise

def upload_file(local_path: str, remote_path: str, bucket_name: str = None, client: storage.Client = None):
    """
    Uploads a file to the specified Google Cloud Storage bucket.

    Args:
        local_path (str): The local path to the file to upload.
        remote_path (str): The desired path (blob name) in the GCS bucket.
        bucket_name (str, optional): The name of the GCS bucket.
                                     If None, uses GCS_BUCKET_NAME from settings.
        client (storage.Client, optional): GCS client. If None, a new one is initialized.

    Returns:
        str: The public URL of the uploaded file, or None if upload fails.
    """
    if not client:
        client = get_gcs_client()

    actual_bucket_name = bucket_name or os.getenv("GCS_BUCKET_NAME", settings.GCS_BUCKET_NAME)

    if not actual_bucket_name or actual_bucket_name == "<YOUR_BUCKET>":
        print("GCS_BUCKET_NAME is not configured. Skipping upload.")
        return None

    try:
        if not os.path.exists(local_path):
            print(f"Local file '{local_path}' not found. Skipping upload.")
            return None

        bucket = client.bucket(actual_bucket_name)
        blob = bucket.blob(remote_path)

        print(f"Uploading '{local_path}' to 'gs://{actual_bucket_name}/{remote_path}'...")
        blob.upload_from_filename(local_path)
        print(f"File '{local_path}' uploaded successfully to 'gs://{actual_bucket_name}/{remote_path}'.")
        # Making the blob public for simplicity, consider ACLs for production
        # blob.make_public()
        # return blob.public_url
        return f"gs://{actual_bucket_name}/{remote_path}" # Return GCS URI

    except Exception as e:
        print(f"Error uploading file '{local_path}' to bucket '{actual_bucket_name}': {e}")
        # Optionally, re-raise the exception if you want the caller to handle it
        # raise
        return None

if __name__ == '__main__':
    # Example Usage (for testing purposes)
    # Ensure 'credentials.json' is in the correct path or GOOGLE_APPLICATION_CREDENTIALS is set
    # and GCS_BUCKET_NAME is set in settings.py or as an env var.

    # Create a dummy file to upload
    dummy_local_file = "dummy_upload_test.txt"
    with open(dummy_local_file, "w") as f:
        f.write("This is a test file for GCS upload.")

    test_bucket_name = os.getenv("GCS_BUCKET_NAME", settings.GCS_BUCKET_NAME)
    if test_bucket_name and test_bucket_name != "<YOUR_BUCKET>":
        print(f"Testing GCS functions with bucket: {test_bucket_name}")

        # Initialize client once
        gcs_client = get_gcs_client()

        # Test bucket creation
        create_bucket_if_not_exists(test_bucket_name, client=gcs_client)

        # Test file upload
        remote_file_path = f"test_uploads/{dummy_local_file}"
        gcs_uri = upload_file(dummy_local_file, remote_file_path, bucket_name=test_bucket_name, client=gcs_client)
        if gcs_uri:
            print(f"Test file uploaded to: {gcs_uri}")
        else:
            print("Test file upload failed.")

        # Clean up dummy file
        os.remove(dummy_local_file)
    else:
        print("GCS_BUCKET_NAME not set, skipping GCS function tests.")
        print("Please set GCS_BUCKET_NAME in config/settings.py or as an environment variable.")
