// Программа на языке Си, которая вычисляет уровень знаний, необходимый для понимания текста по индексу Коулмана-Лиу.
// RU: Эта программа принимает текст и вычисляет его уровень читаемости.
// EN: This program takes a text and computes its readability level.
// FR: Ce programme prend un texte et calcule son niveau de lisibilité.
// ES: Este programa toma un texto y calcula su nivel de legibilidad.

#include <stdio.h>
#include <cs50.h>
#include <string.h>
#include <ctype.h>
#include <math.h>

int count_letters(string text);
int count_words(string text);
int count_sentences(string text);

int main(void)
{
    // RU: Запрашиваем текст у пользователя.
    // EN: Request text from the user.
    // FR: Demander un texte à l'utilisateur.
    // ES: Solicitar texto del usuario.
    string text = get_string("Text: ");

    // RU: Подсчитываем количество букв, слов и предложений.
    // EN: Count the number of letters, words, and sentences.
    // FR: Compter le nombre de lettres, mots et phrases.
    // ES: Contar el número de letras, palabras y oraciones.
    int letters = count_letters(text);
    int words = count_words(text);
    int sentences = count_sentences(text);

    // RU: Вычисляем среднее количество букв и предложений на 100 слов.
    // EN: Calculate the average number of letters and sentences per 100 words.
    // FR: Calculer le nombre moyen de lettres et de phrases pour 100 mots.
    // ES: Calcular el número promedio de letras y oraciones por 100 palabras.
    float L = (float) letters / words * 100;
    float S = (float) sentences / words * 100;

    // RU: Вычисляем индекс Коулмана-Лиу.
    // EN: Calculate the Coleman-Liau index.
    // FR: Calculer l'indice de Coleman-Liau.
    // ES: Calcular el índice de Coleman-Liau.
    int index = round(0.0588 * L - 0.296 * S - 15.8);

    // RU: Определяем и выводим уровень знаний.
    // EN: Determine and print the grade level.
    // FR: Déterminer et afficher le niveau de lecture.
    // ES: Determinar e imprimir el nivel de lectura.
    if (index < 1)
    {
        printf("Before Grade 1\n");
    }
    else if (index >= 16)
    {
        printf("Grade 16+\n");
    }
    else
    {
        printf("Grade %i\n", index);
    }
}

// RU: Функция для подсчета количества букв в тексте.
// EN: Function to count the number of letters in the text.
// FR: Fonction pour compter le nombre de lettres dans le texte.
// ES: Función para contar el número de letras en el texto.
int count_letters(string text)
{
    int letters = 0;
    for (int i = 0, n = strlen(text); i < n; i++)
    {
        if (isalpha(text[i]))
        {
            letters++;
        }
    }
    return letters;
}

// RU: Функция для подсчета количества слов в тексте.
// EN: Function to count the number of words in the text.
// FR: Fonction pour compter le nombre de mots dans le texte.
// ES: Función para contar el número de palabras en el texto.
int count_words(string text)
{
    int words = 1; // RU: Начинаем с 1, так как первое слово не имеет пробела перед ним.
                   // EN: Start with 1, as the first word has no space before it.
                   // FR: Commencez par 1, car le premier mot n'a pas d'espace avant lui.
                   // ES: Comience con 1, ya que la primera palabra no tiene espacio antes de ella.
    for (int i = 0, n = strlen(text); i < n; i++)
    {
        if (text[i] == ' ')
        {
            words++;
        }
    }
    return words;
}

// RU: Функция для подсчета количества предложений в тексте.
// EN: Function to count the number of sentences in the text.
// FR: Fonction pour compter le nombre de phrases dans le texte.
// ES: Función para contar el número de oraciones en el texto.
int count_sentences(string text)
{
    int sentences = 0;
    for (int i = 0, n = strlen(text); i < n; i++)
    {
        if (text[i] == '.' || text[i] == '!' || text[i] == '?')
        {
            sentences++;
        }
    }
    return sentences;
}
