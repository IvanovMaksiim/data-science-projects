import json
import create_new_class_json
autocvat_json = r"C:\project_pid\pythonProject\.venv\merge_json_coco\instances_default.json"
manual_json = r"C:\project_pid\pythonProject\.venv\merge_json_coco\instances.json"
merged_json = r"C:\project_pid\pythonProject\.venv\merge_json_coco\merged_coco.json"


with open(autocvat_json, "r", encoding="utf-8") as f:
    auto_data = json.load(f)
with open(manual_json, "r", encoding="utf-8") as f:
    manual_data = json.load(f)

keep_classes = {36, 34, 35}
auto_filtered = [ann for ann in auto_data["annotations"] if ann["category_id"] in keep_classes]

merged = {
    "images": manual_data["images"],
    "annotations": manual_data["annotations"] + auto_filtered,
    "categories": manual_data["categories"],
}


with open(merged_json, "w", encoding="utf-8") as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)

print(f"\nГотово!")


