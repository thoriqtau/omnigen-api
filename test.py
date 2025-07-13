import httpx
import time
import base64
from PIL import Image
from io import BytesIO
import asyncio

async def send_request():
    endpoint_id = "nqra85vrvbz3ji"
    api_key = "9SPZ3DGRA7UB52OG4A5ILX6MQU85TR21UIS8WO1O"  
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    input_images=["./imgs/demo_cases/emma.jpeg", "./imgs/demo_cases/dress.jpg"]
    # Initial payload with only the prompt
    payload = {
        "input": {
            "prompt": "The man in <img><|image_1|></img> and the style in <img><|image_2|></img>", 
            "height": 1024,
            "width": 1024,
            "guidance_scale": 2.5,
            "input_images": input_images,
            "img_guidance_scale":1.6,
            "max_input_image_size":1024
        }
    }

    try:
        async with httpx.AsyncClient() as client:
            # Submit the job
            run_url = f"https://api.runpod.ai/v2/{endpoint_id}/run"
            response = await client.post(run_url, headers=headers, json=payload)
            response.raise_for_status()
            job = response.json()
            job_id = job['id']
            
            print(f"Job submitted with ID: {job_id}")
            
            # Poll for job completion
            status_url = f"https://api.runpod.ai/v2/{endpoint_id}/status/{job_id}"
            while True:
                status_response = await client.get(status_url, headers=headers)
                status_response.raise_for_status()
                status_data = status_response.json()
                
                if status_data['status'] == 'COMPLETED':
                    # Extract the base64 image directly from the response
                    base64_image = status_data['output']
                    
                    # Convert base64 to image
                    image_data = base64.b64decode(base64_image)
                    image = Image.open(BytesIO(image_data))
                    
                    # Display the image
                    image.show()
                    
                    # Optionally save the image
                    image.save('generated_image.png')
                    break
                    
                elif status_data['status'] == 'FAILED':
                    print("Job failed:", status_data.get('error', 'Unknown error'))
                    break
                    
                print(f"Job status: {status_data['status']}")
                await asyncio.sleep(2)  # Wait 2 seconds before polling again
            
    except httpx.HTTPError as e:
        print(f"HTTP error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Run the async function
asyncio.run(send_request())