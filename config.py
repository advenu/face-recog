from pathlib import Path

PROJECT_ID = "662befeb824a6421a1cf"
BUCKET_ID = "662bf160a056062c8674"

STORAGE_DIR = "training_data"
TEMP_DIR = "temp"

Path(STORAGE_DIR).mkdir(exist_ok=True)
Path(TEMP_DIR).mkdir(exist_ok=True)
