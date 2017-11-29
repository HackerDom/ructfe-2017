package main

import (
    "time"
    "github.com/boltdb/bolt"
)
type Storage struct {
    db *bolt.DB
}

func NewStorage() *Storage {
    db, err := bolt.Open("powder.db", 0600, &bolt.Options{Timeout: 1 * time.Second})

    if err != nil {
        panic(err)
    }

    db.Update(func (tx *bolt.Tx) error {
        _, err := tx.CreateBucketIfNotExists([]byte("users"))
        if err != nil {
            panic(err)
        }
        return nil
    })

    return &Storage{db: db}
}

func (storage *Storage) GetUserProperty(username string, propertyName string) []byte {
    var propertyValue []byte
    storage.db.View(func(tx *bolt.Tx) error {
        usersBucket := tx.Bucket([]byte("users"))
        userBucket := usersBucket.Bucket([]byte(username))

        if userBucket == nil {
            return nil
        }

        propertyValue = userBucket.Get([]byte(propertyName))

        return nil
    })

    return propertyValue
}

func (storage *Storage) SetUserProperty(username string,
                                        propertyName string,
                                        propertyValue []byte) {
    storage.db.Update(func(tx *bolt.Tx) error {
        usersBucket := tx.Bucket([]byte("users"))
        userBucket, err := usersBucket.CreateBucketIfNotExists([]byte(username))

        if err != nil {
            panic(err)
        }

        err = userBucket.Put([]byte(propertyName), propertyValue)
        if err != nil {
            panic(err)
        }

        return nil
    })
}

func (storage *Storage) IterateUsers(fn func(login string, profile map[string]string)) {
    storage.db.View(func(tx *bolt.Tx) error {
        usersBucket := tx.Bucket([]byte("users"))
        usersBucket.ForEach(func(key []byte, _ []byte) error {
            properties := make(map[string]string)
            b := usersBucket.Bucket(key)

            for _, propertyName := range []string{"picture", "fullname"} {
                propertyValue := b.Get([]byte(propertyName))
                if propertyValue != nil {
                    properties[propertyName] = string(propertyValue)
                }
            }

            fn(string(key), properties)

            return nil
        })
        return nil
    })
}
