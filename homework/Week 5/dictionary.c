#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <strings.h>
#include <ctype.h>
#include "dictionary.h"

// Represents number of buckets in a hash table
// RU: Представляет количество корзин в хэш-таблице
// EN: Represents number of buckets in a hash table
// FR: Représente le nombre de compartiments dans une table de hachage
// ES: Representa el número de compartimientos en una tabla hash
#define N 1000

// Represents a node in a hash table
// RU: Представляет узел в хэш-таблице
// EN: Represents a node in a hash table
// FR: Représente un nœud dans une table de hachage
// ES: Representa un nodo en una tabla hash
typedef struct node
{
    char word[LENGTH + 1];
    struct node *next;
}
node;

// Hash table
// RU: Хэш-таблица
// EN: Hash table
// FR: Table de hachage
// ES: Tabla hash
node *table[N];

// Returns true if word is in dictionary else false
// RU: Возвращает true, если слово есть в словаре, иначе false
// EN: Returns true if word is in dictionary else false
// FR: Renvoie true si le mot est dans le dictionnaire, sinon false
// ES: Devuelve true si la palabra está en el diccionario, de lo contrario false
bool check(const char *word)
{
    // Hash word to obtain a hash value
    // RU: Хэшируем слово, чтобы получить его хэш-значение
    // EN: Hash word to obtain a hash value
    // FR: Hacher le mot pour obtenir une valeur de hachage
    // ES: Hashear la palabra para obtener un valor hash
    unsigned int index = hash(word);

    // Access linked list at that index in the hash table
    // RU: Получаем доступ к связанному списку по этому индексу в хэш-таблице
    // EN: Access linked list at that index in the hash table
    // FR: Accéder à la liste chaînée à cet index dans la table de hachage
    // ES: Acceder a la lista enlazada en ese índice en la tabla hash
    node *cursor = table[index];

    // Traverse linked list, looking for the word (case-insensitive)
    // RU: Проходим по связанному списку в поисках слова (без учета регистра)
    // EN: Traverse linked list, looking for the word (case-insensitive)
    // FR: Parcourir la liste chaînée à la recherche du mot (insensible à la casse)
    // ES: Recorrer la lista enlazada buscando la palabra (sin distinguir mayúsculas y minúsculas)
    while (cursor != NULL)
    {
        if (strcasecmp(cursor->word, word) == 0)
        {
            return true;
        }
        cursor = cursor->next;
    }
    return false;
}

// Hashes word to a number
// RU: Хэширует слово в число
// EN: Hashes word to a number
// FR: Hache le mot en un nombre
// ES: Hashea la palabra a un número
unsigned int hash(const char *word)
{
    // Simple hash function using djb2 by Dan Bernstein
    // RU: Простая хэш-функция, использующая djb2 Дэна Бернштейна
    // EN: Simple hash function using djb2 by Dan Bernstein
    // FR: Fonction de hachage simple utilisant djb2 par Dan Bernstein
    // ES: Función hash simple utilizando djb2 por Dan Bernstein
    unsigned long hash = 5381;
    int c;
    while ((c = tolower(*word++)))
    {
        hash = ((hash << 5) + hash) + c;  // hash * 33 + c
    }
    return hash % N;
}

// Loads dictionary into memory, returning true if successful else false
// RU: Загружает словарь в память, возвращает true в случае успеха, иначе false
// EN: Loads dictionary into memory, returning true if successful else false
// FR: Charge le dictionnaire en mémoire, renvoie true si réussi, sinon false
// ES: Carga el diccionario en la memoria, devuelve true si tiene éxito, de lo contrario false
bool load(const char *dictionary)
{
    // Open dictionary file
    // RU: Открываем файл словаря
    // EN: Open dictionary file
    // FR: Ouvrir le fichier du dictionnaire
    // ES: Abrir el archivo del diccionario
    FILE *file = fopen(dictionary, "r");
    if (file == NULL)
    {
        return false;
    }

    // Buffer for a word
    // RU: Буфер для слова
    // EN: Buffer for a word
    // FR: Tampon pour un mot
    // ES: Búfer para una palabra
    char word[LENGTH + 1];

    // Insert words into hash table
    // RU: Вставляем слова в хэш-таблицу
    // EN: Insert words into hash table
    // FR: Insérer les mots dans la table de hachage
    // ES: Insertar palabras en la tabla hash
    while (fscanf(file, "%s", word) != EOF)
    {
        // Create a new node for each word
        // RU: Создаем новый узел для каждого слова
        // EN: Create a new node for each word
        // FR: Créer un nouveau nœud pour chaque mot
        // ES: Crear un nuevo nodo para cada palabra
        node *new_node = malloc(sizeof(node));
        if (new_node == NULL)
        {
            return false;
        }
        strcpy(new_node->word, word);
        new_node->next = NULL;

        // Hash word to obtain a hash value
        // RU: Хэшируем слово, чтобы получить его хэш-значение
        // EN: Hash word to obtain a hash value
        // FR: Hacher le mot pour obtenir une valeur de hachage
        // ES: Hashear la palabra para obtener un valor hash
        unsigned int index = hash(word);

        // Insert node into hash table at that location
        // RU: Вставляем узел в хэш-таблицу по этому индексу
        // EN: Insert node into hash table at that location
        // FR: Insérer le nœud dans la table de hachage à cet emplacement
        // ES: Insertar el nodo en la tabla hash en esa ubicación
        new_node->next = table[index];
        table[index] = new_node;
    }

    // Close dictionary file
    // RU: Закрываем файл словаря
    // EN: Close dictionary file
    // FR: Fermer le fichier du dictionnaire
    // ES: Cerrar el archivo del diccionario
    fclose(file);
    return true;
}

// Returns number of words in dictionary if loaded else 0 if not yet loaded
// RU: Возвращает количество слов в словаре, если он загружен, иначе 0, если не загружен
// EN: Returns number of words in dictionary if loaded else 0 if not yet loaded
// FR: Renvoie le nombre de mots dans le dictionnaire si chargé, sinon 0 s'il n'est pas encore chargé
// ES: Devuelve el número de palabras en el diccionario si está cargado, de lo contrario 0 si aún no se ha cargado
unsigned int size(void)
{
    unsigned int count = 0;
    for (int i = 0; i < N; i++)
    {
        node *cursor = table[i];
        while (cursor != NULL)
        {
            count++;
            cursor = cursor->next;
        }
    }
    return count;
}

// Unloads dictionary from memory, returning true if successful else false
// RU: Освобождает словарь из памяти, возвращает true в случае успеха, иначе false
// EN: Unloads dictionary from memory, returning true if successful else false
// FR: Décharge le dictionnaire de la mémoire, renvoie true si réussi, sinon false
// ES: Descarga el diccionario de la memoria, devuelve true si tiene éxito, de lo contrario false
bool unload(void)
{
    // Iterate over each bucket in the hash table
    // RU: Перебираем каждую корзину в хэш-таблице
    // EN: Iterate over each bucket in the hash table
    // FR: Itérer sur chaque compartiment dans la table de hachage
    // ES: Iterar sobre cada compartimiento en la tabla hash
    for (int i = 0; i < N; i++)
    {
        node *cursor = table[i];
        while (cursor != NULL)
        {
            node *tmp = cursor;
            cursor = cursor->next;
            free(tmp);
        }
    }
    return true;
}
