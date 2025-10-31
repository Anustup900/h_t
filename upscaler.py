import os
import logging
import sys
from comfy_api_simplified import ComfyApiWrapper, ComfyWorkflowWrapper

# ========================
# CONFIG
# ========================
INPUT_FOLDER = "NB"      # folder with input images
OUTPUT_FOLDER = "output"    # folder to save results
WORKFLOW_JSON = "HB_upscaler_final_v3_api.json"
COMFY_API_URL = "http://0.0.0.0:7860/"
LOAD_NODE_NAME = "load_image_input"      # name of the image load node
OUTPUT_NODE_NAME = "output_to_save"    # name of the output node
# ========================

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# Initialize API + Workflow
api = ComfyApiWrapper(COMFY_API_URL)
wf = ComfyWorkflowWrapper(WORKFLOW_JSON)

# Get all image files in the folder
valid_exts = (".png", ".jpg", ".jpeg", ".webp")
image_files = [f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith(valid_exts)]

if not image_files:
    print("⚠️ No image files found in the input folder.")
    sys.exit()

# Process each image one by one
for image_name in sorted(image_files):
    input_path = os.path.join(INPUT_FOLDER, image_name)
    print(f"🔹 Processing: {image_name}")

    # Upload image to Comfy server
    image_metadata = api.upload_image(input_path)

    # Set uploaded image as input to workflow
    wf.set_node_param(LOAD_NODE_NAME, "image", f"{image_metadata['subfolder']}/{image_metadata['name']}")

    # Run the workflow
    results = api.queue_and_wait_images(wf, output_node_title=OUTPUT_NODE_NAME)

    # Save outputs
    for filename, image_data in results.items():
        output_path = os.path.join(OUTPUT_FOLDER, f"{os.path.splitext(image_name)[0]}_{filename}")
        with open(output_path, "wb+") as f:
            f.write(image_data)
        print(f"✅ Saved: {output_path}")

print("🎉 All images processed successfully!")
