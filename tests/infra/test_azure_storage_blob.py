import datetime
import json
import tempfile
from infra.azure_storage_blob import download_blobs, last_modified


def container_string():
    file_path = "./src/local.settings.json"
    with open(file_path, "r") as f:
        json_data = json.load(f)["Values"]
    return json_data["AzureWebJobsContainerString"]


def test_download_blobs():
    temp_dir = tempfile.gettempdir()
    connect_str = container_string()
    container_name = "model-data"
    name_prefix = "camera000"
    download_blobs(container_name, name_prefix, connect_str, temp_dir)


def test_last_modified():
    connect_str = container_string()
    container_name = "learning-data"
    name_prefix = "ideal"
    last_modified_date = last_modified(container_name, name_prefix, connect_str)
    assert last_modified is not None
    assert isinstance(last_modified_date, datetime.datetime)
