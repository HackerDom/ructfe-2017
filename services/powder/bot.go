package main

import (
    "fmt"
    "time"
)

type Bot struct {
    user *User
}

func NewBot(user *User) *Bot {
    return &Bot{user: user}
}

func SetupAutoReply(storage *Storage) {
    storage.IterateUsers(0, func (user *User) {
        if user.AutoReply {
            StartBot(user, storage)
        }
    })
}

func (bot *Bot) Listen(message *Message) {
}

func (bot *Bot) Say(message *Message) []*Message {
    user := bot.user
    messages := make([]*Message, 0)

    if message.Author != user.Username {
        botMessage := &Message{
            From: user.Username,
            To: message.Author,
            Author: user.Username,
            Message: fmt.Sprintf("Hi, I'm %s, nice to meet you!", user.Username),
        }
        messages = append(messages, botMessage)
        botMessage = &Message{
            From: message.Author,
            To: user.Username,
            Author: user.Username,
            Message: fmt.Sprintf("Hi, I'm %s, nice to meet you!", user.Username),
        }
        messages = append(messages, botMessage)
    }
    return messages
}

func StartBot(user *User, storage *Storage) {
    go func() {
        bot := NewBot(user)
        for {
            lastMessage := storage.LastMessage(user.Username)
            bot.Listen(lastMessage)
            for _, message := range bot.Say(lastMessage) {
                storage.SaveMessage(message)
            }
            time.Sleep(5 * time.Second)
        }
    }()
}
