package main

import (
    "github.com/asdine/storm"
)
type Storage struct {
    db *storm.DB
}

type User struct {
    Username string `storm:"id"`
    Properties map[string]string
    Hash []byte
    Salt []byte
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
