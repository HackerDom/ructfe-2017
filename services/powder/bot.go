package main

import (
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
    storage.IterateUsers(0, "", func (user User) {
        if user.AutoReply {
            storage.Mutex.Lock()
            storage.Last[user.Username] = make(chan *Message)
            storage.Mutex.Unlock()
            StartBot(&user, storage)
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
    return g * 0.003
}

func (bot *Bot) Listen(message *Message) {
    if message == nil {
        return
    }

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

    goal.Update(g)
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
    messages := make([]*Message, 0)

    if message == nil {
        return messages
    }

    user := bot.user
    if message.Author == user.Username {
        return messages
    }

    goal, ok := bot.goals[message.Author]
    if !ok {
        goal = NewGoal()
        bot.goals[message.Author] = goal
    }

    key, ok := user.Properties["prime1"]
    if !ok {
        key = "Moscow, Red Square, 1"
    }

    messages = addMessage(user,
                          message.Author,
                          goal.Status(user, key),
                          messages)

    return messages
}

func StartBot(user *User, storage *Storage) {
    go func() {
        bot := NewBot(user)
        storage.Mutex.Lock()
        channel := storage.Last[user.Username]
        storage.Mutex.Unlock()
        for {
            lastMessage := <-channel
            bot.Listen(lastMessage)
            for _, message := range bot.Say(lastMessage) {
                user := storage.GetUser(message.To)

                if user == nil {
                    continue
                }

                storage.SaveMessage(message, user.AutoReply)
            }
        }
    }()
}
