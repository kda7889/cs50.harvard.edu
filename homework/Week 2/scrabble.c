// Программа на языке Си, которая определяет победителя в игре наподобие Scrabble.
// RU: Этот код позволяет двум игрокам вводить слова и определяет, кто из них набрал больше очков.
// EN: This code allows two players to enter words and determines who scored more points.
// FR: Ce code permet à deux joueurs d'entrer des mots et détermine qui a marqué plus de points.
// ES: Este código permite que dos jugadores ingresen palabras y determina quién obtuvo más puntos.

#include <stdio.h>
#include <cs50.h>
#include <string.h>
#include <ctype.h>

int compute_score(string word);

// RU: Главная функция программы.
// EN: Main function of the program.
// FR: Fonction principale du programme.
// ES: Función principal del programa.
int main(void)
{
    // RU: Запрос слов у двух игроков.
    // EN: Request words from both players.
    // FR: Demande des mots aux deux joueurs.
    // ES: Solicitar palabras de ambos jugadores.
    string word1 = get_string("Player 1: ");
    string word2 = get_string("Player 2: ");

    // RU: Подсчитываем очки для каждого игрока.
    // EN: Calculate the score for each player.
    // FR: Calculer le score pour chaque joueur.
    // ES: Calcular la puntuación para cada jugador.
    int score1 = compute_score(word1);
    int score2 = compute_score(word2);

    // RU: Определяем и выводим результат.
    // EN: Determine and print the result.
    // FR: Déterminer et afficher le résultat.
    // ES: Determinar e imprimir el resultado.
    if (score1 > score2)
    {
        printf("Player 1 wins!\n");
    }
    else if (score2 > score1)
    {
        printf("Player 2 wins!\n");
    }
    else
    {
        printf("Tie!\n");
    }
}

// RU: Функция для вычисления очков для заданного слова.
// EN: Function to compute the score for a given word.
// FR: Fonction pour calculer le score d'un mot donné.
// ES: Función para calcular la puntuación de una palabra dada.
int compute_score(string word)
{
    // RU: Очки для каждой буквы алфавита.
    // EN: Points for each letter of the alphabet.
    // FR: Points pour chaque lettre de l'alphabet.
    // ES: Puntos para cada letra del alfabeto.
    int points[] = {
        // RU: A=1, B=3, C=3, D=2, E=1, F=4, G=2, H=4, I=1, J=8, K=5, L=1, M=3, N=1, O=1, P=3, Q=10, R=1, S=1, T=1, U=1, V=4, W=4, X=8, Y=4, Z=10
        // EN: A=1, B=3, C=3, D=2, E=1, F=4, G=2, H=4, I=1, J=8, K=5, L=1, M=3, N=1, O=1, P=3, Q=10, R=1, S=1, T=1, U=1, V=4, W=4, X=8, Y=4, Z=10
        // FR: A=1, B=3, C=3, D=2, E=1, F=4, G=2, H=4, I=1, J=8, K=5, L=1, M=3, N=1, O=1, P=3, Q=10, R=1, S=1, T=1, U=1, V=4, W=4, X=8, Y=4, Z=10
        // ES: A=1, B=3, C=3, D=2, E=1, F=4, G=2, H=4, I=1, J=8, K=5, L=1, M=3, N=1, O=1, P=3, Q=10, R=1, S=1, T=1, U=1, V=4, W=4, X=8, Y=4, Z=10
        1, 3, 3, 2, 1, 4, 2, 4, 1, 8, 5, 1, 3, 1, 1, 3, 10, 1, 1, 1, 1, 4, 4, 8, 4, 10
    };
    int score = 0;

    // RU: Пробегаемся по всем буквам в слове и подсчитываем общие очки.
    // EN: Iterate over all letters in the word and calculate the total score.
    // FR: Parcourir toutes les lettres du mot et calculer le score total.
    // ES: Recorrer todas las letras de la palabra y calcular la puntuación total.
    for (int i = 0, n = strlen(word); i < n; i++)
    {
        if (isalpha(word[i]))
        {
            // RU: Приводим букву к верхнему регистру и вычисляем очки.
            // EN: Convert the letter to uppercase and compute the score.
            // FR: Convertir la lettre en majuscule et calculer le score.
            // ES: Convertir la letra a mayúscula y calcular la puntuación.
            int index = toupper(word[i]) - 'A';
            score += points[index];
        }
    }
    return score;
}
