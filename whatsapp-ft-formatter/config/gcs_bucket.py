# config/gcs_bucket.py
import os
import json # For uploading JSON objects directly
from google.cloud import storage
from google.oauth2 import service_account
from config import settings

def get_gcs_client():
    """Initializes and returns a GCS client."""
    credentials_path = settings.GCP_CREDENTIALS_PATH

    # Try to use service account credentials if the file exists
    if os.path.exists(credentials_path):
        try:
            credentials = service_account.Credentials.from_service_account_file(credentials_path)
            client = storage.Client(credentials=credentials, project=credentials.project_id)
            print(f"GCS client initialized using credentials from: {credentials_path}")
            return client
        except Exception as e:
            print(f"Failed to initialize GCS client with {credentials_path}: {e}. Falling back to default.")

    # Fallback to default credentials (e.g., for GCE, Cloud Run, or local gcloud auth)
    try:
        client = storage.Client()
        print("GCS client initialized using default credentials.")
        return client
    except Exception as e:
        print(f"Failed to initialize GCS client with default credentials: {e}")
        raise # Or handle more gracefully depending on desired behavior

def create_bucket_if_not_exists(name: str, location: str = "europe-west1"): # Added location as per new plan's example
    """
    Creates a Google Cloud Storage bucket if it does not already exist.
    Args:
        name (str): The name of the bucket to create.
        location (str): The location/region for the bucket.
    """
    client = get_gcs_client()
    try:
        bucket = client.get_bucket(name)
        print(f"Bucket '{name}' already exists in location '{bucket.location}'.")
    except storage.exceptions.NotFound:
        print(f"Bucket '{name}' not found. Creating new bucket in location '{location}'...")
        try:
            bucket = client.create_bucket(name, location=location)
            print(f"Bucket '{name}' created successfully in location '{location}'.")
        except Exception as e:
            print(f"Error creating bucket '{name}': {e}")
            # Depending on strictness, you might want to raise e here
    except Exception as e:
        print(f"Error checking bucket '{name}': {e}")
        # Depending on strictness, you might want to raise e here

def upload_file(local_path: str, remote_path: str, bucket_name: str): # As per new plan
    """
    Uploads a local file to the specified GCS bucket.
    Args:
        local_path (str): The path to the local file to upload.
        remote_path (str): The desired path (blob name) in the GCS bucket.
        bucket_name (str): The name of the GCS bucket.
    Returns:
        str: The GCS URI of the uploaded file (e.g., gs://bucket_name/remote_path), or None on failure.
    """
    if not bucket_name or bucket_name == "<YOUR_BUCKET>":
        print(f"Invalid bucket name: '{bucket_name}'. Skipping GCS upload.")
        return None

    client = get_gcs_client()
    try:
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(remote_path)

        print(f"Uploading '{local_path}' to 'gs://{bucket_name}/{remote_path}'...")
        blob.upload_from_filename(local_path)
        print(f"File '{local_path}' uploaded successfully to 'gs://{bucket_name}/{remote_path}'.")
        return f"gs://{bucket_name}/{remote_path}"
    except FileNotFoundError:
        print(f"Local file '{local_path}' not found. Cannot upload to GCS.")
        return None
    except Exception as e:
        print(f"Error uploading file '{local_path}' to bucket '{bucket_name}': {e}")
        return None

def upload_json_objects(json_objs: list, remote_folder: str, bucket_name: str):
    """
    Uploads a list of JSON objects to GCS. Each object is saved as a separate file.
    This is an alternative to uploading a single file if app.py provides a list of JSONs.
    The new plan for app.py seems to suggest `gcs_bucket.upload(json_objs, ...)`
    which implies uploading the list itself or each item. This function handles each item.
    If a single file containing all JSON objects is needed, another function or modification is required.

    Args:
        json_objs (list): A list of serializable JSON objects (dictionaries).
        remote_folder (str): The folder in GCS where JSON files will be stored.
        bucket_name (str): The name of the GCS bucket.
    Returns:
        List[str]: A list of GCS URIs for the uploaded files.
    """
    if not bucket_name or bucket_name == "<YOUR_BUCKET>":
        print(f"Invalid bucket name: '{bucket_name}'. Skipping GCS upload of JSON objects.")
        return []

    client = get_gcs_client()
    uploaded_uris = []

    for i, obj_data in enumerate(json_objs):
        # Determine a filename, e.g., based on dialog_id or index
        dialog_id = obj_data.get('dialog_id', f'object_{i}')
        remote_filename = f"{dialog_id}.json"
        full_remote_path = os.path.join(remote_folder, remote_filename)

        try:
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(full_remote_path)

            print(f"Uploading JSON object for '{dialog_id}' to 'gs://{bucket_name}/{full_remote_path}'...")
            # Serialize dict to JSON string and upload
            blob.upload_from_string(
                data=json.dumps(obj_data, indent=2),
                content_type='application/json'
            )
            print(f"JSON object for '{dialog_id}' uploaded successfully.")
            uploaded_uris.append(f"gs://{bucket_name}/{full_remote_path}")

        except Exception as e:
            print(f"Error uploading JSON object for '{dialog_id}' to bucket '{bucket_name}': {e}")
            # Decide if one failure should stop all: probably not, just skip and report.

    return uploaded_uris


if __name__ == '__main__':
    # Basic Test (requires GOOGLE_APPLICATION_CREDENTIALS to be set up for your environment)
    print("\n--- GCS Bucket Basic Test ---")
    test_bucket = settings.GCS_BUCKET_NAME
    if not test_bucket or test_bucket == "<YOUR_BUCKET>":
        print("GCS_BUCKET_NAME is not set in config/settings.py or environment. Using a default test name.")
        # IMPORTANT: For real tests, use a dedicated test bucket name
        test_bucket = "your-unique-test-bucket-name-123abc" # Replace or ensure this is set via env for testing

    print(f"Using test bucket: {test_bucket}")

    # Test bucket creation (idempotent)
    create_bucket_if_not_exists(test_bucket, location="us-central1") # Use a common location for testing

    # Create a dummy local file for upload test
    dummy_local_file = "test_upload.txt"
    with open(dummy_local_file, "w") as f:
        f.write("This is a test file for GCS upload.")

    # Test file upload
    remote_file_name = f"test_data/{dummy_local_file}"
    gcs_uri = upload_file(dummy_local_file, remote_file_name, test_bucket)
    if gcs_uri:
        print(f"Test file uploaded to: {gcs_uri}")
    else:
        print("Test file upload failed.")

    # Test JSON object upload
    sample_json_objs = [
        {"dialog_id": "sample1", "messages": [{"role": "user", "text": "Hello"}]},
        {"dialog_id": "sample2", "messages": [{"role": "agent", "text": "Hi there"}]}
    ]
    json_uris = upload_json_objects(sample_json_objs, "test_json_outputs", test_bucket)
    if json_uris:
        print(f"JSON objects uploaded to: {json_uris}")
    else:
        print("JSON object upload failed or produced no URIs.")

    # Clean up local dummy file
    if os.path.exists(dummy_local_file):
        os.remove(dummy_local_file)

    print("--- GCS Bucket Test Complete ---")
