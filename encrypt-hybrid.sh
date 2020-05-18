#!/bin/bash

# usage: enrypt-hybrid <file-to-encrypt>.txt <public-key-of-recipient>.pem

file_to_encrypt="$1"
public_key="$2"

# creating a random symetric key
openssl rand -base64 32 > key.bin

# encrypt symetric key using public key of recepient
openssl rsautl -encrypt -inkey "${public_key}" -pubin -in key.bin -out key.bin.enc

# encrypt destination file using symetric key
openssl enc -d -aes-256-cbc -in "${file_to_encrypt}" -out "${file_to_encrypt}.enc" -kfile key.bin

echo "Done! send files 'key.bin.enc' and '${file_to_encrypt}.enc'"

