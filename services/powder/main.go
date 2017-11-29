package main

import (
    "net/http"

    "github.com/elazarl/go-bindata-assetfs"
    "github.com/labstack/echo"
    "github.com/labstack/echo/middleware"
)

func main() {
    engine := echo.New()
    api := NewAPI()

    engine.Use(middleware.LoggerWithConfig(middleware.LoggerConfig{
        Format: `${method} | ${status} | ${uri} -> ${latency_human}` + "\n",
    }))

    staticFiles := http.FileServer(&assetfs.AssetFS{
        Asset: Asset,
        AssetDir: AssetDir,
        AssetInfo: AssetInfo,
    })

    api.Bind(engine.Group("/api"))

    engine.Use(func(next echo.HandlerFunc) echo.HandlerFunc {
        return func(c echo.Context) error {
            err := next(c)
            if err != nil {
                httpError, ok := err.(*echo.HTTPError)
                if ok && httpError.Code == http.StatusNotFound {
                    url := c.Request().URL.Path
                    if url == "/" {
                        url = "/index.html"
                    }
                    if _, err := Asset(url[1:]); err == nil {
                        staticFiles.ServeHTTP(c.Response().Writer, c.Request())
                        return nil
                    }
                }
            }
            return err
        }
    })

    engine.Start(":8080")
}
