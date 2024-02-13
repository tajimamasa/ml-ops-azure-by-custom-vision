import azure.functions as func
import json
import logging
import os
import tempfile

from custom_vision import get_model, get_properties, train
from custom_vision import ImageData, Tag
from infra.azure_storage_blob import download_blobs
from infra.azure_storage_blob import upload_file
from infra.azure_storage_blob import last_modified_blob
from infra.mysql import insert_data
from image_preprocessing.noise_estimation import estimate_noise
from image_preprocessing.noise_simulation import add_noise
from predictor.onnxruntime_predict import predict
import utils

app = func.FunctionApp()

CAMERAS = ["camera000", "camera001", "camera002"]


@app.blob_trigger(
    arg_name="myblob",
    path="image-data/{name}",
    connection="ContainerString",
)
def counting_person(myblob: func.InputStream):
    file_name = os.path.basename(myblob.name)
    temp_dir = tempfile.gettempdir()
    img_file_path = os.path.join(temp_dir, file_name)
    logging.info(f"Name: {file_name}\nTemp Dir: {temp_dir}")

    # ファイル拡張子のチェック
    if not utils.check_extension(file_name=file_name):
        logging.error("File extension not supported")
        return

    # ファイルを書き込む
    with open(img_file_path, "wb") as f:
        f.write(myblob.read())
    logging.info("Write image file.")

    # ファイル名からカメラ番号を取得
    camera_id = utils.extract_camera_id(file_name=file_name)
    download_blobs(
        container_name="model-data",
        blob_name_prefix=f"ideal/camera{camera_id}",
        connection_string=os.environ["AzureWebJobsContainerString"],
        local_dir=temp_dir,
    )

    # モデルファイルのダウンロード
    model_path = os.path.join(temp_dir, "model.onnx")
    if os.path.exists(model_path):
        logging.info("Downloaded model file.")
    else:
        logging.info("Download is failed.")
        return

    # 予測
    predictions = predict(
        image_filename=img_file_path, model_path=model_path, labels=["Person"]
    )

    # データベースにデータを挿入
    query = "INSERT INTO person_count (camera_id, count) VALUES (%s, %s)"
    params = (camera_id, len(predictions))
    insert_data(
        connection_string=os.environ["MySQLConnectionString"],
        query=query,
        params=params,
    )


@app.function_name(name="training_timer")
@app.schedule(
    schedule="0 0 0 * * *",  # 1日ごとに実行, AM0時
    arg_name="training_timer",
    run_on_startup=True,
)
def training(training_timer: func.TimerRequest) -> None:
    temp_dir = tempfile.gettempdir()
    ideal_images = download_blobs(
        container_name="learning-data",
        blob_name_prefix="ideal",
        connection_string=os.environ["AzureWebJobsContainerString"],
        local_dir=temp_dir,
    )
    logging.info("Downloaded ideal images")

    json_file_path = [img for img in ideal_images if img == "tag.json"][0]
    with open(json_file_path, "r") as f:
        json_data = json.load(f)  # タグの情報を取得

    # 元の理想画像のタグ情報を取得
    tags: list[list[Tag]] = [
        [
            Tag(
                left=data["left"],
                top=data["top"],
                width=data["width"],
                height=data["height"],
            )
            for data in img["tags"]
        ]
        for img in json_data
    ]
    ideal_images: list[str] = [
        img for img in ideal_images if utils.check_extension(img)
    ]
    logging.info("Extracted tag information")

    for camera in CAMERAS:
        calibration_imgs = download_blobs(
            container_name="learning-data",
            blob_name_prefix=camera,
            connection_string=os.environ["AzureWebJobsContainerString"],
            local_dir=temp_dir,
        )
        calibration_imgs = [
            img for img in calibration_imgs if utils.check_extension(img)
        ]
        logging.info(f"Downloaded calibration images for {camera}")

        noise_levels = estimate_noise(calibration_imgs)
        logging.info(f"Noise levels: {noise_levels}")

        learning_images = add_noise(ideal_images, noise_levels)
        logging.info(f"Added noise to ideal images for {camera}")

        learning_images_data = [
            ImageData(path=img, tags=tag)
            for img, tag in zip(
                learning_images,
                tags,
            )
        ]
        train(
            project_name=camera,
            endpoint=os.environ["CustomVisionEndpoint"],
            training_key=os.environ["CustomVisionTrainingKey"],
            images=learning_images_data,
        )
        logging.info(f"Trained model for {camera}")


@app.function_name(name="update_timer")
@app.schedule(
    schedule="0 0 5 * * *",  # 1日ごとに実行, AM5時
    arg_name="update_timer",
    run_on_startup=True,
)
def update_model(update_timer: func.TimerRequest) -> None:
    for camera in CAMERAS:
        iteration_properties = get_properties(
            project_name=camera,
            endpoint=os.environ["CustomVisionEndpoint"],
            training_key=os.environ["CustomVisionTrainingKey"],
        )

        last_modified_model = last_modified_blob(
            container_name="model-data",
            blob_name_prefix=camera,
            connection_string=os.environ["AzureWebJobsContainerString"],
        )

        if last_modified_model is None:
            logging.error(f"No model for {camera}")
            continue

        if iteration_properties is None:
            logging.error(f"No iteration for {camera}")
            continue

        if last_modified_model > iteration_properties[2]:
            logging.info(f"Model for {camera} is up-to-date.")
            continue

        logging.info(f"Last modified model for {camera}: {last_modified_model}")
        logging.info(f"Last trained model for {camera}: {iteration_properties[2]}")

        model_path = get_model(
            project_id=iteration_properties[0],
            iteration_id=iteration_properties[1],
            endpoint=os.environ["CustomVisionEndpoint"],
            training_key=os.environ["CustomVisionTrainingKey"],
        )
        logging.info(f"Downloaded model for {camera}")

        upload_file(
            local_file_path=model_path,
            container_name="model-data",
            blob_name=f"{camera}/model.onnx",
            connection_string=os.environ["AzureWebJobsContainerString"],
        )
        logging.info(f"Updated model for {camera}")
