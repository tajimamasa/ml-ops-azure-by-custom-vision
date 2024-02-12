from azure.cognitiveservices.vision.customvision.training import (
    CustomVisionTrainingClient,
)
from azure.cognitiveservices.vision.customvision.training.models import (
    Region,
    ImageFileCreateEntry,
    ImageFileCreateBatch,
)
from dataclasses import dataclass
from msrest.authentication import ApiKeyCredentials

import datetime
import os
import requests
import shutil
import tempfile
import time


@dataclass
class Tag:
    left: float
    top: float
    width: float
    height: float


@dataclass
class ImageData:
    path: str
    tags: list[Tag]


def train(
    project_name: str,
    endpoint: str,
    training_key: str,
    images: list[ImageData],
) -> tuple[str, str]:
    """Train a model with the given images"""

    credentials = ApiKeyCredentials(in_headers={"Training-key": training_key})
    trainer = CustomVisionTrainingClient(endpoint, credentials)

    # プロジェクトの作成
    _delete_project(trainer, project_name)
    project = trainer.create_project(
        project_name,
        domain_id=_get_domain_id(trainer),
    )

    # タグの作成
    person_tag = trainer.create_tag(project.id, "Person")

    # 画像のアップロードとタグ付け
    tagged_images_with_regions = []
    for img in images:
        regions = [
            Region(
                tag_id=person_tag.id,
                left=tag.left,
                top=tag.top,
                width=tag.width,
                height=tag.height,
            )
            for tag in img.tags
        ]
        with open(img.path, "rb") as image_contents:
            tagged_images_with_regions.append(
                ImageFileCreateEntry(
                    name=img.path,
                    contents=image_contents.read(),
                    regions=regions,
                )
            )

    trainer.create_images_from_files(
        project.id, ImageFileCreateBatch(images=tagged_images_with_regions)
    )

    # モデルのトレーニング
    trainer.train_project(project.id)


def get_properties(
    project_name: str,
    endpoint: str,
    training_key: str,
) -> tuple[str, str, datetime.datetime] or None:
    """Get the project id, iteration id, and created time"""

    credentials = ApiKeyCredentials(in_headers={"Training-key": training_key})
    trainer = CustomVisionTrainingClient(endpoint, credentials)
    for project in trainer.get_projects():
        if project.name == project_name:
            iteration = trainer.get_iterations(project.id)[-1]
            return project.id, iteration.id, iteration.created
    return None


def get_model(
    project_id: str,
    iteration_id: str,
    endpoint: str,
    training_key: str,
) -> str:
    """Get the model by exporting it"""
    credentials = ApiKeyCredentials(in_headers={"Training-key": training_key})
    trainer = CustomVisionTrainingClient(endpoint, credentials)

    try:
        export = trainer.export_iteration(project_id, iteration_id, "ONNX")
    except Exception as e:
        if "is already queued for export" not in e.message:
            raise e
        export = trainer.get_exports(project_id, iteration_id)[-1]

    while export.status != "Done":
        export = trainer.get_export(project_id, iteration_id)[-1]
        time.sleep(5)

    temp_dir = tempfile.gettempdir()
    zip_file = f"{temp_dir}/export.zip"
    export_file = requests.get(export.download_uri)
    with open(zip_file, "wb") as file:
        file.write(export_file.content)

    shutil.unpack_archive(zip_file, temp_dir)
    model_path = f"{temp_dir}/model.onnx"

    return model_path if os.path.exists(model_path) else None


def _get_domain_id(trainer, domain_name: str = "General (compact)") -> str:
    """Get a domain by name"""
    return next(
        x
        for x in trainer.get_domains()
        if x.type == "ObjectDetection" and x.name == domain_name
    ).id


def _delete_project(trainer, project_name: str):
    """Delete a project if it exists"""
    projects = trainer.get_projects()
    for project in projects:
        if project.name == project_name:
            trainer.delete_project(project.id)
            break
