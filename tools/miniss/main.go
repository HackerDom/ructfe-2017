package main

import (
    "fmt"
    "os"
    "os/exec"
    "encoding/hex"
    "crypto/rand"
    "time"
    "syscall"
    r "math/rand"
    "strings"
    "strconv"
)

type TCase struct {
    Id string
    Flag string
    Vuln string

    IdForGet string
    StatusCode int
}

func RandomString(n int) string {
    bytes := make([]byte, n)
    rand.Read(bytes)
    return hex.EncodeToString(bytes)
}

func NewCase() *TCase {
    return &TCase{
        Id: fmt.Sprintf("%s-%s-%s", RandomString(2), RandomString(2), RandomString(2)),
        Flag: fmt.Sprintf("%s=", RandomString(16)[:31]),
        Vuln: "1",
    }
}

type TAction struct {
    Type string
    Case *TCase

}

type TSS struct {
    Checker string
    Hostname string
    History []*TAction
    Stats map[int]int
}

func NewTSS(checker string, hostname string) *TSS {
    return &TSS{
        Checker: checker,
        Hostname: hostname,
        History: make([]*TAction, 0),
        Stats: make(map[int]int),
    }
}

func (ss *TSS) Exec(action *TAction) {
    out, err := exec.Command(ss.Checker,
                             action.Type,
                             ss.Hostname,
                             action.Case.Id,
                             action.Case.Flag,
                             action.Case.Vuln).Output()

    fmt.Printf("%s %s %s %s %s\n", action.Type,
                                   ss.Hostname,
                                   action.Case.Id,
                                   action.Case.Flag,
                                   action.Case.Vuln)
    if string(out) != "" {
        action.Case.IdForGet = strings.TrimSpace(string(out))
    }
    action.Case.StatusCode = err.(*exec.ExitError).Sys().(syscall.WaitStatus).ExitStatus()
}

func (ss *TSS) MakePut() {
    action := &TAction{
        Type: "PUT",
        Case: NewCase(),
    }
    ss.Exec(action)
    ss.Stats[action.Case.StatusCode] += 1
    ss.History = append(ss.History, action)
}

func (ss *TSS) MakeGet(putAction *TAction) {
    c := NewCase()

    c.Id = putAction.Case.IdForGet
    c.Flag = putAction.Case.Flag

    action := &TAction{
        Type: "GET",
        Case: c,
    }

    ss.Exec(action)
    ss.Stats[action.Case.StatusCode] += 1
    ss.History = append(ss.History, action)
}

func (ss *TSS) MakeRandomGet() {
    putActions := make([]*TAction, 0)
    for _, action := range ss.History {
        if action.Type == "PUT" {
            putActions = append(putActions, action)
        }
    }

    if len(putActions) == 0 {
        return
    }

    randomAction := putActions[r.Intn(len(putActions))]
    ss.MakeGet(randomAction)
}

func main() {
    if len(os.Args) != 4 {
        return
    }

    checker, hostname, concurrencyS := os.Args[1], os.Args[2], os.Args[3]
    ss := NewTSS(checker, hostname)

    concurrency, _ := strconv.Atoi(concurrencyS)

    for i := 0; i < concurrency; i++ {
        go func() {
            for {
                ss.MakePut()
                ss.MakeRandomGet()

                for statusCode, count := range ss.Stats {
                    fmt.Printf("%d\t%d\n", statusCode, count)
                }
            }
        }()
    }
    for {
        time.Sleep(time.Second)
    }
}
