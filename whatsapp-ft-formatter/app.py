# app.py
import gradio as gr
import os
import json # For saving the final JSON output locally if needed
import time # For unique output filenames
from typing import List, Dict, Any, Tuple

# Import configurations and utility functions
from config import settings
from config import gcs_bucket

# Import core processing modules from src
from src import io_utils
from src import parser
from src import segmentation
from src import roles
from src import nlp_extraction
from src import formatter
from src import validator

# Ensure processed_data directory exists for local JSON output
if not os.path.exists(settings.PROCESSED_DATA_DIR):
    os.makedirs(settings.PROCESSED_DATA_DIR)

def process_uploaded_chats(files_list: List[gr. gradio_typing.FileValue]) -> Tuple[str, str, List[Dict[str, Any]]]:
    """
    Main pipeline function to process uploaded WhatsApp chat files.
    Takes a list of file objects from Gradio, processes them, and returns status and results.
    """
    if not files_list:
        return "No files uploaded. Please upload .txt chat files.", "", []

    log_messages = ["Pipeline started..."]

    # 1. Save uploaded files
    log_messages.append("Step 1/8: Saving uploaded files...")
    print("Uploaded file objects:", files_list)

    # My earlier io_utils.save_upload expects Gradio FileValue objects.
    saved_raw_file_paths = io_utils.save_upload(files_list) # type: ignore
    if not saved_raw_file_paths:
        log_messages.append("Error: Failed to save uploaded files via io_utils.save_upload.")
        return "\n".join(log_messages), "", []
    log_messages.append(f"Saved {len(saved_raw_file_paths)} files to data/raw: {saved_raw_file_paths}")
    paths_to_parse = saved_raw_file_paths


    # 2. Parse TXT files
    log_messages.append("\nStep 2/8: Parsing chat files...")
    parsed_messages = parser.parse_txt(paths_to_parse)
    if not parsed_messages:
        log_messages.append("Error: No messages parsed. Check file content and format.")
        return "\n".join(log_messages), "", []
    log_messages.append(f"Parsed {len(parsed_messages)} messages.")

    # 3. Segment conversations
    log_messages.append("\nStep 3/8: Segmenting conversations...")
    segmented_conversations = segmentation.segment(parsed_messages)
    if not segmented_conversations:
        log_messages.append("Error: Failed to segment conversations.")
        return "\n".join(log_messages), "", []
    log_messages.append(f"Segmented into {len(segmented_conversations)} conversations.")

    # 4. Assign roles
    log_messages.append("\nStep 4/8: Assigning roles...")
    roles_map = roles.assign_roles(segmented_conversations)
    log_messages.append(f"Assigned roles: {roles_map}")

    # 5. NLP Extraction (for each message)
    log_messages.append("\nStep 5/8: Performing NLP extraction on messages...")
    all_nlp_extractions = []
    total_messages_for_nlp = sum(len(conv) for conv in segmented_conversations)
    count_nlp_done = 0
    for conv_idx, conv in enumerate(segmented_conversations):
        for msg_idx, message_data in enumerate(conv):
            # Ensure 'text' key exists, fallback to empty string if not
            text_to_extract = message_data.get("text", "")
            if not text_to_extract:
                 print(f"Warning: Message at Conv {conv_idx}, Msg {msg_idx} has no text. Skipping NLP.")
                 # Append a default empty extraction to maintain list alignment
                 all_nlp_extractions.append({"intent": "", "entities": {}, "confidence": 0.0})
            else:
                all_nlp_extractions.append(nlp_extraction.extract_entities(text_to_extract))
            count_nlp_done +=1
            # print(f"NLP processing: {count_nlp_done}/{total_messages_for_nlp}") # Progress log
    log_messages.append(f"Performed NLP extraction for {len(all_nlp_extractions)} messages.")
    if len(all_nlp_extractions) != total_messages_for_nlp:
        log_messages.append(f"Warning: Mismatch in NLP extractions ({len(all_nlp_extractions)}) vs total messages ({total_messages_for_nlp}).")


    # 6. Format to JSON
    log_messages.append("\nStep 6/8: Formatting to structured JSON...")
    final_json_objects = formatter.build_json(segmented_conversations, roles_map, all_nlp_extractions)
    if not final_json_objects:
        log_messages.append("Error: Failed to format JSON objects.")
        return "\n".join(log_messages), "", []
    log_messages.append(f"Formatted {len(final_json_objects)} JSON dialog objects.")

    # 7. Validate JSON
    log_messages.append("\nStep 7/8: Validating JSON objects against schema...")
    is_valid = validator.validate_json(final_json_objects) # Uses schema from settings by default
    if not is_valid:
        log_messages.append("Error: JSON validation failed. Check logs for details. Output will not be uploaded to GCS.")
        # Optionally, still return the invalid JSON for debugging, or an empty list.
        # For now, let's return the (potentially invalid) JSON for inspection.
    else:
        log_messages.append("JSON validation successful.")

    # 8. Upload to GCS (if valid and GCS is configured)
    output_gcs_uris = []
    if is_valid and settings.GCS_BUCKET_NAME and settings.GCS_BUCKET_NAME != "<YOUR_BUCKET>":
        log_messages.append(f"\nStep 8/8: Uploading valid JSON to GCS bucket '{settings.GCS_BUCKET_NAME}'...")

        upload_batch_folder = f"whatsapp_formatter_outputs/{time.strftime('%Y%m%d_%H%M%S')}"

        output_gcs_uris = gcs_bucket.upload_json_objects(
            json_objs=final_json_objects,
            remote_folder=upload_batch_folder,
            bucket_name=settings.GCS_BUCKET_NAME
        )

        if output_gcs_uris:
            log_messages.append(f"Successfully uploaded {len(output_gcs_uris)} files to GCS:")
            for uri in output_gcs_uris:
                log_messages.append(f"  - {uri}")
        else:
            log_messages.append("GCS upload did not return any URIs or failed. Check GCS bucket setup and permissions.")
    elif not is_valid:
        log_messages.append("\nStep 8/8: Skipped GCS upload due to JSON validation errors.")
    else:
        log_messages.append(f"\nStep 8/8: Skipped GCS upload (GCS_BUCKET_NAME not configured or is placeholder: '{settings.GCS_BUCKET_NAME}').")

    local_json_output_path = ""
    if final_json_objects:
        timestamp_str = time.strftime("%Y%m%d-%H%M%S")
        base_input_filename = "batch_upload"
        # Gradio FileValue has .name (abs path to temp file), .orig_name (original client-side name)
        if files_list and hasattr(files_list[0], 'orig_name') and files_list[0].orig_name:
            base_input_filename = os.path.splitext(os.path.basename(files_list[0].orig_name))[0]
        elif files_list and hasattr(files_list[0], 'name'): # fallback to temp file name if orig_name missing
            base_input_filename = os.path.splitext(os.path.basename(files_list[0].name))[0]


        local_filename = f"{base_input_filename}_{timestamp_str}_processed.json"
        local_json_output_path = os.path.join(settings.PROCESSED_DATA_DIR, local_filename)
        try:
            with open(local_json_output_path, 'w', encoding='utf-8') as f_out:
                json.dump(final_json_objects, f_out, indent=2)
            log_messages.append(f"\nOutput saved locally to: {local_json_output_path}")
        except Exception as e:
            log_messages.append(f"\nError saving output locally: {e}")
            local_json_output_path = "" # Reset if saving failed

    log_messages.append("\nPipeline finished.")
    return "\n".join(log_messages), local_json_output_path, final_json_objects


# --- Gradio Interface Definition ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# WhatsApp Chat Finetuning Formatter 💬📊")
    gr.Markdown(
        "Upload your WhatsApp chat .txt file(s) to process them into a structured JSON format, "
        "perform NLP analysis, and optionally upload to Google Cloud Storage."
    )

    with gr.Row():
        with gr.Column(scale=1):
            chat_uploader = gr.Files(
                label="Upload WhatsApp Chat Files (.txt)",
                file_types=[".txt"],
                file_count="multiple" # Allow multiple files
            )
            process_button = gr.Button("Process Chats", variant="primary")

        with gr.Column(scale=2):
            gr.Markdown("### Processing Log")
            log_output_textbox = gr.Textbox(lines=15, label="Logs", interactive=False, show_copy_button=True)

            gr.Markdown("### JSON Output")
            json_display_output = gr.JSON(label="Processed JSON Output", interactive=False)
            local_file_path_display = gr.Textbox(label="Local Output File Path (if saved)", interactive=False)


    process_button.click(
        fn=process_uploaded_chats,
        inputs=[chat_uploader],
        outputs=[log_output_textbox, local_file_path_display, json_display_output]
    )

    gr.Markdown("---")
    gr.Markdown("### Configuration Notes:")
    gr.Markdown(
        f"- **Timeout for Segmentation:** {settings.TIMEOUT_MINUTES} minutes\n"
        f"- **Semantic Similarity Threshold:** {settings.SEMANTIC_SIMILARITY_THRESHOLD}\n"
        f"- **GCS Bucket for Upload:** '{settings.GCS_BUCKET_NAME}' (Ensure this is configured in your environment if you want GCS upload)\n"
        f"- **SpaCy Model:** {settings.SPACY_MODEL}\n"
        f"- **Sentence Transformer Model:** {settings.SENTENCE_TRANSFORMER_MODEL}"
    )


if __name__ == "__main__":
    print("Launching Gradio App...")
    demo.launch(debug=True)
