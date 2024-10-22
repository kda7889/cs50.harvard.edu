// Программа на языке Си, которая шифрует сообщения с использованием подстановочного шифра.
// RU: Эта программа позволяет пользователю зашифровать сообщение, используя подстановочный шифр с заданным ключом.
// EN: This program allows the user to encrypt a message using a substitution cipher with a given key.
// FR: Ce programme permet à l'utilisateur de chiffrer un message en utilisant un chiffrement par substitution avec une clé donnée.
// ES: Este programa permite al usuario cifrar un mensaje utilizando un cifrado por sustitución con una clave dada.

#include <stdio.h>
#include <cs50.h>
#include <string.h>
#include <ctype.h>

bool validate_key(string key);
void encrypt_message(string plaintext, string key);

int main(int argc, string argv[])
{
    // RU: Проверяем количество аргументов командной строки.
    // EN: Check the number of command line arguments.
    // FR: Vérifiez le nombre d'arguments de ligne de commande.
    // ES: Verificar el número de argumentos de línea de comandos.
    if (argc != 2)
    {
        printf("Usage: ./substitution key\n");
        return 1;
    }

    string key = argv[1];

    // RU: Проверяем правильность ключа.
    // EN: Validate the key.
    // FR: Validez la clé.
    // ES: Validar la clave.
    if (!validate_key(key))
    {
        printf("Key must contain 26 unique alphabetic characters.\n");
        return 1;
    }

    // RU: Запрашиваем обычный текст у пользователя.
    // EN: Request plaintext from the user.
    // FR: Demander le texte en clair à l'utilisateur.
    // ES: Solicitar texto plano del usuario.
    string plaintext = get_string("plaintext: ");

    // RU: Шифруем и выводим зашифрованное сообщение.
    // EN: Encrypt and print the ciphertext.
    // FR: Chiffrer et imprimer le texte chiffré.
    // ES: Cifrar e imprimir el texto cifrado.
    printf("ciphertext: ");
    encrypt_message(plaintext, key);
    printf("\n");

    return 0;
}

// RU: Функция для проверки правильности ключа.
// EN: Function to validate the key.
// FR: Fonction pour valider la clé.
// ES: Función para validar la clave.
bool validate_key(string key)
{
    // RU: Ключ должен содержать ровно 26 символов.
    // EN: The key must contain exactly 26 characters.
    // FR: La clé doit contenir exactement 26 caractères.
    // ES: La clave debe contener exactamente 26 caracteres.
    if (strlen(key) != 26)
    {
        return false;
    }

    bool used[26] = {false};

    for (int i = 0; i < 26; i++)
    {
        if (!isalpha(key[i]))
        {
            return false;
        }

        int index = toupper(key[i]) - 'A';
        if (used[index])
        {
            return false;
        }
        used[index] = true;
    }

    return true;
}

// RU: Функция для шифрования сообщения.
// EN: Function to encrypt the message.
// FR: Fonction pour chiffrer le message.
// ES: Función para cifrar el mensaje.
void encrypt_message(string plaintext, string key)
{
    for (int i = 0, n = strlen(plaintext); i < n; i++)
    {
        char c = plaintext[i];
        if (isalpha(c))
        {
            // RU: Сохраняем регистр буквы (заглавная или строчная).
            // EN: Preserve the case of the letter (uppercase or lowercase).
            // FR: Conserver la casse de la lettre (majuscule ou minuscule).
            // ES: Preservar el caso de la letra (mayúscula o minúscula).
            if (isupper(c))
            {
                printf("%c", toupper(key[c - 'A']));
            }
            else
            {
                printf("%c", tolower(key[c - 'a']));
            }
        }
        else
        {
            // RU: Если символ не является буквой, выводим его без изменений.
            // EN: If the character is not a letter, print it unchanged.
            // FR: Si le caractère n'est pas une lettre, l'imprimer tel quel.
            // ES: Si el carácter no es una letra, imprimirlo sin cambios.
            printf("%c", c);
        }
    }
}
