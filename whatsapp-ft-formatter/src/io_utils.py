# src/io_utils.py
import os
import uuid
from typing import List, IO, Any # IO for type hinting file objects
from config import settings

def save_upload(gr_files: List[Any]) -> List[str]: # Gradio gr.Files gives a list of tempfile._TemporaryFileWrapper
    """
    Saves uploaded files (from Gradio gr.Files) to the raw data directory.
    Ensures unique filenames to prevent overwrites.

    Args:
        gr_files (List[Any]): A list of file-like objects from gr.Files().
                              Each object is expected to have a .name attribute (path to temp file).

    Returns:
        List[str]: A list of local file paths in 'data/raw/' where files were saved.
    """
    saved_file_paths: List[str] = []

    if not gr_files:
        print("No files provided to io_utils.save_upload.")
        return saved_file_paths

    # Ensure the raw data directory exists
    raw_dir = settings.RAW_DATA_DIR
    if not os.path.exists(raw_dir):
        try:
            os.makedirs(raw_dir)
            print(f"Created directory: {raw_dir}")
        except OSError as e:
            print(f"Error creating directory {raw_dir}: {e}. Cannot save files.")
            return saved_file_paths


    for uploaded_file_obj in gr_files:
        if not hasattr(uploaded_file_obj, 'name') or not uploaded_file_obj.name:
            print(f"Warning: Uploaded file object is invalid or has no 'name' attribute: {uploaded_file_obj}")
            continue

        temp_file_path = uploaded_file_obj.name # This is the path to Gradio's temporary file

        # Get the original filename from the temp path if possible, or use a generic name
        # Gradio's temp files might not retain original client-side filename directly in .name
        # For gr.Files(type="file"), the object itself might have an 'orig_name' or similar,
        # but .name is the crucial path to the temp file.
        # Let's try to get original name if available, else make one up.
        original_filename = getattr(uploaded_file_obj, 'orig_name', None)
        if not original_filename:
            original_filename = os.path.basename(temp_file_path) # Fallback to temp file's name
            if not original_filename or '.' not in original_filename : # if basename is just random string
                 original_filename = "uploaded_file.txt" # Default if basename is not useful

        # Create a unique filename to avoid collisions in data/raw/
        unique_id = uuid.uuid4().hex[:8]
        filename_stem, file_extension = os.path.splitext(original_filename)
        # Sanitize filename_stem if necessary (e.g., remove tricky characters)
        safe_filename_stem = "".join(c if c.isalnum() or c in ('_', '-') else '_' for c in filename_stem)
        if not safe_filename_stem: safe_filename_stem = "file" # handle empty stem after sanitize

        safe_filename = f"{safe_filename_stem}_{unique_id}{file_extension if file_extension else '.txt'}"
        destination_path = os.path.join(raw_dir, safe_filename)

        try:
            # Read from the temp file and write to the destination
            # Gradio temp files should be openable in 'rb' mode.
            with open(temp_file_path, 'rb') as src_f:
                with open(destination_path, 'wb') as dest_f:
                    dest_f.write(src_f.read())

            saved_file_paths.append(destination_path)
            print(f"Successfully saved '{original_filename}' to '{destination_path}'")
        except Exception as e:
            print(f"Error saving file '{original_filename}' (from '{temp_file_path}') to '{destination_path}': {e}")
            # Decide if you want to skip this file or raise an error

    return saved_file_paths

if __name__ == '__main__':
    print("--- Testing src/io_utils.py ---")

    # Mock Gradio file objects for testing
    # In Gradio, these are typically tempfile._TemporaryFileWrapper
    class MockGradioFile:
        def __init__(self, temp_path: str, original_name: str = None):
            self.name = temp_path # Path to the temporary file on disk
            self.orig_name = original_name if original_name else os.path.basename(temp_path)

    # Create some dummy temporary files to act as "uploads"
    temp_dir = "temp_uploads_for_test"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    dummy_content1 = b"This is chat one."
    dummy_content2 = b"This is chat two with special chars !@#$%^&*().txt"

    temp_file1_path = os.path.join(temp_dir, "chat1_temp.txt")
    temp_file2_path = os.path.join(temp_dir, "chat2_temp_!@#.txt")

    with open(temp_file1_path, "wb") as f: f.write(dummy_content1)
    with open(temp_file2_path, "wb") as f: f.write(dummy_content2)

    mock_gr_files_list = [
        MockGradioFile(temp_file1_path, "my_chat_1.txt"),
        MockGradioFile(temp_file2_path, "another chat file with spaces.txt")
    ]

    # Test save_upload
    print("\nTesting save_upload function...")
    saved_paths = save_upload(mock_gr_files_list)

    assert len(saved_paths) == 2, f"Expected 2 files saved, got {len(saved_paths)}"
    print(f"Files saved to data/raw/: {saved_paths}")

    for spath in saved_paths:
        assert os.path.exists(spath), f"Saved path {spath} does not exist."
        # Verify content if necessary by reading from spath
        # For example, check if content matches dummy_content1 or dummy_content2
        # This requires knowing which saved_path corresponds to which input,
        # which might be tricky if names are heavily mangled.
        # For now, existence check is primary.

    print("\nVerifying content of saved files (simple check):")
    # This part is a bit more involved as save_upload changes names.
    # We can check if total bytes match or if one of the contents is present.
    raw_files_in_dir = [os.path.join(settings.RAW_DATA_DIR, f) for f in os.listdir(settings.RAW_DATA_DIR) if os.path.isfile(os.path.join(settings.RAW_DATA_DIR, f))]
    content1_found = False
    content2_found = False
    for rf_path in raw_files_in_dir:
        if rf_path in saved_paths: # Only check files created in this test run
            with open(rf_path, "rb") as f_read:
                content = f_read.read()
                if content == dummy_content1: content1_found = True
                if content == dummy_content2: content2_found = True

    assert content1_found, "Content of first dummy file not found in data/raw/"
    assert content2_found, "Content of second dummy file not found in data/raw/"
    print("Content verification passed for the two test files.")


    # Clean up: remove dummy temp files and directory, and files created in data/raw by this test
    print("\nCleaning up test files...")
    if os.path.exists(temp_file1_path): os.remove(temp_file1_path)
    if os.path.exists(temp_file2_path): os.remove(temp_file2_path)
    if os.path.exists(temp_dir): os.rmdir(temp_dir)
    for spath in saved_paths:
        if os.path.exists(spath):
            os.remove(spath)
            print(f"Removed test file: {spath}")

    print("--- Finished testing src/io_utils.py ---")
