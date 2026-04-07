import os
import json
import time

_LOG_FILE_NAME = f"logs/log_{time.strftime('%Y%m%d_%H%M%S')}.txt"



def read_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read().strip()

def read_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def write_json_file(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def log(message, heading="INFO", file_path=_LOG_FILE_NAME):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(f"============[{heading}]============\n")
        f.write(f"{message}\n")
        f.write(f"====================================\n")
