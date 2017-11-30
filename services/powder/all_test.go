package main

import (
    "testing"
    "bytes"
)

func TestHash(t *testing.T) {
    crypto := NewCrypto()

    userA := NewUser("a", "a", crypto)
    userB := NewUser("b", "a", crypto)

    hash := crypto.Hash(userA.Salt, "a")
    if !bytes.Equal(userA.Hash, hash) {
        t.Error("!bytes.Equal(userA.Hash, hash)")
    }

    hash = crypto.Hash(userB.Salt, "a")
    if !bytes.Equal(userB.Hash, hash) {
        t.Error("!bytes.Equal(userB.Hash, hash)", userB.Hash, hash)
    }

    hash = crypto.Hash(userB.Salt, "a")
    if bytes.Equal(userA.Hash, hash) {
        t.Error("bytes.Equal(userA.Hash, hash)")
    }

}

func TestToken(t *testing.T) {
    crypto := NewCrypto()

    token := crypto.MakeToken("qwer")
    login, err := crypto.LoginFromToken(token)

    if err != nil {
        t.Error("err != nil", err)
    }

    if login != "qwer" {
        t.Error("login != \"qwer\"", login)
    }

    _, err = crypto.LoginFromToken("")
    if err == nil {
        t.Error("err == nil, 1")
    }

    _, err = crypto.LoginFromToken("qwer")
    if err == nil {
        t.Error("err == nil, 2")
    }

    token = crypto.MakeToken("qwerqwerqwerqwerqwerqwerqwerqwerqwerqwerqwer")
    login, err = crypto.LoginFromToken(token)
    if err != nil {
        t.Error("err != nil")
    }

    if login != "qwerqwerqwerqwerqwerqwerqwerqwerqwerqwerqwer" {
        t.Error("login != \"qwerqwerqwerqwerqwerqwerqwerqwerqwerqwerqwer\"")
    }

}

func TestEncrypt(t *testing.T) {
    crypto := NewCrypto()
    user := NewUser("a", "b", crypto)

    plaintext := "qwer"
    ciphertext := crypto.Encrypt(user, plaintext)

    if plaintext == ciphertext {
        t.Error("plaintext == ciphertext")
    }

    if plaintext != crypto.Decrypt(user, ciphertext) {
        t.Error("plaintext != crypt.Decrypt(ciphertext)")
    }
}
