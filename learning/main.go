package main

import (
	_ "learning/docs"
	"learning/images"
	"net/http"

	"github.com/labstack/echo/v4"
	echoSwagger "github.com/swaggo/echo-swagger"
)

// Check Health
// @Description サーバーのヘルスチェック
// @Accept  json
// @Produce  json
// @Success 200 {string} string "OK"
// @Router / [get]
func hello(c echo.Context) error {
	return c.JSON(http.StatusOK, "OK")
}

// @title Learning API
// @version 1.0
func main() {
	e := echo.New()
	e.GET("/", hello)
	e.GET("/docs/*", echoSwagger.WrapHandler)
	img := e.Group("/images")
	{
		img.GET("", images.GetImages)
		img.GET("/:name", images.GetImage)
		img.POST("/:name/delete", images.DeleteImage)
		img.POST("/:name", images.PostImage)
	}
	e.Logger.Fatal(e.Start(":8000"))
}
