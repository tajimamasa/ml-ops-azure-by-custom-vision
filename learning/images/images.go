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

// Images List
// @Description ユーザーがアップロードした画像の一覧をBlob Storage から取得する。
// @Accept  json
// @Produce  json
// @Success 200 {string} string "OK"
// @Failure 500 {string} string "Internal Server Error"
// @Router /images [get]
func GetImages(c echo.Context) error {
	blob_list, err := azureutil.GetBlobList("", "user-image", constants.StorageConnectionString())
	if err != nil {
		return c.String(http.StatusInternalServerError, err.Error())
	}
	return c.JSON(http.StatusOK, blob_list)
}

// Image Info
// @Description 指定した画像の情報をBlob Storage から取得する。
// @Param name path string true "Image Name"
// @Accept  json
// @Produce  json
// @Success 200 {string} string "OK"
// @Failure 500 {string} string "Internal Server Error"
// @Router /images/{name} [get]
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

// Delete Image
// @Description 指定した画像をBlob Storageから削除する。
// @Param name path string true "Image Name"
// @Accept  json
// @Produce  json
// @Success 200 {string} string "OK"
// @Failure 500 {string} string "Internal Server Error"
// @Router /images/{name}/delete [post]
func DeleteImage(c echo.Context) error {
	blob_name := c.Param("name")
	err := azureutil.DeleteBlob(blob_name, "user-image", constants.StorageConnectionString())
	if err != nil {
		message := err.Error()
		if strings.Contains(message, "BlobNotFound") {
			return c.JSON(http.StatusOK, "OK")
		}
		return c.String(http.StatusInternalServerError, message)
	}
	return c.JSON(http.StatusOK, "OK")
}

// Upload Image
// @Description ユーザーがアップロードした画像をBlob Storageにアップロードする。Bodyにはbase64エンコードされた画像を要求する。
// @Param name path string true "Image Name"
// @Param body body string true "Image Body"
// @Accept  json
// @Produce  json
// @Success 200 {string} string "OK"
// @Failure 400 {string} string "Invalid Extension"
// @Failure 400 {string} string "Error decoding base64"
// @Failure 500 {string} string "Internal Server Error"
// @Router /images/{name} [post]
func PostImage(c echo.Context) error {
	blob_name := c.Param("name")
	if isInvalidExtension(blob_name) {
		return c.String(http.StatusBadRequest, "Invalid Extension")
	}

	body, err := io.ReadAll(c.Request().Body)
	if err != nil {
		return c.String(http.StatusInternalServerError, err.Error())
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

	return c.JSON(http.StatusOK, "OK")
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
