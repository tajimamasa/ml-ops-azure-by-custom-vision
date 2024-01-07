package images

import (
	"encoding/base64"
	"io"
	"net/http"
	"os"
	"strings"

	"learning/azureutil"
	"learning/constants"

	"github.com/labstack/echo/v4"
)

func GetImages(c echo.Context) error {
	blob_list, err := azureutil.GetBlobList("", "user-image", constants.StorageConnectionString())
	if err != nil {
		return c.String(http.StatusInternalServerError, err.Error())
	}
	return c.JSON(http.StatusOK, blob_list)
}

func GetImage(c echo.Context) error {
	blob_list, err := azureutil.GetBlobList("", "user-image", constants.StorageConnectionString())
	if err != nil {
		return c.String(http.StatusInternalServerError, err.Error())
	}

	blob_name := c.Param("name")
	for _, blob := range blob_list {
		if blob.Name == blob_name {
			return c.JSON(http.StatusOK, blob)
		}
	}
	return c.String(http.StatusNotFound, "Not Found")
}

func DeleteImage(c echo.Context) error {
	blob_name := c.Param("name")
	err := azureutil.DeleteBlob(blob_name, "user-image", constants.StorageConnectionString())
	if err != nil {
		message := err.Error()
		if strings.Contains(message, "BlobNotFound") {
			return c.String(http.StatusOK, "Already Deleted")
		}
		return c.String(http.StatusInternalServerError, message)
	}
	return c.String(http.StatusOK, "Deleted")
}

func PostImage(c echo.Context) error {
	blob_name := c.Param("name")
	if isInvalidExtension(blob_name) {
		return c.String(http.StatusBadRequest, "Invalid Extension")
	}

	body, err := io.ReadAll(c.Request().Body)
	if err != nil {
		return c.String(http.StatusInternalServerError, "Error reading body: "+err.Error())
	}

	local_name := blob_name
	err_decode := decodeBase64ToFile(string(body), local_name)
	if err_decode != nil {
		return c.String(http.StatusBadRequest, "Error decoding base64: "+err_decode.Error())
	}

	// ToDo: 画像の確認

	err_upload := azureutil.UploadBlob(blob_name, local_name, "user-image", constants.StorageConnectionString())
	if err_upload != nil {
		return c.String(http.StatusInternalServerError, "Error uploading blob: "+err_upload.Error())
	}
	os.Remove(local_name)

	return c.String(http.StatusOK, "Uploaded")
}

func isInvalidExtension(filename string) bool {
	extensions := []string{".jpg", ".jpeg", ".png", ".bmp"}
	for _, extension := range extensions {
		if strings.HasSuffix(filename, extension) {
			return false
		}

		// Capital extension
		if strings.HasSuffix(filename, strings.ToUpper(extension)) {
			return false
		}
	}
	return true
}

func decodeBase64ToFile(encodedString string, filePath string) error {
	decodedData, err := base64.StdEncoding.DecodeString(encodedString)
	if err != nil {
		return err
	}

	err = os.WriteFile(filePath, decodedData, 0644)
	if err != nil {
		return err
	}

	return nil
}
