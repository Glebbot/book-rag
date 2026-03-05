import yaml
import os
from pathlib import Path
from functools import lru_cache
from pydantic import BaseModel


class Qdrant(BaseModel):
    url: str
    api_key: str
    collection_name: str


class Model(BaseModel):
    url: str
    api_key: str
    model: str


class Splitter(BaseModel):
    chunk_size: int
    chunk_overlap: int


class Config(BaseModel):
    qdrant: Qdrant
    model: Model
    splitter: Splitter


@lru_cache()
def load_config(config_path: str = "config.yml") -> Config:
    path = Path(config_path)

    if not path.exists():
        raise FileNotFoundError(f"Конфигурационный файл не найден: {path.absolute()}")

    with open(path, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)

    config_data["qdrant"]["api_key"] = os.getenv("QDRANT_API_KEY")
    config_data["model"]["api_key"] = os.getenv("OPENAI_API_KEY")

    return Config(**config_data)


def get_config() -> Config:
    return load_config()