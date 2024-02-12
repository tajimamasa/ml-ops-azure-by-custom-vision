import azure.functions as func
import logging
import os
import tempfile

from infra.azure_storage_blob import download_blobs
from predictor.onnxruntime_predict import predict
import utils

app = func.FunctionApp()


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
    logging.info("Downloaded model file.")

    model_path = os.path.join(temp_dir, "model.onnx")
    labels = ["Person"]
    predictions = predict(
        image_filename=img_file_path, model_path=model_path, labels=labels
    )
    logging.info(predictions)
