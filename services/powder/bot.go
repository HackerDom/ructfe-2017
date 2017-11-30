package main

import (
    "fmt"
    "time"
    "crypto/md5"
    "io"
)

type Bot struct {
    user *User
    goals map[string]*Goal
}

func NewBot(user *User) *Bot {
    return &Bot{
        user: user,
        goals: make(map[string]*Goal),
    }
}

func SetupAutoReply(storage *Storage) {
    storage.IterateUsers(0, func (user *User) {
        if user.AutoReply {
            StartBot(user, storage)
        }
    })
}

func understandMessage(message string) float32 {
    h := md5.New()

    io.WriteString(h, message)
    var g float32 = 0
    for _, b := range h.Sum(nil) {
        g += (float32(b) - 127)
    }

    g /= float32(len(h.Sum(nil)))
    return g * 0.001
}

func (bot *Bot) Listen(message *Message) {
    user := bot.user
    if message.Author == user.Username {
        return
    }

    g := understandMessage(message.Message)
    goal, ok := bot.goals[message.Author]
    if !ok {
        goal = NewGoal()
        bot.goals[message.Author] = goal
    }

    fmt.Println(g)
    goal.Update(g)

    fmt.Printf("%v %f\n", goal, goal.HowFar())
}

func addMessage(user *User, to string, message string, messages []*Message) []*Message {
    botMessage := &Message{
        From: user.Username,
        To: to,
        Author: user.Username,
        Message: message,
    }
    messages = append(messages, botMessage)

    botMessage = &Message{
        From: to,
        To: user.Username,
        Author: user.Username,
        Message: message,
    }
    messages = append(messages, botMessage)
    return messages
}

func (bot *Bot) Say(message *Message) []*Message {
    user := bot.user
    messages := make([]*Message, 0)

    if message.Author == user.Username {
        return messages
    }

    goal, ok := bot.goals[message.Author]
    if !ok {
        goal = NewGoal()
        bot.goals[message.Author] = goal
    }

    messages = addMessage(user,
                          message.Author,
                          goal.Status(user, "goal"),
                          messages)

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
            time.Sleep(time.Second)
        }
    }()
}
