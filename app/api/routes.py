from fastapi import APIRouter, UploadFile, File
from app.services.inference import run_vlm_inference

router = APIRouter()

@router.post("/vlm/analyze")
async def analyze_image(file: UploadFile = File(...)):
    return await run_vlm_inference(file)
