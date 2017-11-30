package main

import (
    "fmt"
    "math/rand"
)

type Goal struct {
    Goal float32
    State float32
}

func NewGoal() *Goal {
    return &Goal{
        Goal: rand.Float32(),
        State: 0.5,
    }
}

func (goal *Goal) Update(g float32) {
    goal.State += g
}

func (goal *Goal) HowFar() float32 {
    return (goal.Goal - goal.State) * (goal.Goal - goal.State)
}

func (goal *Goal) Status(user *User, message string) string {
    howFar := goal.HowFar()
    if howFar < 0.001 {
        return fmt.Sprintf("OK, I'll give what you want tonight. Let's meet here — %s", message)
    }
    if howFar < 0.01 {
        return fmt.Sprintf("I don't know, maybe we should meet each other.")
    }
    if howFar < 0.05 {
        return fmt.Sprintf("Hmm.")
    }
    if howFar < 0.1 {
        return fmt.Sprintf("Tell me more about you.")
    }
    if howFar < 0.15 {
        return fmt.Sprintf("Do I know you?")
    }
    if howFar < 0.2 {
        return fmt.Sprintf("Today is nice weather.")
    }

    return fmt.Sprintf("Hi, I'm %s, nice to meet you!", user.Username)
}
