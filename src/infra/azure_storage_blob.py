import os

from azure.core.exceptions import (
    HttpResponseError,
    ResourceNotFoundError,
)
from azure.storage.blob import (
    ContainerClient,
)
import datetime


def download_blobs(
    container_name,
    blob_name_prefix,
    connection_string,
    local_dir="",
):
    """
    コンテナ名から指定したプレフィックスを持つブロブを指定したローカルディレクトリにダウンロードする

    Args:
        container_name (str): コンテナ名
        blob_name_prefix (str): ブロブ名のプレフィックス
        connection_string (str): 接続文字列
        local_dir (str): ダウンロード先のディレクトリパス
    """
    client = ContainerClient.from_connection_string(
        conn_str=connection_string, container_name=container_name
    )

    blob_list = _get_blob_list(
        client=client,
        blob_name_prefix=blob_name_prefix,
    )

    for blob in blob_list:
        try:
            content = client.download_blob(blob=blob.name).readall()
        except ResourceNotFoundError:
            raise RuntimeError(
                message="Failed to download blob. The specified resource doesn't exist.",
            )
        except HttpResponseError as err:
            raise RuntimeError(
                message=f"Failed to download blob. HTTP error occurred. Message: {err.message}",
            )

        file_path = os.path.join(local_dir, blob.name)
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(content)
            f.flush()


def last_modified(
    container_name,
    blob_name_prefix,
    connection_string,
):
    """
    コンテナ名から指定したプレフィックスを持つブロブの最終更新日時を取得する

    Args:
        container_name (str): コンテナ名
        blob_name_prefix (str): ブロブ名のプレフィックス
        connection_string (str): 接続文字列
    """
    client = ContainerClient.from_connection_string(
        conn_str=connection_string, container_name=container_name
    )

    blob_list = _get_blob_list(
        client=client,
        blob_name_prefix=blob_name_prefix,
    )

    last_modified = None
    for blob in blob_list:
        blob_last_modified = blob.last_modified

        if last_modified is None or blob_last_modified > last_modified:
            last_modified = blob_last_modified
    return last_modified


def delete_blobs(
    container_name,
    blob_name_prefix,
    connection_string,
):
    """
    コンテナ名から指定したプレフィックスを持つブロブを削除する

    Args:
        container_name (str): コンテナ名
        blob_name_prefix (str): ブロブ名のプレフィックス
        connection_string (str): 接続文字列
    """
    client = ContainerClient.from_connection_string(
        conn_str=connection_string, container_name=container_name
    )

    blob_list = _get_blob_list(
        client=client,
        blob_name_prefix=blob_name_prefix,
    )

    for blob in blob_list:
        client.delete_blob(blob.name)


def _get_blob_list(client, blob_name_prefix):
    """
    コンテナ名から指定したプレフィックスを持つブロブのリストを取得する

    Args:
        client (ContainerClient): コンテナクライアント
        blob_name_prefix (str): ブロブ名のプレフィックス
    """

    try:
        blob_list = client.list_blobs(name_starts_with=blob_name_prefix)
    except ResourceNotFoundError:
        raise RuntimeError(
            message="Failed to list blobs. The specified resource doesn't exist.",
        )
    except HttpResponseError as err:
        raise RuntimeError(
            message=f"Failed to list blobs. HTTP error occurred. Message: {err.message}",
        )

    return blob_list


def upload_files(
    container_name,
    local_dir,
    connection_string,
    blob_name_prefix="",
):
    """
    コンテナURLに指定したローカルディレクトリのファイルをアップロードする

    Args:
        container_name (str): コンテナ名
        local_dir (str): アップロードするファイルのあるディレクトリパス
        connection_string (str): 接続文字列
        blob_name_prefix (str): ブロブ名のプレフィックス
    """
    client = ContainerClient.from_connection_string(
        conn_str=connection_string, container_name=container_name
    )
    for dir, _, files in os.walk(local_dir):
        for file_name in files:
            src_path = os.path.join(dir, file_name)
            dest_path = os.path.join(blob_name_prefix, dir, file_name)

            with open(src_path, "rb") as data:
                try:
                    client.upload_blob(
                        name=dest_path,
                        data=data,
                        overwrite=True,
                    )
                except HttpResponseError as err:
                    raise RuntimeError(
                        message=f"Failed to upload blob. HTTP error occurred. Message: {err.message}",
                    )
