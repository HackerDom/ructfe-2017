package main

import (
    "time"
    "github.com/asdine/storm"
    "github.com/asdine/storm/q"
)
type Storage struct {
    db *storm.DB
}

type User struct {
    Username string `storm:"id"`
    Properties map[string]string
    Salt string
    Hash []byte
    CreatedAt time.Time `stort:"index"`
}

func NewUser(login string, password string, crypto* Crypto) *User {
    salt := crypto.CreateSalt()
    hash := crypto.PasswordHash(salt, password)

    return &User{
        Username: login,
        Salt: salt,
        Hash: hash,
        Properties: make(map[string]string),
    }
}

type Message struct {
    Ts int `storm:"id,increment"`
    From string `storm:"index"`
    To string `storm:"index"`
    Author string
    Message string
    SendedAt time.Time `storm:"index"`
}

func NewStorage() *Storage {
    db, err := storm.Open("powder.db")

    if err != nil {
        panic(err)
    }

    return &Storage{db: db}
}

func (storage *Storage) GetUser(username string) *User {
    var user User
    err := storage.db.One("Username", username, &user)

    if err != nil {
        return nil
    }

    return &user
}

func (storage *Storage) SaveUser(user *User) {
    ok := storage.GetUser(user.Username)
    if ok != nil {
        err := storage.db.Update(user)
        if err != nil {
            panic(err)
        }
    } else {
        err := storage.db.Save(user)
        if err != nil {
            panic(err)
        }
    }
}

func (storage *Storage) IterateUsers(fn func(user *User)) {
    var users []User
    err := storage.db.All(&users, storm.Limit(10))

    if err != nil {
        panic(err)
    }

    for _, u := range users {
        fn(&u)
    }
}

func (storage *Storage) SaveMessage(message *Message) {
    message.SendedAt = time.Now()
    err := storage.db.Save(message)

    if err != nil {
        panic(err)
    }
}

func (storage *Storage) IterateMessages(from string, to string, fn func(_ *Message)) {
    var messages []Message
    query := storage.db.Select(q.Eq("From", from), q.Eq("To", to)).OrderBy("SendedAt").Limit(10)
    query.Find(&messages)

    for _, m := range messages {
        fn(&m)
    }
}

func (storage *Storage) LastMessage(to string) *Message {
    var message Message
    err := storage.db.Select(q.Eq("To", to)).OrderBy("SendedAt").Reverse().First(&message)
    if err != nil {
        return nil
    }
    return &message
}
