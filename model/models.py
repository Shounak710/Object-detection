import json
import base64
from PIL import Image
from io import BytesIO
from ultralytics import YOLO

model = YOLO("yolo11n.pt")

def predict(image_path, save_path=None):
  responses = []

  results = model(image_path)

  for result in results:
    result.save(save_path)
    responses.append(result.to_json())

  return responses[0]