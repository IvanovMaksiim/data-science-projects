import torch
from ultralytics import YOLO
import multiprocessing
import re_split_dataset
from check_classes import enough_classes

def main():
    print("CUDA available:", torch.cuda.is_available())

    model = YOLO("yolov8m.pt")

    model.train(
        data=r"C:\project_pid\pythonProject\.venv\dataset\data.yaml",
        epochs=100,
        imgsz=640,
        batch=16,
        name="project_pid_run_aug",
        augment=True,
        auto_augment="RandAugment",
        # classes= enough_classes,
        patience=5,
        workers=0,
        verbose=True
    )

if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()
    main()
