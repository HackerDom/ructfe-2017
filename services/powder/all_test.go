package main

import (
    "testing"
    "bytes"
)

func TestHash(t *testing.T) {
    crypto := NewCrypto()

    userA := NewUser("a", "a", crypto)
    userB := NewUser("b", "a", crypto)

    hash := crypto.PasswordHash(userA.Salt, "a")
    if !bytes.Equal(userA.Hash, hash) {
        t.Error("!bytes.Equal(userA.Hash, hash)")
    }

    hash = crypto.PasswordHash(userB.Salt, "a")
    if !bytes.Equal(userB.Hash, hash) {
        t.Error("!bytes.Equal(userB.Hash, hash)", userB.Hash, hash)
    }

    hash = crypto.PasswordHash(userB.Salt, "a")
    if bytes.Equal(userA.Hash, hash) {
        t.Error("bytes.Equal(userA.Hash, hash)")
    }

}

func TestToken(t *testing.T) {
    crypto := NewCrypto()


}
