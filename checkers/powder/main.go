package main

import (
    "fmt"
    "net/http"
    "net/url"
    "io/ioutil"
    "encoding/json"
    "errors"
    "strings"
    "crypto/rand"
    "encoding/hex"
    "os"
)

type Server struct {
    Host string
}

type User struct {
    Login string
    Password string
    Token string
}

func (server *Server) SignUpUrl() string {
    return fmt.Sprintf("%s/api/v1/auth/signup", server.Host)
}

func (server *Server) LoginUrl() string {
    return fmt.Sprintf("%s/api/v1/auth/login", server.Host)
}

func (server *Server) GetProfileUrl() string {
    return fmt.Sprintf("%s/api/v1/user/profile", server.Host)
}

func (server *Server) SaveProfileUrl() string {
    return fmt.Sprintf("%s/api/v1/user/profile", server.Host)
}

func (server *Server) GetUsersUrl(limit int, re string) string {
    return fmt.Sprintf("%s/api/v1/users?limit=%d&re=%s", server.Host, limit, re)
}

func (server *Server) AutoReplyUrl() string {
    return fmt.Sprintf("%s/api/v1/autoreply", server.Host)
}

func (server *Server) SignUp(user *User) (*User, error, int) {
    response, err := http.PostForm(server.SignUpUrl(), url.Values{
        "login": {user.Login},
        "password": {user.Password},
    })

    if err != nil {
        return user, err, DOWN
    }

    defer response.Body.Close()
    body, err := ioutil.ReadAll(response.Body)

    var data map[string]interface{}
    if err := json.Unmarshal(body, &data); err != nil {
        return user, err, MUMBLE
    }

    if data["error"].(bool) {
        return user, errors.New(data["errorMessage"].(string)), MUMBLE
    }

    user.Token = data["token"].(string)

    return user, nil, OK
}

func (server *Server) Login(user *User) (*User, error, int) {
    response, err := http.PostForm(server.LoginUrl(), url.Values{
        "login": {user.Login},
        "password": {user.Password},
    })

    if err != nil {
        return user, err, DOWN
    }

    defer response.Body.Close()
    body, err := ioutil.ReadAll(response.Body)
    if err != nil {
        return user, err, MUMBLE
    }

    var data map[string]interface{}
    if err := json.Unmarshal(body, &data); err != nil {
        return user, err, MUMBLE
    }

    if data["error"].(bool) {
        return user, errors.New(data["errorMessage"].(string)), CORRUPT
    }

    user.Token = data["token"].(string)

    return user, nil, OK
}

func (server *Server) GetProfile(user *User) (map[string]string, error, int) {
    if user.Token == "" {
        return nil, errors.New("user.Token must be filled"), CHECKER_ERROR
    }

    request, err := http.NewRequest("GET", server.GetProfileUrl(), nil)
    if err != nil {
        return nil, err, CHECKER_ERROR
    }
    request.Header.Add("token", user.Token)
    client := &http.Client{}
    response, err := client.Do(request)

    if err != nil {
        return nil, err, DOWN
    }

    defer response.Body.Close()
    body, err := ioutil.ReadAll(response.Body)
    if err != nil {
        return nil, err, MUMBLE
    }

    var data map[string]interface{}
    if err := json.Unmarshal(body, &data); err != nil {
        return nil, err, MUMBLE
    }

    if data["error"].(bool) {
        return nil, errors.New(data["errorMessage"].(string)), MUMBLE
    }

    profile := make(map[string]string)
    for key, value := range data {
        if key == "error" {
            continue
        }
        profile[key] = value.(string)
    }

    return profile, nil, OK
}

func (server *Server) SaveProfile(user *User, profile map[string]string) (error, int) {
    if user.Token == "" {
        return errors.New("user.Token must be filled"), CHECKER_ERROR
    }

    values := url.Values{}
    for key, value := range profile {
        values.Add(key, value)
    }

    request, err := http.NewRequest("POST",
                                    server.SaveProfileUrl(),
                                    strings.NewReader(values.Encode()))
    if err != nil {
        return err, DOWN
    }

    request.Header.Add("token", user.Token)
    request.Header.Set("Content-Type", "application/x-www-form-urlencoded")

    client := &http.Client{}
    response, err := client.Do(request)

    if err != nil {
        return err, MUMBLE
    }

    defer response.Body.Close()
    body, err := ioutil.ReadAll(response.Body)
    if err != nil {
        return err, MUMBLE
    }

    var data map[string]interface{}
    if err := json.Unmarshal(body, &data); err != nil {
        return err, MUMBLE
    }

    if data["error"].(bool) {
        return errors.New(data["errorMessage"].(string)), MUMBLE
    }

    return nil, OK
}

func (server *Server) GetUsers(limit int, re string) ([]map[string]string, error) {
    response, err := http.Get(server.GetUsersUrl(limit, re))

    if err != nil {
        return nil, err
    }

    defer response.Body.Close()
    body, err := ioutil.ReadAll(response.Body)

    var data map[string]interface{}
    if err := json.Unmarshal(body, &data); err != nil {
        return nil, err
    }

    users := make([]map[string]string, 0)

    if data["error"].(bool) {
        return users, errors.New(data["errorMessage"].(string))
    }

    for _, user := range data["users"].([]interface{}) {
        profile := make(map[string]string)
        for key, value := range user.(map[string]interface{}) {
            profile[key] = value.(string)
        }
        users = append(users, profile)
    }

    return users, nil

}

func (server *Server) AutoReply(user *User) (error, int) {
    if user.Token == "" {
        return errors.New("user.Token must be filled"), CHECKER_ERROR
    }

    request, err := http.NewRequest("POST", server.AutoReplyUrl(), nil)
    if err != nil {
        return err, DOWN
    }

    request.Header.Add("token", user.Token)

    client := &http.Client{}
    response, err := client.Do(request)

    if err != nil {
        return err, MUMBLE
    }

    defer response.Body.Close()
    body, err := ioutil.ReadAll(response.Body)
    if err != nil {
        return err, MUMBLE
    }

    var data map[string]interface{}
    if err := json.Unmarshal(body, &data); err != nil {
        return err, MUMBLE
    }

    if data["error"].(bool) {
        return errors.New(data["errorMessage"].(string)), MUMBLE
    }

    return nil, OK
}

const (
    OK = 101
    CORRUPT = 102
    MUMBLE = 103
    DOWN = 104
    CHECKER_ERROR = 110
)

func Info(args []string) int {
    fmt.Println("1")
    return OK
}

func Check(args []string) int {
    return OK
}

func RandomString(n int) string {
    bytes := make([]byte, n)
    rand.Read(bytes)
    return hex.EncodeToString(bytes)
}

func Put(args []string) int {
    if len(args) != 4 {
        return CHECKER_ERROR
    }

    hostname, id, flag := args[0], args[1], args[2]
    password := RandomString(32)

    server := &Server{Host: fmt.Sprintf("http://%s", hostname)}
    user := &User{Login: id, Password: password}
    user, err, code := server.SignUp(user)

    if err != nil {
        return code
    }

    updates := map[string]string{"address": flag}
    err, code = server.SaveProfile(user, updates)

    if err != nil {
        return code
    }

    err, code = server.AutoReply(user)

    if err != nil {
        return code
    }

    fmt.Println(strings.Join([]string{id, password}, ","))

    return OK
}

func Get(args []string) int {
    if len(args) != 4 {
        return CHECKER_ERROR
    }

    hostname, joinedId, flag := args[0], args[1], args[2]
    splittedId := strings.Split(joinedId, ",")

    id, password := splittedId[0], splittedId[0]

    if len(splittedId) == 2 {
        password = splittedId[1]
    }

    server := &Server{Host: fmt.Sprintf("http://%s", hostname)}
    user := &User{Login: id, Password: password}

    user, err, code := server.Login(user)
    if err != nil {
        return code
    }

    profile, err, code := server.GetProfile(user)
    if err != nil {
        return code
    }

    flagFromService, ok := profile["address"]
    if !ok || flagFromService != flag {
        return CORRUPT
    }

    return OK
}


func main() {
    if len(os.Args) < 2 {
        os.Exit(CHECKER_ERROR)
    }
    handlers := map[string](func (args []string) int) {
        "INFO": Info,
        "CHECK": Check,
        "PUT": Put,
        "GET": Get,
    }
    mode := os.Args[1]

    handler, ok := handlers[mode]
    if !ok {
        os.Exit(CHECKER_ERROR)
    }

    os.Exit(handler(os.Args[2:]))
}
