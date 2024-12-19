import os
import shutil
import datetime
from model.model import predict
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PARENT_DIR = os.path.join("app", "results")
os.makedirs(PARENT_DIR, exist_ok=True)
app.mount("/app/results", StaticFiles(directory=os.path.join("app", "results")), name="results")

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename, ext = os.path.splitext(file.filename)
        
        dir_name = f"{filename}_{timestamp}"
        dir_path = os.path.join(PARENT_DIR, dir_name)
        os.makedirs(dir_path, exist_ok=False)

        upload_path = os.path.join(dir_path, f"upload{ext}")

        try:
            with open(upload_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            print(f"Error: {e}")

        processed_path = os.path.join(dir_path, f"processed{ext}")
        json_response_path = os.path.join(dir_path, "response.json")
        model_response = predict(
            upload_image_path=upload_path,
            processed_image_path=processed_path,
            json_response_path=json_response_path
        )

        return JSONResponse(content={
            "dir_name": f"{dir_name}",
            "message": f"File '{file.filename}' processed successfully.",
            "uploaded_image": f"{upload_path}",
            "processed_image": f"{processed_path}",
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

