from detect_and_generate import detect_and_generate_3d
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from scaling import compute_scale
from classification_utils import cairosvg, dxf_to_png
from floorplan_classification import process_image, model
from fastapi import Form
from typing import Tuple
import nest_asyncio
import uvicorn
import shutil
import os


# Autoriser l'exécution asynchrone multiple dans le notebook
nest_asyncio.apply()

# Créer l'app FastAPI
app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    file_bytes = await file.read()
    # Convert SVG to PNG
    if file.content_type == "image/svg+xml":
        image_bytes = await cairosvg(file_bytes)

    # Convert DXF to PNG
    elif file.content_type == "application/dxf" or file.filename.endswith(".dxf"):
        image_bytes = await dxf_to_png(file_bytes)

    # Use file as-is for other image formats
    else:
        image_bytes = file_bytes

    return process_image(image_bytes, model)
    # return cocaViT(image_bytes)
    # return ViT(image_bytes)


@app.post("/upload/")
async def upload_image(
    file: UploadFile = File(...),
    point1: str = Form(...),
    point2: str = Form(...),
    real_distance_m: float = Form(...),
):
    file_location = f"uploads/{file.filename}"
    os.makedirs("uploads", exist_ok=True)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    x1, y1 = map(float, point1.split(","))
    x2, y2 = map(float, point2.split(","))
    point1_tuple: Tuple[float, float] = (x1, y1)
    point2_tuple: Tuple[float, float] = (x2, y2)

    print("Points parsed:", point1_tuple, point2_tuple)

    scale = compute_scale(
        file_location,
        point1_tuple,
        point2_tuple,
        real_distance_m,
    )

    model_path, _ = detect_and_generate_3d(file_location, scale)
    return FileResponse(model_path, media_type="application/octet-stream")


@app.get("/")
async def root():
    return {"message": "Hello, please upload an image to /upload/."}


# Lancer le serveur
uvicorn.run(app, host="0.0.0.0", port=8000)
