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

    group.POST("/v1/conversations", api.UpdateConversation)
}

func (api *API) Login(c echo.Context) error {
    login := c.FormValue("login")

    user := api.storage.GetUser(login)
    if user == nil {
        return api.Error(c,
                        fmt.Sprintf("Can't find user %s", login))
    }

    password := api.crypto.PasswordHash(user.Salt, c.FormValue("password"))
    if !bytes.Equal(user.Hash, password) {
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

    user := api.storage.GetUser(login)
    if user != nil {
        return api.Error(c,
                        fmt.Sprintf("User %s already exists", login))
    }

    salt := api.crypto.CreateSalt()
    hash := api.crypto.PasswordHash(salt, c.FormValue("password"))

    user = &User{
        Username: login,
        Salt: salt,
        Hash: hash,
        Properties: make(map[string]string),
    }

    api.storage.SaveUser(user)

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

    user := api.storage.GetUser(login)
    for key := range params {
        user.Properties[key] = params.Get(key)
    }
    api.storage.SaveUser(user)

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

    user := api.storage.GetUser(login)

    for _, key := range []string{"fullname", "picture"} {
        result[key] = user.Properties[key]
    }

    return api.OK(c, result)
}

func (api *API) GetUsers(c echo.Context) error {
    users := make([]map[string]string, 0)

    api.storage.IterateUsers(func (user *User) {
        user.Properties["login"] = user.Username

        users = append(users, user.Properties)
    })

    result := map[string]interface{}{
        "users": users,
    }

    return api.OK(c, result)
}

func (api *API) UpdateConversation(c echo.Context) error {
    token := c.Request().Header.Get("token")
    login, err := api.crypto.LoginFromToken(token)

    if err != nil {
        return api.Error(c, "You should login first")
    }

    result := map[string]interface{}{
        "nickname": login,
    }

    return api.OK(c, result)
}
