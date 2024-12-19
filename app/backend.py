from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ImageDraw
import datetime
import os
import shutil
from model.models import predict

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PARENT_DIR = "images"
os.makedirs(PARENT_DIR, exist_ok=True)
# UPLOAD_DIR = "uploaded_images"
# PROCESSED_DIR = "processed_images"
# os.makedirs(UPLOAD_DIR, exist_ok=True)
# os.makedirs(PROCESSED_DIR, exist_ok=True)

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename, ext = os.path.splitext(file.filename)
        
        dir_name = f"{filename}_{timestamp}"
        dir_path = os.path.join(PARENT_DIR, dir_name)
        os.makedirs(dir_path, exist_ok=False)

        upload_path = os.path.join(dir_path, f"upload{ext}")
        print('upload path', upload_path)

        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        processed_path = os.path.join(dir_path, f"processed{ext}")
        model_response = predict(image_path=upload_path, save_path=processed_path)

        print(model_response)

        return JSONResponse(content={
            "dir_name": f"{dir_name}",
            "message": f"File '{file.filename}' processed successfully.",
            "uploaded_image": f"/{PARENT_DIR}/{dir_name}/upload{ext}",
            "processed_image": f"/{PARENT_DIR}/{dir_name}/processed{ext}",
            "json_response": f"{model_response}"
        })
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

def find_file_with_keyword(dir, keyword):
    files = os.listdir(dir)

    for file in files:
        if keyword in file:
            return file
        
    return None

@app.get(f"/{{dir_name}}/uploaded")
async def get_uploaded_image(dir_name: str):
    dir = os.path.join(PARENT_DIR, dir_name)
    filename = find_file_with_keyword(dir, 'upload')

    return FileResponse(os.path.join(PARENT_DIR, dir_name, filename))

@app.get(f"/{{dir_name}}/processed")
async def get_processed_image(dir_name: str):
    dir = os.path.join(PARENT_DIR, dir_name)
    filename = find_file_with_keyword(dir, 'processed')

    return FileResponse(os.path.join(PARENT_DIR, dir_name, filename))

