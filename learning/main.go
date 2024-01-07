package main

import (
	"learning/images"
	"net/http"

	"github.com/labstack/echo/v4"
)

func hello(c echo.Context) error {
	return c.String(http.StatusOK, "Hello World!")
}

func main() {
	e := echo.New()
	e.GET("/", hello)
	img := e.Group("/images")
	{
		img.GET("", images.GetImages)
		img.GET("/:name", images.GetImage)
		img.POST("/:name/delete", images.DeleteImage)
		img.POST("/:name", images.PostImage)
	}
	e.Logger.Fatal(e.Start(":8000"))
}
