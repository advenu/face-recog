from pydantic import BaseModel


class TrainingData(BaseModel):
    file_ids: list[str]
