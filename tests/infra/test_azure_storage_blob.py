import json
import tempfile
from infra.azure_storage_blob import download_blobs


def container_string():
    file_path = "./src/local.settings.json"
    with open(file_path, "r") as f:
        json_data = json.load(f)["Values"]
    return json_data["AzureWebJobsContainerString"]


def test_download_blobs():
    temp_dir = tempfile.gettempdir()
    connect_str = container_string()
    container_name = "model-data"
    name_prefix = "ideal/camera000"
    download_blobs(container_name, name_prefix, connect_str, temp_dir)
