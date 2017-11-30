package main

import (
    "math/rand"
    "crypto/md5"
    "io"
)

type Crypto struct {
    masterKey []byte
}

func NewCrypto() *Crypto {
    return &Crypto{
        masterKey: []byte("DONT_FORGET_TO_CHANGE_IT"),
    }
}

func (*Crypto) CreateSalt() string {
    const n = 4
    var letters = []rune("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
    salt := make([]rune, n)
    for i := range salt {
        salt[i] = letters[rand.Intn(len(letters))]
    }
    return string(salt)
}

func (*Crypto) PasswordHash(salt string, password string) []byte {
    h := md5.New()
    io.WriteString(h, salt)
    io.WriteString(h, password)
    return h.Sum(nil)
}

func (crypto *Crypto) MakeToken(login string) string {
    return login
}

func (crypto *Crypto) LoginFromToken(token string) (string, error) {
    return token, nil
}
