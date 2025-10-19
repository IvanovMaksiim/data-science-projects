import os
import shutil
import zipfile
import subprocess
from glob import glob

YOLO_RUN_DIR = r"C:\project_pid\pythonProject\.venv\runs\detect\project_pid_run_aug12"
AUTOCVAT_SCRIPT = r"C:\project_pid\pythonProject\.venv\AutoCVAT\AutoCvat.py"
AUTOCVAT_DIR = os.path.dirname(AUTOCVAT_SCRIPT)
IMG_FOLDER = os.path.join(AUTOCVAT_DIR, "new_pids")
CONFIG_YAML = os.path.join(AUTOCVAT_DIR, "config.yaml")
MERGE_JSON_DIR = r"C:\project_pid\pythonProject\.venv\merge_json_coco"
ANNOTATIONS_ZIP = os.path.join(AUTOCVAT_DIR, "annotations.zip")

os.makedirs(MERGE_JSON_DIR, exist_ok=True)

pt_files = glob(os.path.join(YOLO_RUN_DIR, "weights", "best.pt"))
MODEL_PATH = pt_files[0]

cmd = [
    "python", "AutoCvat.py",
    f'--img_folder="new_pids"',
    f'--weights="{MODEL_PATH}"',
    f'--yaml_pth=config.yaml'
]

subprocess.run(" ".join(cmd), shell=True, check=True, cwd=AUTOCVAT_DIR)

TEMP_EXTRACT_DIR = os.path.join(MERGE_JSON_DIR, "_temp_extract")
if os.path.exists(TEMP_EXTRACT_DIR):
    shutil.rmtree(TEMP_EXTRACT_DIR)
os.makedirs(TEMP_EXTRACT_DIR, exist_ok=True)

with zipfile.ZipFile(ANNOTATIONS_ZIP, 'r') as zip_ref:
    zip_ref.extractall(TEMP_EXTRACT_DIR)

SRC_JSON = os.path.join(TEMP_EXTRACT_DIR, "annotations", "instances_default.json")
DST_JSON = os.path.join(MERGE_JSON_DIR, "instances_default.json")

if os.path.exists(SRC_JSON):
    shutil.move(SRC_JSON, DST_JSON)

shutil.rmtree(TEMP_EXTRACT_DIR)


print("Файл instances_default.json перемещен в merge_json_coco")
