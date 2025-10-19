from ultralytics import YOLO
import torch
import multiprocessing

def main():
    print("CUDA available:", torch.cuda.is_available())
    print("GPU:", torch.cuda.get_device_name(0))

    model = YOLO(r"C:\project_pid\pythonProject\.venv\runs\detect\project_pid_run_aug13\weights\best.pt")

    results = model.val(
        data=r"C:\project_pid\pythonProject\.venv\dataset\data.yaml",
        split='test',
        imgsz=640,
        batch=16,
        save_json=True,
        save_hybrid=True,
        conf=0.25
    )

    print(results)

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
