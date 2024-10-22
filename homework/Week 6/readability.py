# Программа на языке Python, которая вычисляет уровень знаний, необходимый для понимания текста по индексу Коулмана-Лиу.
# RU: Эта программа принимает текст и вычисляет его уровень читаемости.
# EN: This program takes a text and computes its readability level.
# FR: Ce programme prend un texte et calcule son niveau de lisibilité.
# ES: Este programa toma un texto y calcula su nivel de legibilidad.

def count_letters(text):
    """
    RU: Функция для подсчета количества букв в тексте.
    EN: Function to count the number of letters in the text.
    FR: Fonction pour compter le nombre de lettres dans le texte.
    ES: Función para contar el número de letras en el texto.
    """
    letters = sum(1 for char in text if char.isalpha())
    return letters

def count_words(text):
    """
    RU: Функция для подсчета количества слов в тексте.
    EN: Function to count the number of words in the text.
    FR: Fonction pour compter le nombre de mots dans le texte.
    ES: Función para contar el número de palabras en el texto.
    """
    words = len(text.split())
    return words

def count_sentences(text):
    """
    RU: Функция для подсчета количества предложений в тексте.
    EN: Function to count the number of sentences in the text.
    FR: Fonction pour compter le nombre de phrases dans le texte.
    ES: Función para contar el número de oraciones en el texto.
    """
    sentences = sum(1 for char in text if char in '.!?')
    return sentences

def main():
    """
    RU: Основная функция программы.
    EN: Main function of the program.
    FR: Fonction principale du programme.
    ES: Función principal del programa.
    """
    # RU: Запрашиваем текст у пользователя.
    # EN: Request text from the user.
    # FR: Demander un texte à l'utilisateur.
    # ES: Solicitar texto del usuario.
    text = input("Text: ")

    # RU: Подсчитываем количество букв, слов и предложений.
    # EN: Count the number of letters, words, and sentences.
    # FR: Compter le nombre de lettres, mots et phrases.
    # ES: Contar el número de letras, palabras y oraciones.
    letters = count_letters(text)
    words = count_words(text)
    sentences = count_sentences(text)

    # RU: Вычисляем среднее количество букв и предложений на 100 слов.
    # EN: Calculate the average number of letters and sentences per 100 words.
    # FR: Calculer le nombre moyen de lettres et de phrases pour 100 mots.
    # ES: Calcular el número promedio de letras y oraciones por 100 palabras.
    L = (letters / words) * 100
    S = (sentences / words) * 100

    # RU: Вычисляем индекс Коулмана-Лиу.
    # EN: Calculate the Coleman-Liau index.
    # FR: Calculer l'indice de Coleman-Liau.
    # ES: Calcular el índice de Coleman-Liau.
    index = round(0.0588 * L - 0.296 * S - 15.8)

    # RU: Определяем и выводим уровень знаний.
    # EN: Determine and print the grade level.
    # FR: Déterminer et afficher le niveau de lecture.
    # ES: Determinar e imprimir el nivel de lectura.
    if index < 1:
        print("Before Grade 1")
    elif index >= 16:
        print("Grade 16+")
    else:
        print(f"Grade {index}")

if __name__ == "__main__":
    main()
