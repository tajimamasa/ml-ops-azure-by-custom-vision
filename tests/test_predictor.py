from predictor.onnxruntime_predict import predict


def test_predictor():
    image_file = "image/img_000.png"
    model_path = "tests/data/model.onnx"
    predictions = predict(
        image_filename=image_file, model_path=model_path, labels=["Person"]
    )
    assert len(predictions) == 1
