package azureutil

import (
	"context"
	"os"

	"github.com/Azure/azure-sdk-for-go/sdk/storage/azblob"
	"github.com/Azure/azure-sdk-for-go/sdk/storage/azblob/container"
)

func DownloadBlob(blob_name string, local_name string, container_name string, connection_string string) error {
	client, err := createContainerClient(container_name, connection_string)
	if err != nil {
		return err
	}

	local_file, err_file := os.Create(local_name)
	if err_file != nil {
		return err_file
	}

	_, err_download := client.NewBlobClient(blob_name).DownloadFile(context.Background(), local_file, nil)
	if err_download != nil {
		local_file.Close()
		os.Remove(local_name)
		return err_download
	}

	local_file.Close()
	return nil
}

func UploadBlob(blob_name string, local_name string, container_name string, connection_string string) error {
	client, err := createAzblobClient(connection_string)
	if err != nil {
		return err
	}

	local_file, err_file := os.Open(local_name)
	if err_file != nil {
		return err_file
	}

	client.UploadFile(context.Background(), container_name, blob_name, local_file, nil)
	local_file.Close()
	return nil
}

func DeleteBlob(blob_name string, container_name string, connection_string string) error {
	client, err := createContainerClient(container_name, connection_string)
	if err != nil {
		return err
	}

	_, err_delete := client.NewBlobClient(blob_name).Delete(context.Background(), nil)
	return err_delete
}

type blobProp struct {
	Name string
	Date string
}

func GetBlobList(blob_name_prefix string, container_name string, connection_string string) ([]blobProp, error) {
	client, err := createContainerClient(container_name, connection_string)
	if err != nil {
		return nil, err
	}

	option := azblob.ListBlobsFlatOptions{Prefix: &blob_name_prefix}
	pager := client.NewListBlobsFlatPager(&option)
	var blobs []blobProp
	for pager.More() {
		result, err := pager.NextPage(context.Background())
		if err != nil {
			return nil, err
		}
		for _, blob := range result.Segment.BlobItems {
			data := blobProp{
				Name: *blob.Name,
				Date: blob.Properties.LastModified.String(),
			}
			blobs = append(blobs, data)
		}
	}

	return blobs, nil
}

// container_name と connection_string から、ContainerClient を生成します
func createContainerClient(container_name string, connection_string string) (*container.Client, error) {
	client, err := createAzblobClient(connection_string)
	if err != nil {
		return nil, err
	}
	container_client := client.ServiceClient().NewContainerClient(container_name)
	return container_client, nil
}

func createAzblobClient(connection_string string) (*azblob.Client, error) {
	client, err := azblob.NewClientFromConnectionString(connection_string, nil)
	if err != nil {
		return nil, err
	}
	return client, nil
}
