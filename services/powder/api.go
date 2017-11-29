package main

import (
    "fmt"
    "bytes"

    "github.com/labstack/echo"
)

type API struct {
    storage *Storage
    crypto *Crypto
}

func NewAPI() *API {
    return &API{
        storage: NewStorage(),
        crypto: NewCrypto(),
    }
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

    group.POST("/v1/user/profile", api.SaveProfile)
    group.GET("/v1/user/profile", api.GetProfile)

    group.GET("/v1/users", api.GetUsers)
}

func (api *API) Login(c echo.Context) error {
    login := c.FormValue("login")

    hash := api.storage.GetUserProperty(login, "hash")
    if hash == nil {
        return api.Error(c,
                        fmt.Sprintf("Can't find user %s", login))
    }

    salt := api.storage.GetUserProperty(login, "salt")
    password := api.crypto.PasswordHash(salt, c.FormValue("password"))

    if !bytes.Equal(hash, password) {
        return api.Error(c, "Wrong password")
    }

    token := api.crypto.MakeToken(login)

    result := map[string]interface{}{
        "token": token,
        "nickname": login,
    }

    return api.OK(c, result)
}

func (api *API) SignUp(c echo.Context) error {
    login := c.FormValue("login")

    hash := api.storage.GetUserProperty(login, "hash")
    if hash != nil {
        return api.Error(c,
                        fmt.Sprintf("User %s already exists", login))
    }

    salt := api.crypto.CreateSalt()
    password := api.crypto.PasswordHash(salt, c.FormValue("password"))

    api.storage.SetUserProperty(login, "hash", password)
    api.storage.SetUserProperty(login, "salt", salt)

    token := api.crypto.MakeToken(login)

    result := map[string]interface{}{
        "token": token,
        "nickname": login,
    }

    return api.OK(c, result)
}

func (api *API) SaveProfile(c echo.Context) error {
    token := c.Request().Header.Get("token")
    login, err := api.crypto.LoginFromToken(token)

    if err != nil {
        return api.Error(c, "You should login first")
    }

    params, err := c.FormParams()

    if err != nil {
        return api.Error(c, "Internal server error")
    }

    for key := range params {
        api.storage.SetUserProperty(login, key, []byte(params.Get(key)))
    }

    result := map[string]interface{}{}
    return api.OK(c, result)
}

func (api *API) GetProfile(c echo.Context) error {
    token := c.Request().Header.Get("token")
    login, err := api.crypto.LoginFromToken(token)

    if err != nil {
        return api.Error(c, "You should login first")
    }

    result := map[string]interface{}{
        "nickname": login,
    }

    for _, key := range []string{"fullname", "picture"} {
        result[key] = string(api.storage.GetUserProperty(login, key))
    }

    return api.OK(c, result)
}

func (api *API) GetUsers(c echo.Context) error {
    result := map[string]interface{}{}
    return api.OK(c, result)
}
