import base64
from app.models.vlm_client import analyze_image

async def run_vlm_inference(file):
    contents = await file.read()

    image_base64 = base64.b64encode(contents).decode("utf-8")

    report = analyze_image(image_base64)

    return report