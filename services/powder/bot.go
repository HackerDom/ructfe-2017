package main

import (
    "fmt"
    "time"
)

type Bot struct {
}

func NewBot() *Bot {
    return &Bot{}
}

func SetupAutoReply(storage *Storage) {
    storage.IterateUsers(0, func (user *User) {
        fmt.Printf("%v", user)
        if user.AutoReply {
            StartBot(user, storage)
        }
    })
}

func StartBot(user *User, storage *Storage) {
    go func() {
        _ = NewBot()
        for {
            lastMessage := storage.LastMessage(user.Username)
            if lastMessage.Author != user.Username {
                message := &Message{
                    From: user.Username,
                    To: lastMessage.Author,
                    Author: user.Username,
                    Message: fmt.Sprintf("Hi, I'm %s, nice to meet you!", user.Username),
                }
                storage.SaveMessage(message)

                message = &Message{
                    From: lastMessage.Author,
                    To: user.Username,
                    Author: user.Username,
                    Message: fmt.Sprintf("Hi, I'm %s, nice to meet you!", user.Username),
                }
                storage.SaveMessage(message)
            }
            time.Sleep(5 * time.Second)
        }
    }()
}
