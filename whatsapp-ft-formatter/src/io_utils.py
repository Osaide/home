# src/io_utils.py

import os
import uuid
from typing import List, IO
from config import settings

def save_upload(gr_files: List[IO]) -> List[str]:
    """
    Saves uploaded files (from Gradio gr.Files) to the raw data directory.
    Ensures unique filenames to prevent overwrites.

    Args:
        gr_files (List[IO]): A list of file-like objects, typically from gr.Files().
                             Each object has a .name attribute for the original filename.

    Returns:
        List[str]: A list of local file paths where the uploaded files were saved.
    """
    saved_file_paths = []

    if not gr_files:
        print("No files provided to save.")
        return saved_file_paths

    # Ensure the raw data directory exists
    raw_dir = settings.RAW_DATA_DIR
    if not os.path.exists(raw_dir):
        os.makedirs(raw_dir)
        print(f"Created directory: {raw_dir}")

    for uploaded_file in gr_files:
        if hasattr(uploaded_file, 'name'):
            original_filename = os.path.basename(uploaded_file.name)
            # Create a unique filename to avoid collisions
            unique_id = uuid.uuid4().hex[:8]
            filename, file_extension = os.path.splitext(original_filename)
            # It's important that Gradio provides temp files that can be read directly.
            # The 'uploaded_file' object itself is the temporary file path.
            temp_file_path = uploaded_file.name # Gradio's IO object's name attribute is the temp path

            # Construct the new path in our data/raw directory
            # We need to ensure the filename is safe and doesn't cause issues
            safe_filename = f"{filename}_{unique_id}{file_extension}"
            destination_path = os.path.join(raw_dir, safe_filename)

            try:
                # Read from the temp file and write to the destination
                with open(temp_file_path, 'rb') as src_f:
                    with open(destination_path, 'wb') as dest_f:
                        dest_f.write(src_f.read())

                saved_file_paths.append(destination_path)
                print(f"Successfully saved '{original_filename}' to '{destination_path}'")
            except Exception as e:
                print(f"Error saving file '{original_filename}' to '{destination_path}': {e}")
                # Decide if you want to skip this file or raise an error
        else:
            print(f"Uploaded file object does not have a 'name' attribute: {uploaded_file}")

    return saved_file_paths

if __name__ == '__main__':
    # Example Usage (for testing purposes)
    # This requires creating mock Gradio file objects, which is a bit complex.
    # For simplicity, we'll simulate by creating dummy files and then "uploading" them.

    print("Testing io_utils.save_upload...")

    # Create dummy raw data directory if it doesn't exist
    if not os.path.exists(settings.RAW_DATA_DIR):
        os.makedirs(settings.RAW_DATA_DIR)

    # Create some dummy files to "upload"
    mock_files_to_upload_paths = []
    for i in range(2):
        temp_path = f"temp_chat_{i}.txt"
        with open(temp_path, "w") as f:
            f.write(f"This is dummy chat content for file {i}.")
        mock_files_to_upload_paths.append(temp_path)

    # Mock Gradio file objects (very simplified)
    # In reality, Gradio provides tempfile.NamedTemporaryFile objects
    class MockGradioFile:
        def __init__(self, path):
            self.name = path # .name attribute holds the path to the temp file

    mock_gr_files = [MockGradioFile(p) for p in mock_files_to_upload_paths]

    if mock_gr_files:
        saved_paths = save_upload(mock_gr_files)
        print("
Files saved to:")
        for path in saved_paths:
            print(path)
            # Verify content (optional)
            # with open(path, "r") as f_check:
            # print(f" Content: {f_check.read()[:30]}...")

        # Clean up dummy raw files (optional, for repeated testing)
        # for p_saved in saved_paths:
        #     if os.path.exists(p_saved):
        #         os.remove(p_saved)
    else:
        print("No mock files created for testing.")

    # Clean up initial temp files
    for temp_p in mock_files_to_upload_paths:
        if os.path.exists(temp_p):
            os.remove(temp_p)

    print("
Finished testing io_utils.")
