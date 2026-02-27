
from fastapi import FastAPI, UploadFile, File
from PIL import Image
import io

app = FastAPI()
model = CleaningAssessmentModel()

@app.post("/assess-cleaning")
async def assess_cleaning(image: UploadFile = File(...)):
    image_data = await image.read()
    image = Image.open(io.BytesIO(image_data))
    
    result = model.assess_cleaning(image)
    return result

@app.post("/batch-assess")
async def batch_assess(images: list[UploadFile] = File(...)):
    results = []
    for image in images:
        result = await assess_cleaning(image)
        results.append(result)
    return results