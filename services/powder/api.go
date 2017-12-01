package main

import (
    "fmt"
    "bytes"
    "strconv"

    "github.com/labstack/echo"
)

type API struct {
    storage *Storage
    crypto *Crypto
}

func NewAPI() *API {
    storage := NewStorage()
    crypto := NewCrypto()

    SetupAutoReply(storage)

    return &API{
        storage: storage,
        crypto: crypto,
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
    group.GET("/v1/conversations", api.GetConversation)

    group.POST("/v1/autoreply", api.AutoReply)
}

func (api *API) Login(c echo.Context) error {
    login := c.FormValue("login")

    user := api.storage.GetUser(login)
    if user == nil {
        return api.Error(c,
                        fmt.Sprintf("Can't find user %s", login))
    }

    password := api.crypto.Hash(user.Salt, c.FormValue("password"))
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

    user = NewUser(login, c.FormValue("password"), api.crypto)
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
    if user == nil {
        return api.Error(c, fmt.Sprintf("Can't find user %s", login))
    }

    for key := range params {
        value := params.Get(key)
        if key == "address" {
            value = api.crypto.Encrypt(user, value)
        }
        user.Properties[key] = value
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

    if user == nil {
        return api.Error(c, fmt.Sprintf("Can't find user %s", login))
    }

    for key := range user.Properties {
        value := user.Properties[key]
        if key == "address" {
            value = api.crypto.Decrypt(user, value)
        }
        result[key] = value
    }

    return api.OK(c, result)
}

func (api *API) GetUsers(c echo.Context) error {
    users := make([]map[string]string, 0)

    re := c.FormValue("re")
    limit := 10

    if parsedLimit, err := strconv.Atoi(c.FormValue("limit")); err == nil {
        limit = parsedLimit
    }

    api.storage.IterateUsers(limit, re, func (user User) {
        properties := make(map[string]string)

        for _, key := range []string{"fullname", "picture", "public", "address"} {
            properties[key] = user.Properties[key]
        }
        properties["login"] = user.Username

        users = append(users, properties)
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

    user := api.storage.GetUser(c.FormValue("to"))

    if user == nil {
        return api.Error(c, fmt.Sprintf("Can't find user %s", login))
    }

    message := Message{
        From: login,
        To: c.FormValue("to"),
        Author: login,
        Message: c.FormValue("message"),
    }
    api.storage.SaveMessage(&message, user.AutoReply)

    message = Message{
        From: c.FormValue("to"),
        To: login,
        Author: login,
        Message: c.FormValue("message"),
    }
    api.storage.SaveMessage(&message, user.AutoReply)

    result := map[string]interface{}{}

    return api.OK(c, result)
}

func (api *API) GetConversation(c echo.Context) error {
    token := c.Request().Header.Get("token")
    login, err := api.crypto.LoginFromToken(token)

    if err != nil {
        return api.Error(c, "You should login first")
    }

    messages := make([]string, 0)
    to := c.FormValue("to")

    api.storage.IterateMessages(login, to, func (message Message) {
        messages = append(messages, fmt.Sprintf("%s > %s", message.Author, message.Message))
    })

    result := map[string]interface{}{
        "name": to,
        "messages": messages,
    }

    return api.OK(c, result)
}

func (api *API) AutoReply(c echo.Context) error {
    token := c.Request().Header.Get("token")
    login, err := api.crypto.LoginFromToken(token)

    if err != nil {
        return api.Error(c, "You should login first")
    }

    user := api.storage.GetUser(login)

    if user == nil {
        return api.Error(c, fmt.Sprintf("Can't find user %s", login))
    }

    user.AutoReply = true
    api.storage.Mutex.Lock()
    api.storage.Last[user.Username] = make(chan *Message)
    api.storage.Mutex.Unlock()

    api.storage.SaveUser(user)

    StartBot(user, api.storage)

    result := map[string]interface{}{}
    return api.OK(c, result)

}
