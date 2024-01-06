package azureutil

// Azure Storage Emulator が動作していることを前提とします

import (
	"fmt"
	"os"
	"testing"
)

func connection_string_for_dev() string {
	return "AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;DefaultEndpointsProtocol=http;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;QueueEndpoint=http://127.0.0.1:10001/devstoreaccount1;TableEndpoint=http://127.0.0.1:10002/devstoreaccount1;"
}

func Test_createContainerClient(t *testing.T) {
	container_name := "user-image"
	_, err := createContainerClient(container_name, connection_string_for_dev())
	if err != nil {
		t.Error(err)
	}
}

func Test_createContainerClientWithWrongConnection(t *testing.T) {
	container_name := "user-image"
	_, err := createContainerClient(container_name, "Wrong connection string")
	if err == nil {
		t.Error("Should return error")
	}
}

func Test_GetBlobList(t *testing.T) {
	container_name := "user-image"
	result, err := GetBlobList("", container_name, connection_string_for_dev())
	if err != nil {
		t.Error(err)
	}

	expected_name := "test.jpeg"
	expected_date := "2024-01-06 13:58:25 +0000 GMT"
	if len(result) != 1 {
		t.Error("Should return one file")
	}

	if result[0].Name != expected_date && result[0].Date != expected_date {
		t.Error("Should return " + expected_name + " and " + expected_date + "\n but return " + result[0].Name + " and " + result[0].Date)
	}
}

func Test_DownloadBlob(t *testing.T) {
	container_name := "user-image"
	blob_name := "test.jpeg"
	local_name := "test-local.jpeg"
	err_download := DownloadBlob(blob_name, local_name, container_name, connection_string_for_dev())
	if err_download != nil {
		t.Error(err_download)
	}
	if _, err := os.Stat(local_name); err != nil {
		t.Error(err)
	}
	os.Remove(local_name)
}

func Test_DownloadBlobWithNoBlob(t *testing.T) {
	container_name := "user-image"
	blob_name := "no-exist.jpeg"
	local_name := "test-local.jpeg"
	err_download := DownloadBlob(blob_name, local_name, container_name, connection_string_for_dev())
	if err_download == nil {
		t.Error("Should return error")
	}
	fmt.Println(err_download)
}

func Test_UploadBlob_DeleteBlob(t *testing.T) {
	container_name := "user-image"
	blob_name := "test-upload.jpeg"
	local_name := "test-upload.jpeg"

	local_file, err_file := os.Create(local_name)
	if err_file != nil {
		t.Error(err_file)
	}
	local_file.Write([]byte("test"))

	err_upload := UploadBlob(blob_name, local_name, container_name, connection_string_for_dev())
	if err_upload != nil {
		t.Error(err_upload)
	}
	os.Remove(local_name)

	err_delete := DeleteBlob(blob_name, container_name, connection_string_for_dev())
	if err_delete != nil {
		t.Error(err_delete)
	}
}
