package main

import (
    "github.com/labstack/echo"
)

type Users struct {
    state map[string]string
}

type API struct {
    users *Users
}

func NewUsers() *Users {
    return &Users{state: make(map[string]string)}
}

func NewAPI() *API {
    return &API{users: NewUsers()}
}

func (api *API) OK(c echo.Context, value map[string]interface{}) error {
    value["error"] = false;
    value["status"] = "ok";
    return c.JSON(200, value)
}

func (users *Users) GetUsers() []string {
    keys := make([]string, 0, len(users.state))
    for k := range users.state {
        keys = append(keys, k)
    }
    return keys
}

func (users *Users) AddUser(name string) {
    users.state[name] = name
}

func (api *API) Bind(group *echo.Group) {
    group.GET("/v1/user", api.ListUsers)
    group.POST("/v1/user", api.AddUser)
    group.POST("/v1/token", api.GetToken)
}

func (api *API) ListUsers(c echo.Context) error {
    return c.JSON(200, api.users.GetUsers())
}

func (api *API) AddUser(c echo.Context) error {
    name := c.FormValue("name")
    api.users.AddUser(name)
    return c.JSON(200, map[string]interface{}{})
}

func (api *API) GetToken(c echo.Context) error {
    result := map[string]interface{}{
        "token": "qwer",
    }
    return api.OK(c, result)
}
