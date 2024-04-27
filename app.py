from fastapi import FastAPI, Depends, BackgroundTasks
from dependencies import authenticate
from appwrite.client import Client
from appwrite.services.users import Users
from appwrite.services.storage import Storage
from typing import Annotated
from models import TrainingData
from recog import train, predict, save_cropped_images
from config import BUCKET_ID, STORAGE_DIR, TEMP_DIR
from pathlib import Path
import hashlib
import uuid
import os

app = FastAPI()


def download_file(storage: Storage, user_dir: str, file_id: str) -> str:
    print(f"Downloading file: {file_id}")

    file = storage.get_file(BUCKET_ID, file_id)
    file_content = storage.get_file_download(BUCKET_ID, file_id)

    # use file hash as name
    file_hash = hashlib.sha256(file_content).hexdigest()[:16]
    filename = os.path.join(user_dir, f"{file_hash}{os.path.splitext(file['name'])[1]}")

    with open(filename, "wb") as f:
        f.write(file_content)


@app.post("/learn")
async def train_model(
    data: TrainingData, auth: Annotated[tuple[Client, Users], Depends(authenticate)]
):
    client, user = auth

    user_dir = os.path.join(STORAGE_DIR, user["$id"])
    Path(user_dir).mkdir(exist_ok=True)

    storage = Storage(client)
    for file_id in data.file_ids:
        download_file(storage, user_dir, file_id)

    print("Training model ...")
    train(
        STORAGE_DIR,
        model_save_path="trained_model.clf",
        n_neighbors=2,
        verbose=True,
    )

    return {"success": True, "msg": "Successfully added data into model"}


@app.get("/recognize")
async def recognize(
    file_id: str,
    auth: Annotated[tuple[Client, Users], Depends(authenticate)],
    bg: BackgroundTasks,
):
    client = auth[0]
    storage = Storage(client)

    # use random uuid as name
    file = storage.get_file(BUCKET_ID, file_id)
    filename = os.path.join(
        TEMP_DIR, f"{uuid.uuid4()}{os.path.splitext(file['name'])[1]}"
    )

    file_content = storage.get_file_download(BUCKET_ID, file_id)
    with open(filename, "wb") as f:
        f.write(file_content)

    predictions = predict(filename, model_path="trained_model.clf")

    def bg_task():
        save_cropped_images(filename, predictions, STORAGE_DIR)
        os.remove(filename)

        # re-train
        print("Re-training model ...")
        train(
            STORAGE_DIR,
            model_save_path="trained_model.clf",
            n_neighbors=2,
            verbose=True,
        )

    bg.add_task(bg_task)
    return {"success": True, "recognized_users": [id for id, _ in predictions]}
