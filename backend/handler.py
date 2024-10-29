from typing import List, Optional
from PIL import Image
import io
import base64
import os
from OmniGen import OmniGenPipeline
import time
import runpod


# backend/main.py

# Set the absolute path to the model directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # project root
MODEL_DIR = os.path.join(BASE_DIR, "model_files")  # absolute path to model_files

# Load the OmniGen model pipeline from the local directory
try:
    pipe = OmniGenPipeline.from_pretrained(MODEL_DIR)
    print("Model loaded successfully")
except Exception as e:
    raise RuntimeError(f"Failed to load the model: {e}")

def handler(job):
    """ Handler function that will be used to process jobs. """
    try:
        job_input = job['input']
        prompt = job_input['prompt']
        height = job_input.get('height', 512)
        width = job_input.get('width', 512)
        guidance_scale = job_input.get('guidance_scale', 2.5)
        img_guidance_scale = job_input.get('img_guidance_scale', None)
        seed = job_input.get('seed', 0)
        input_images = job_input.get('input_images', None)

        if input_images:
            # Load images from base64 strings
            loaded_images = []
            for image_data in input_images:
                image_bytes = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                loaded_images.append(image)

            # Create placeholders for each image
            placeholders = " ".join(
                [f"<img><|image_{i+1}|></img>" for i in range(len(loaded_images))]
            )
            formatted_prompt = f"{prompt} {placeholders}"

            # Generate images using the pipeline
            time_start = time.time()
            images = pipe(
                prompt=formatted_prompt,
                input_images=loaded_images,
                height=height,
                width=width,
                guidance_scale=guidance_scale,
                img_guidance_scale=img_guidance_scale or 1.0,
                seed=seed,
            )
            print(f"Time taken: {time.time() - time_start}")
        else:
            # Generate images using only the prompt
            time_start = time.time()
            images = pipe(
                prompt=prompt,
                height=height,
                width=width,
                guidance_scale=guidance_scale,
                seed=seed,
            )
            print(f"Time taken: {time.time() - time_start}")

        # Convert the first image to a base64 string
        img = images[0]
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        image_bytes = buffer.getvalue()

        return base64.b64encode(image_bytes).decode('utf-8')

    except Exception as e:
        raise Exception(f"Image generation failed: {e}")

runpod.serverless.start({"handler": handler})

