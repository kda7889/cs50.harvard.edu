// Simulate genetic inheritance of blood type

#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

// Each person has two parents and two alleles
// RU: Каждый человек имеет двух родителей и два аллеля
// EN: Each person has two parents and two alleles
// FR: Chaque personne a deux parents et deux allèles
// ES: Cada persona tiene dos padres y dos alelos
typedef struct person
{
    struct person *parents[2];
    char alleles[2];
} person;

const int GENERATIONS = 3;
const int INDENT_LENGTH = 4;

person *create_family(int generations);
void print_family(person *p, int generation);
void free_family(person *p);
char random_allele();

int main(void)
{
    // Seed random number generator
    // RU: Инициализация генератора случайных чисел
    // EN: Seed random number generator
    // FR: Initialiser le générateur de nombres aléatoires
    // ES: Inicializar el generador de números aleatorios
    srand(time(0));

    // Create a new family with three generations
    // RU: Создаем новую семью с тремя поколениями
    // EN: Create a new family with three generations
    // FR: Créer une nouvelle famille avec trois générations
    // ES: Crear una nueva familia con tres generaciones
    person *p = create_family(GENERATIONS);

    // Print family tree of blood types
    // RU: Печатаем генеалогическое древо с типами крови
    // EN: Print family tree of blood types
    // FR: Imprimer l'arbre généalogique des groupes sanguins
    // ES: Imprimir el árbol genealógico con los tipos de sangre
    print_family(p, 0);

    // Free memory
    // RU: Освобождаем память
    // EN: Free memory
    // FR: Libérer la mémoire
    // ES: Liberar la memoria
    free_family(p);

    return 0;
}

// Create a new individual with `generations`
// RU: Создаем нового человека с количеством поколений `generations`
// EN: Create a new individual with `generations`
// FR: Créer un nouvel individu avec `générations`
// ES: Crear un nuevo individuo con `generaciones`
person *create_family(int generations)
{
    // Allocate memory for new person
    // RU: Выделяем память для нового человека
    // EN: Allocate memory for new person
    // FR: Allouer de la mémoire pour la nouvelle personne
    // ES: Asignar memoria para la nueva persona
    person *new_person = malloc(sizeof(person));
    if (new_person == NULL)
    {
        printf("Memory allocation failed\n");
        exit(1);
    }

    // If there are generations left to create
    if (generations > 1)
    {
        // Create two new parents for current person by recursively calling create_family
        // RU: Создаем двух новых родителей для текущего человека с помощью рекурсивного вызова create_family
        // EN: Create two new parents for current person by recursively calling create_family
        // FR: Créer deux nouveaux parents pour la personne actuelle en appelant récursivement create_family
        // ES: Crear dos nuevos padres para la persona actual llamando recursivamente a create_family
        new_person->parents[0] = create_family(generations - 1);
        new_person->parents[1] = create_family(generations - 1);

        // Randomly assign current person's alleles based on the alleles of their parents
        // RU: Случайным образом назначаем аллели текущего человека на основе аллелей его родителей
        // EN: Randomly assign current person's alleles based on the alleles of their parents
        // FR: Attribuer aléatoirement les allèles de la personne actuelle en fonction des allèles de ses parents
        // ES: Asignar aleatoriamente los alelos de la persona actual según los alelos de sus padres
        new_person->alleles[0] = new_person->parents[0]->alleles[rand() % 2];
        new_person->alleles[1] = new_person->parents[1]->alleles[rand() % 2];
    }
    else
    {
        // Set parent pointers to NULL
        // RU: Устанавливаем указатели родителей в NULL
        // EN: Set parent pointers to NULL
        // FR: Définir les pointeurs des parents sur NULL
        // ES: Establecer los punteros de los padres a NULL
        new_person->parents[0] = NULL;
        new_person->parents[1] = NULL;

        // Randomly assign alleles
        // RU: Случайным образом назначаем аллели
        // EN: Randomly assign alleles
        // FR: Attribuer aléatoirement les allèles
        // ES: Asignar alelos aleatoriamente
        new_person->alleles[0] = random_allele();
        new_person->alleles[1] = random_allele();
    }

    // Return newly created person
    // RU: Возвращаем нового человека
    // EN: Return newly created person
    // FR: Retourner la nouvelle personne créée
    // ES: Devolver la nueva persona creada
    return new_person;
}

// Free `p` and all ancestors of `p`
// RU: Освободить память для `p` и всех его предков
// EN: Free `p` and all ancestors of `p`
// FR: Libérer `p` et tous ses ancêtres
// ES: Liberar `p` y todos sus ancestros
void free_family(person *p)
{
    // Handle base case
    // RU: Обработка базового случая
    // EN: Handle base case
    // FR: Gérer le cas de base
    // ES: Manejar el caso base
    if (p == NULL)
    {
        return;
    }

    // Free parents recursively
    // RU: Рекурсивно освобождаем память для родителей
    // EN: Free parents recursively
    // FR: Libérer les parents récursivement
    // ES: Liberar a los padres recursivamente
    free_family(p->parents[0]);
    free_family(p->parents[1]);

    // Free child
    // RU: Освобождаем память для ребенка
    // EN: Free child
    // FR: Libérer l'enfant
    // ES: Liberar al hijo
    free(p);
}

// Randomly choose a blood type allele
// RU: Случайным образом выбираем аллель группы крови
// EN: Randomly choose a blood type allele
// FR: Choisir aléatoirement un allèle de groupe sanguin
// ES: Elegir aleatoriamente un alelo del tipo de sangre
char random_allele()
{
    int r = rand() % 3;
    if (r == 0)
    {
        return 'A';
    }
    else if (r == 1)
    {
        return 'B';
    }
    else
    {
        return 'O';
    }
}

// Print each family member and their blood type
// RU: Печатает каждого члена семьи и его группу крови
// EN: Print each family member and their blood type
// FR: Imprimer chaque membre de la famille et son groupe sanguin
// ES: Imprimir cada miembro de la familia y su tipo de sangre
void print_family(person *p, int generation)
{
    // Handle base case
    if (p == NULL)
    {
        return;
    }

    // Print indentation
    for (int i = 0; i < generation * INDENT_LENGTH; i++)
    {
        printf(" ");
    }

    // Print person
    printf("Generation %i, blood type %c%c\n", generation, p->alleles[0], p->alleles[1]);

    // Print parents recursively
    print_family(p->parents[0], generation + 1);
    print_family(p->parents[1], generation + 1);
}
