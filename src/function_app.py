import azure.functions as func
import logging
from predictor.onnxruntime_predict import predict

app = func.FunctionApp()


@app.blob_trigger(
    arg_name="myblob",
    path="image-data/{name}",
    connection="ContainerString",
)
def counting_person(myblob: func.InputStream):
    file_name = myblob.name

    # ファイル名のログ
    logging.info(f"Name: {myblob.name}")
    if not check_extension(file_name=file_name):
        return

    model_path = "model.onnx"
    labels = ["Person"]
    predictions = predict(
        image_filename=myblob.name, model_path=model_path, labels=labels
    )
    logging.info(predictions)


def check_extension(file_name: str) -> bool:
    # ファイルの拡張子を確認する
    file_extension = file_name.split(".")[-1].upper()
    image_extensions = ["PNG", "JPEG", "BMP"]
    if file_extension not in image_extensions:
        logging.error(f"File extension {file_extension} not supported")
        return False
    else:
        logging.info(f"File extension {file_extension} supported")
        return True
