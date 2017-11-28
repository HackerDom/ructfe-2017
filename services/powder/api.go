package main

import (
    "fmt"
    "bytes"

    "github.com/labstack/echo"
)

type API struct {
    storage *Storage
}

func NewAPI() *API {
    return &API{storage: NewStorage()}
}

func (api *API) OK(c echo.Context, result map[string]interface{}) error {
    result["error"] = false
    return c.JSON(200, result)
}

func (api *API) Error(c echo.Context, errorMessage string) error {
    result := map[string]interface{}{}

    result["error"] = true
    result["errorMessage"] = errorMessage

    return c.JSON(200, result)
}

func (api *API) Bind(group *echo.Group) {
    group.POST("/v1/auth/login", api.Login)
    group.POST("/v1/auth/signup", api.SignUp)
}

func (api *API) Login(c echo.Context) error {
    login := c.FormValue("login")
    password := PasswordHash("", c.FormValue("password"))

    hash := api.storage.GetUserProperty(login, "hash")
    if hash == nil {
        return api.Error(c,
                        fmt.Sprintf("Can't find user %s", login))
    }

    if !bytes.Equal(hash, password) {
        return api.Error(c, "Wrong password")
    }

    result := map[string]interface{}{
        "token": login,
        "nickname": login,
    }

    return api.OK(c, result)
}

func (api *API) SignUp(c echo.Context) error {
    login := c.FormValue("login")
    password := PasswordHash("", c.FormValue("password"))

    hash := api.storage.GetUserProperty(login, "hash")
    if hash != nil {
        return api.Error(c,
                        fmt.Sprintf("User %s already exists", login))
    }

    api.storage.SetUserProperty(login, "hash", password)

    result := map[string]interface{}{
        "token": login,
        "nickname": login,
    }

    return api.OK(c, result)
}
