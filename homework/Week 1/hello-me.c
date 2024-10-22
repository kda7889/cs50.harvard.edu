// Программа на языке Си, которая запрашивает имя и выводит приветствие.
// RU: Этот код запрашивает имя пользователя и выводит строку приветствия.
// EN: This code asks for the user's name and prints a greeting.
// FR: Ce code demande le nom de l'utilisateur et imprime un message de salutation.
// ES: Este código solicita el nombre del usuario e imprime un saludo.

#include <stdio.h>

int main() {
    char name[50];
    
    // RU: Запрашиваем имя пользователя.
    // EN: Asking for the user's name.
    // FR: Demande le nom de l'utilisateur.
    // ES: Solicitar el nombre del usuario.
    printf("What's your name? ");
    fgets(name, sizeof(name), stdin);
    
    // RU: Выводим приветствие с именем пользователя.
    // EN: Printing a greeting with the user's name.
    // FR: Impression d'un message de salutation avec le nom de l'utilisateur.
    // ES: Imprimir un saludo con el nombre del usuario.
    printf("hello, %s", name);
    
    return 0;
} 
