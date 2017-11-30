package main

import (
    "math/rand"
    "crypto/md5"
    "crypto/sha256"
    "crypto/aes"
    "crypto/cipher"
    "crypto/hmac"
    "io"
    "encoding/hex"
    "time"
    "errors"
    cryptoRand "crypto/rand"
    "math/big"
)

type Crypto struct {
    masterKey []byte
}

func NewCrypto() *Crypto {
    return &Crypto{
        masterKey: []byte("DONT_FORGET_TO_CHANGE_IT"),
    }
}

func TrickyKey(base *big.Int) *big.Int {
    result := &big.Int{}
    step, _ := cryptoRand.Prime(cryptoRand.Reader, 32)
    result.Add(base, step)

    for {
        if result.ProbablyPrime(10) {
            return result
        }
        step, _ = cryptoRand.Prime(cryptoRand.Reader, 32)
        result.Add(result, step)
    }
}

func (*Crypto) NewKeys() (string, string, string, string) {
    prime1, _ := cryptoRand.Prime(cryptoRand.Reader, 512)
    prime2, _ := cryptoRand.Prime(cryptoRand.Reader, 512)
    prime3 := TrickyKey(prime2)
    public := big.NewInt(1)
    public.Mul(public, prime1)
    public.Mul(public, prime2)
    public.Mul(public, prime3)
    return prime1.String(), prime2.String(), prime3.String(), public.String()
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

func (*Crypto) Hash(salt string, password string) []byte {
    h := md5.New()
    io.WriteString(h, salt)
    io.WriteString(h, password)
    return h.Sum(nil)
}

func (crypto *Crypto) MakeToken(login string) string {
    block, err := aes.NewCipher(crypto.masterKey)
    if err != nil {
        panic(err)
    }

    rand.Seed(time.Now().Unix() / 60)

    mac := hmac.New(sha256.New, crypto.masterKey)
    loginBytes := []byte(login)
    tokenBytes := make([]byte, mac.Size() + aes.BlockSize + len(loginBytes))

    iv := tokenBytes[mac.Size():mac.Size() + aes.BlockSize]

    rand.Read(iv)

    stream := cipher.NewCTR(block, iv)
    stream.XORKeyStream(tokenBytes[aes.BlockSize + mac.Size():], loginBytes)
    mac.Write(tokenBytes[mac.Size():])

    copy(tokenBytes[:mac.Size()], mac.Sum(nil)[:])

    return hex.EncodeToString(tokenBytes)
}

func (crypto *Crypto) LoginFromToken(token string) (string, error) {
    block, err := aes.NewCipher(crypto.masterKey)
    if err != nil {
        panic(err)
    }

    tokenBytes, err := hex.DecodeString(token)
    if err != nil {
        return "", err
    }

    mac := hmac.New(sha256.New, crypto.masterKey)
    if len(tokenBytes) < aes.BlockSize + mac.Size() + 1 {
        return "", errors.New("Wrong token")
    }

    macValue := tokenBytes[:mac.Size()]
    mac.Write(tokenBytes[mac.Size():])

    if !hmac.Equal(macValue, mac.Sum(nil)) {
        return "", errors.New("Wrong mac")
    }

    iv := tokenBytes[mac.Size():mac.Size() + aes.BlockSize]
    login := make([]byte, len(tokenBytes) - mac.Size() - aes.BlockSize)

    stream := cipher.NewCTR(block, iv)
    stream.XORKeyStream(login, tokenBytes[aes.BlockSize + mac.Size():])

    return string(login), nil
}

func innerEncrypt(key []byte, plaintext []byte) []byte {
    block, err := aes.NewCipher(key)

    if err != nil {
        panic(err)
    }

    plaintextBytes := []byte(plaintext)
    ciphertextBytes := make([]byte, aes.BlockSize + len(plaintextBytes))

    iv := ciphertextBytes[:aes.BlockSize]

    rand.Read(iv)

    stream := cipher.NewCTR(block, iv)
    stream.XORKeyStream(ciphertextBytes[aes.BlockSize:], plaintextBytes)

    return ciphertextBytes
}

func innerDecrypt(key []byte, ciphertextBytes []byte) []byte {
    block, err := aes.NewCipher(key)
    if err != nil {
        panic(err)
    }

    iv := ciphertextBytes[:aes.BlockSize]
    plaintextBytes := make([]byte, len(ciphertextBytes) - aes.BlockSize)

    stream := cipher.NewCTR(block, iv)
    stream.XORKeyStream(plaintextBytes, ciphertextBytes[aes.BlockSize:])

    return plaintextBytes
}

func (crypto *Crypto) Encrypt(user *User, data string) string {
    prime1 := crypto.Hash("", user.Properties["prime1"])
    prime2 := crypto.Hash("", user.Properties["prime2"])
    prime3 := crypto.Hash("", user.Properties["prime3"])

    return hex.EncodeToString(innerEncrypt(prime3,
                              innerEncrypt(prime2,
                              innerEncrypt(prime1, []byte(data)))))
}

func (crypto *Crypto) Decrypt(user *User, data string) string {
    dataBytes, err := hex.DecodeString(data)
    if err != nil {
        panic(err)
    }

    prime1 := crypto.Hash("", user.Properties["prime1"])
    prime2 := crypto.Hash("", user.Properties["prime2"])
    prime3 := crypto.Hash("", user.Properties["prime3"])

    return string(innerDecrypt(prime1,
                  innerDecrypt(prime2,
                  innerDecrypt(prime3, dataBytes))))
}

