// Программа на языке Си, которая строит пирамиду заданной высоты с использованием хэшей (#).
// RU: Этот код позволяет пользователю ввести высоту пирамиды и строит её.
// EN: This code allows the user to enter the height of the pyramid and builds it.
// FR: Ce code permet à l'utilisateur de saisir la hauteur de la pyramide et la construit.
// ES: Este código permite al usuario ingresar la altura de la pirámide y la construye.

#include <stdio.h>

int main() {
    int height;

    // RU: Запрашиваем высоту пирамиды от пользователя (от 1 до 8).
    // EN: Asking the user for the height of the pyramid (from 1 to 8).
    // FR: Demande à l'utilisateur la hauteur de la pyramide (de 1 à 8).
    // ES: Solicitar al usuario la altura de la pirámide (de 1 a 8).
    do {
        printf("Height: ");
        scanf("%d", &height);
    } while (height < 1 || height > 8);

    // RU: Строим пирамиду указанной высоты.
    // EN: Building a pyramid of the specified height.
    // FR: Construire une pyramide de la hauteur spécifiée.
    // ES: Construir una pirámide de la altura especificada.
    for (int i = 1; i <= height; i++) {
        // RU: Печатаем пробелы слева.
        // EN: Printing spaces on the left.
        // FR: Impression des espaces à gauche.
        // ES: Imprimir espacios a la izquierda.
        for (int j = 0; j < height - i; j++) {
            printf(" ");
        }

        // RU: Печатаем хэши слева.
        // EN: Printing hashes on the left.
        // FR: Impression des hachures à gauche.
        // ES: Imprimir almohadillas a la izquierda.
        for (int j = 0; j < i; j++) {
            printf("#");
        }

        // RU: Печатаем промежуток между двумя частями пирамиды.
        // EN: Printing the gap between the two parts of the pyramid.
        // FR: Impression de l'espace entre les deux parties de la pyramide.
        // ES: Imprimir el espacio entre las dos partes de la pirámide.
        printf("  ");

        // RU: Печатаем хэши справа.
        // EN: Printing hashes on the right.
        // FR: Impression des hachures à droite.
        // ES: Imprimir almohadillas a la derecha.
        for (int j = 0; j < i; j++) {
            printf("#");
        }

        // RU: Переход на следующую строку.
        // EN: Moving to the next line.
        // FR: Passage à la ligne suivante.
        // ES: Pasar a la siguiente línea.
        printf("\n");
    }

    return 0;
}
