import cv2
import torch
from ultralytics import YOLO

def to_float32_module(module: torch.nn.Module):
    module.to(torch.float32)
    for child in module.children():
        to_float32_module(child)

def safe_load_yolo(model_path: str):
    ckpt = torch.load(model_path, map_location="cpu", weights_only=False)
    model = YOLO()
    model.model = ckpt.get("model", ckpt)
    # Convert to float32 to avoid Half vs Float errors at fuse time
    to_float32_module(model.model)
    model.ckpt = ckpt
    return model

def detect_emotions_in_video(video_path, model_path):
    model = safe_load_yolo(model_path)
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Cannot open video")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        results = model(frame)          # predictor will run, fuse() now safe
        annotated = results[0].plot()
        cv2.imshow("out", annotated)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# -----------------------------------------------------------------
# STEP 4 — Run main
# -----------------------------------------------------------------
if __name__ == "__main__":
    video_path = r"sample_tests\Video-855.mp4"
    model_path = r"best.pt"
    detect_emotions_in_video(video_path, model_path)
