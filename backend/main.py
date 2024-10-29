from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from typing import List, Optional
from PIL import Image
import io
import base64
import os

from OmniGen import OmniGenPipeline


# backend/main.py

# Initialize FastAPI app
app = FastAPI()

# Set the absolute path to the model directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # project root
MODEL_DIR = os.path.join(BASE_DIR, "model_files")  # absolute path to model_files

# Load the OmniGen model pipeline from the local directory
try:
    pipe = OmniGenPipeline.from_pretrained(MODEL_DIR)
    print("Model loaded successfully")
except Exception as e:
    raise RuntimeError(f"Failed to load the model: {e}")

# Define an endpoint to generate images
@app.post("/generate-image")
async def generate_image(
    prompt: str = Form(...),
    height: int = Form(512, ge=64, le=2048),
    width: int = Form(512, ge=64, le=2048),
    guidance_scale: float = Form(2.5, gt=0),
    img_guidance_scale: Optional[float] = Form(None, gt=0),
    seed: int = Form(0),
    input_images: Optional[List[UploadFile]] = File(None),
):
    try:
        if input_images:
            # Load images from uploaded files
            loaded_images = []
            for image_file in input_images:
                image_bytes = await image_file.read()
                image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                loaded_images.append(image)

            # Create placeholders for each image
            placeholders = " ".join(
                [f"<img><|image_{i+1}|></img>" for i in range(len(loaded_images))]
            )
            formatted_prompt = f"{prompt} {placeholders}"

            # Generate images using the pipeline
            images = pipe(
                prompt=formatted_prompt,
                input_images=loaded_images,
                height=height,
                width=width,
                guidance_scale=guidance_scale,
                img_guidance_scale=img_guidance_scale or 1.0,
                seed=seed,
            )
        else:
            # Generate images using only the prompt
            images = pipe(
                prompt=prompt,
                height=height,
                width=width,
                guidance_scale=guidance_scale,
                seed=seed,
            )

        # Convert the first image to a base64 string
        img = images[0]
        img_io = io.BytesIO()
        img.save(img_io, format="PNG")
        img_base64 = base64.b64encode(img_io.getvalue()).decode()

        return {"image": img_base64}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {e}")

# Optional Health Check Endpoint
@app.get("/health")
def health_check():
    return {"status": "ok"}

