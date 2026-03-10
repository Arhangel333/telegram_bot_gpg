#!/bin/bash

# Получаем ID ключа из файла (5-е поле строки pub)
KEY_ID_FULL=$(gpg --with-colons "$1" 2>/dev/null | grep "^uid:" | head -1 | cut -d':' -f10)

KEY_NAME=$(echo $KEY_ID_FULL | cut -d'<' -f1)
KEY_ID=$(echo $KEY_ID_FULL | cut -d'<' -f2)
KEY_ID=${KEY_ID%?}
echo "ID ключа: $KEY_ID"
echo "Name ключа: $KEY_NAME"




gpg --import $1
gpg --batch --yes --sign-key "$KEY_ID"
gpg --list-sign "$KEY_ID"
gpg --export $KEY_ID > $1