import json
from custom_vision import Tag, ImageData
from custom_vision import train, get_properties, get_model


def read_json(file_path: str) -> dict:
    with open(file_path, "r") as f:
        return json.load(f)


def endpoint_and_key():
    file_path = "./src/local.settings.json"
    data = read_json(file_path)["Values"]
    return data["CustomVisionEndpoint"], data["CustomVisionTrainingKey"]


def test_train():
    endpoint, training_key = endpoint_and_key()
    dataset = read_json("./image/tag.json")
    images = []
    for data in dataset:
        tags = [
            Tag(
                left=tag["left"],
                top=tag["top"],
                width=tag["width"],
                height=tag["height"],
            )
            for tag in data["tags"]
        ]
        images.append(ImageData(path=f"./image/{data['fileName']}", tags=tags))

    train(
        "camera000",
        endpoint,
        training_key,
        images,
    )


# test_train()の実行後に以下のコードを実行してください
def test_get_properties():
    endpoint, training_key = endpoint_and_key()
    retval = get_properties("camera000", endpoint, training_key)
    assert len(retval) == 3


def test_get_properties_with_none():
    endpoint, training_key = endpoint_and_key()
    assert get_properties("cameraXXX", endpoint, training_key) is None


def test_get_model():
    endpoint, training_key = endpoint_and_key()
    project_id, iteration_id, _ = get_properties(
        "camera000",
        endpoint,
        training_key,
    )
    file_path = get_model(project_id, iteration_id, endpoint, training_key)
    assert file_path != "" and file_path is not None
