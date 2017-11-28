package main

type Crypto struct {
    masterKey []byte
}

func NewCrypto() *Crypto {
    return &Crypto{
        masterKey: []byte("DONT_FORGET_TO_CHANGE_IT"),
    }
}

func (*Crypto) CreateSalt() []byte {
    return []byte("")
}

func (*Crypto) PasswordHash(salt []byte, password string) []byte {
    return []byte(password)
}

func (crypto *Crypto) MakeToken(login string) string {
    return login
}

func (crypto *Crypto) LoginFromToken(token string) (string, error) {
    return token, nil
}
