import os
import logging
import sys
from comfy_api_simplified import ComfyApiWrapper, ComfyWorkflowWrapper

# ========================
# CONFIG
# ========================
INPUT_FOLDER = "batch_second_HB"          # folder with input subfolders
OUTPUT_FOLDER = "batch_2_up"          # base folder for output results
WORKFLOW_JSON = "v4_final_hb_api.json"
COMFY_API_URL = "http://0.0.0.0:7860/"
LOAD_NODE_NAME = "load_image_input"  # name of the image load node
OUTPUT_NODE_NAME = "output_to_save"  # name of the output node
# ========================

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# Initialize API + Workflow
api = ComfyApiWrapper(COMFY_API_URL)
wf = ComfyWorkflowWrapper(WORKFLOW_JSON)

valid_exts = (".png", ".jpg", ".jpeg", ".webp")

# Walk through all subfolders
for root, _, files in os.walk(INPUT_FOLDER):
    image_files = [f for f in files if f.lower().endswith(valid_exts)]
    if not image_files:
        continue

    # Compute relative subfolder path (for preserving structure)
    rel_path = os.path.relpath(root, INPUT_FOLDER)
    output_subfolder = os.path.join(OUTPUT_FOLDER, rel_path)
    os.makedirs(output_subfolder, exist_ok=True)

    print(f"\n📂 Processing folder: {rel_path}")

    for image_name in sorted(image_files):
        base_name = os.path.splitext(image_name)[0]
        input_path = os.path.join(root, image_name)

        # Check if already processed
        already_done = any(f.startswith(base_name + "_") for f in os.listdir(output_subfolder))
        if already_done:
            print(f"⏭️ Skipping (already processed): {image_name}")
            continue

        print(f"🔹 Processing: {image_name}")

        try:
            # Upload image to Comfy server
            image_metadata = api.upload_image(input_path)

            # Set uploaded image as input to workflow
            wf.set_node_param(LOAD_NODE_NAME, "image", f"{image_metadata['subfolder']}/{image_metadata['name']}")

            # Run workflow
            results = api.queue_and_wait_images(wf, output_node_title=OUTPUT_NODE_NAME)

            # Save outputs to the same subfolder under OUTPUT_FOLDER
            for filename, image_data in results.items():
                output_path = os.path.join(output_subfolder, f"{base_name}_{filename}")
                with open(output_path, "wb+") as f:
                    f.write(image_data)
                print(f"✅ Saved: {output_path}")

        except Exception as e:
            print(f"❌ Error processing {image_name}: {e}")

print("\n🎉 All subfolders processed successfully (skipping completed ones)!")
