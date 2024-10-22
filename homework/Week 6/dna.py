import csv
import sys

# RU: Основная функция программы
# FR: Fonction principale du programme
# ES: Función principal del programa
# EN: Main function of the program
def main():
    # RU: Проверка на корректное количество аргументов командной строки
    # FR: Vérifier le nombre correct d'arguments de ligne de commande
    # ES: Verificar el número correcto de argumentos de línea de comandos
    # EN: Check for correct command-line arguments
    if len(sys.argv) != 3:
        print("Usage: python dna.py <database.csv> <sequence.txt>")
        sys.exit(1)

    # RU: Чтение файла базы данных STR в переменную
    # FR: Lecture du fichier de base de données STR dans une variable
    # ES: Leer el archivo de la base de datos STR en una variable
    # EN: Read the STR database file into a variable
    csv_filename = sys.argv[1]
    with open(csv_filename, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        str_data = [row for row in reader]
        str_names = reader.fieldnames[1:]

    # RU: Чтение файла последовательности ДНК в переменную
    # FR: Lecture du fichier de séquence ADN dans une variable
    # ES: Leer el archivo de secuencia de ADN en una variable
    # EN: Read the DNA sequence file into a variable
    dna_filename = sys.argv[2]
    with open(dna_filename, 'r') as dna_file:
        dna_sequence = dna_file.read()

    # RU: Нахождение самой длинной последовательности каждого STR в ДНК
    # FR: Trouver la plus longue séquence de chaque STR dans l'ADN
    # ES: Encontrar la secuencia más larga de cada STR en el ADN
    # EN: Find the longest match of each STR in the DNA sequence
    str_counts = {}
    for str_name in str_names:
        str_counts[str_name] = longest_match(dna_sequence, str_name)

    # RU: Проверка базы данных на наличие совпадающих профилей
    # FR: Vérifier la base de données pour les profils correspondants
    # ES: Verificar la base de datos para perfiles coincidentes
    # EN: Check the database for matching profiles
    for person in str_data:
        match = True
        for str_name in str_names:
            if int(person[str_name]) != str_counts[str_name]:
                match = False
                break

        if match:
            print(person['name'])
            return

    print("No match")

# RU: Вспомогательная функция для поиска самой длинной последовательности повторов
# FR: Fonction auxiliaire pour trouver la séquence répétée la plus longue
# ES: Función auxiliar para encontrar la secuencia repetitiva más larga
# EN: Helper function to find the longest sequence of repeats
def longest_match(sequence, subsequence):
    """
    RU: Возвращает максимальное количество повторений subsequence в sequence.
    FR: Renvoie le nombre maximal de répétitions de subsequence dans sequence.
    ES: Devuelve la cantidad máxima de repeticiones de subsequence en sequence.
    EN: Returns the maximum number of repeats of the subsequence in the sequence.
    """
    longest_run = 0
    subsequence_length = len(subsequence)
    sequence_length = len(sequence)

    for i in range(sequence_length):
        count = 0

        while True:
            start = i + count * subsequence_length
            end = start + subsequence_length

            if sequence[start:end] == subsequence:
                count += 1
            else:
                break

        longest_run = max(longest_run, count)

    return longest_run

# RU: Запуск основной функции
# FR: Exécuter la fonction principale
# ES: Ejecutar la función principal
# EN: Run the main function
if __name__ == "__main__":
    main()
