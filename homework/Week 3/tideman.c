// Программа на языке Си, которая реализует выборы по методу Тидемана.
// RU: Эта программа позволяет пользователям голосовать за кандидатов, а затем определяет победителя, используя метод сортировки Тидемана.
// EN: This program implements the Tideman voting system, allowing users to vote for candidates and then determining the winner using the Tideman sorting method.
// FR: Ce programme implémente le système de vote Tideman, permettant aux utilisateurs de voter pour des candidats, puis de déterminer le gagnant en utilisant la méthode de tri Tideman.
// ES: Este programa implementa el sistema de votación Tideman, permitiendo a los usuarios votar por candidatos y luego determinando al ganador usando el método de clasificación de Tideman.

#include <cs50.h>
#include <stdio.h>
#include <string.h>

// Max number of candidates
#define MAX 9

// RU: preferences[i][j] - количество избирателей, которые предпочитают кандидата i кандидату j.
// EN: preferences[i][j] - number of voters who prefer candidate i over candidate j.
int preferences[MAX][MAX];

// RU: locked[i][j] означает, что кандидат i победил кандидата j и связь зафиксирована.
// EN: locked[i][j] means candidate i is locked in over candidate j.
bool locked[MAX][MAX];

// RU: Каждая пара имеет победителя и проигравшего.
// EN: Each pair has a winner and a loser.
typedef struct
{
    int winner;
    int loser;
} pair;

// Array of candidates
string candidates[MAX];
pair pairs[MAX * (MAX - 1) / 2];

int pair_count;
int candidate_count;

// Function prototypes
bool vote(int rank, string name, int ranks[]);
void record_preferences(int ranks[]);
void add_pairs(void);
void sort_pairs(void);
void lock_pairs(void);
void print_winner(void);
bool cycle(int winner, int loser);

int main(int argc, string argv[])
{
    // RU: Проверка на правильное использование программы.
    // EN: Check for invalid usage of the program.
    if (argc < 2)
    {
        printf("Usage: tideman [candidate ...]\n");
        return 1;
    }

    // RU: Заполняем массив кандидатов.
    // EN: Populate the array of candidates.
    candidate_count = argc - 1;
    if (candidate_count > MAX)
    {
        printf("Maximum number of candidates is %i\n", MAX);
        return 2;
    }
    for (int i = 0; i < candidate_count; i++)
    {
        candidates[i] = argv[i + 1];
    }

    // RU: Очищаем граф заблокированных пар.
    // EN: Clear the graph of locked pairs.
    for (int i = 0; i < candidate_count; i++)
    {
        for (int j = 0; j < candidate_count; j++)
        {
            locked[i][j] = false;
        }
    }

    pair_count = 0;
    int voter_count = get_int("Number of voters: ");

    // RU: Запрашиваем голоса избирателей.
    // EN: Query votes from voters.
    for (int i = 0; i < voter_count; i++)
    {
        // ranks[i] is voter's ith preference
        int ranks[candidate_count];

        // RU: Запрашиваем каждый ранг.
        // EN: Query for each rank.
        for (int j = 0; j < candidate_count; j++)
        {
            string name = get_string("Rank %i: ", j + 1);

            if (!vote(j, name, ranks))
            {
                printf("Invalid vote.\n");
                return 3;
            }
        }

        record_preferences(ranks);
        printf("\n");
    }

    add_pairs();
    sort_pairs();
    lock_pairs();
    print_winner();
    return 0;
}

// RU: Обновление рангов на основе нового голоса.
// EN: Update ranks given a new vote.
bool vote(int rank, string name, int ranks[])
{
    for (int i = 0; i < candidate_count; i++)
    {
        if (strcmp(candidates[i], name) == 0)
        {
            ranks[rank] = i;
            return true;
        }
    }
    return false;
}

// RU: Обновление предпочтений на основе рангов избирателей.
// EN: Update preferences given one voter's ranks.
void record_preferences(int ranks[])
{
    for (int i = 0; i < candidate_count; i++)
    {
        for (int j = i + 1; j < candidate_count; j++)
        {
            preferences[ranks[i]][ranks[j]]++;
        }
    }
}

// RU: Запись пар кандидатов, где один предпочтительнее другого.
// EN: Record pairs of candidates where one is preferred over the other.
void add_pairs(void)
{
    for (int i = 0; i < candidate_count; i++)
    {
        for (int j = 0; j < candidate_count; j++)
        {
            if (preferences[i][j] > preferences[j][i])
            {
                pairs[pair_count].winner = i;
                pairs[pair_count].loser = j;
                pair_count++;
            }
        }
    }
}

// RU: Сортировка пар в порядке убывания силы победы.
// EN: Sort pairs in decreasing order by strength of victory.
void sort_pairs(void)
{
    for (int i = 0; i < pair_count - 1; i++)
    {
        for (int j = i + 1; j < pair_count; j++)
        {
            int strength_i = preferences[pairs[i].winner][pairs[i].loser] - preferences[pairs[i].loser][pairs[i].winner];
            int strength_j = preferences[pairs[j].winner][pairs[j].loser] - preferences[pairs[j].loser][pairs[j].winner];
            if (strength_j > strength_i)
            {
                pair temp = pairs[i];
                pairs[i] = pairs[j];
                pairs[j] = temp;
            }
        }
    }
}

// RU: Закрепление пар в графе, не создавая циклов.
// EN: Lock pairs into the candidate graph in order, without creating cycles.
void lock_pairs(void)
{
    for (int i = 0; i < pair_count; i++)
    {
        if (!cycle(pairs[i].winner, pairs[i].loser))
        {
            locked[pairs[i].winner][pairs[i].loser] = true;
        }
    }
}

// RU: Функция для проверки, создаст ли закрепление пары цикл.
// EN: Function to check if locking a pair will create a cycle.
bool cycle(int winner, int loser)
{
    if (loser == winner)
    {
        return true;
    }
    for (int i = 0; i < candidate_count; i++)
    {
        if (locked[loser][i])
        {
            if (cycle(winner, i))
            {
                return true;
            }
        }
    }
    return false;
}

// RU: Печать победителя выборов.
// EN: Print the winner of the election.
void print_winner(void)
{
    for (int i = 0; i < candidate_count; i++)
    {
        bool is_source = true;
        for (int j = 0; j < candidate_count; j++)
        {
            if (locked[j][i])
            {
                is_source = false;
                break;
            }
        }
        if (is_source)
        {
            printf("%s\n", candidates[i]);
            return;
        }
    }
}
