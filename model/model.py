import json
from ultralytics import YOLO

model = YOLO("yolo11n.pt")

def predict(upload_image_path, processed_image_path, json_response_path):
  responses = []

  results = model(upload_image_path)

  for result in results:
    result.save(processed_image_path)

    json_response = result.to_json()

    with open(json_response_path, "w") as file:
      json.dump(json_response, file)

    responses.append(json_response)

  return responses[0]