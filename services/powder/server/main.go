package main

import (
    "github.com/labstack/echo"
    "github.com/labstack/echo/middleware"
)

func main() {
    engine := echo.New()
    api := NewAPI()

    engine.Use(middleware.LoggerWithConfig(middleware.LoggerConfig{
        Format: `${method} | ${status} | ${uri} -> ${latency_human}` + "\n",
    }))

    api.Bind(engine.Group("/api"))
    engine.Start(":3001")
}
