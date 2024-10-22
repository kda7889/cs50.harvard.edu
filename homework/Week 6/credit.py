# Программа на языке Python, которая проверяет правильность ввода номера кредитной карты по алгоритму Луна.
# RU: Этот код запрашивает номер кредитной карты и проверяет его на корректность.
# EN: This code requests a credit card number and checks it for validity.
# FR: Ce code demande un numéro de carte de crédit et vérifie sa validité.
# ES: Este código solicita un número de tarjeta de crédito y verifica su validez.

def get_card_number():
    """
    RU: Функция для получения номера кредитной карты от пользователя.
    EN: Function to get the credit card number from the user.
    FR: Fonction pour obtenir le numéro de carte de crédit de l'utilisateur.
    ES: Función para obtener el número de tarjeta de crédito del usuario.
    """
    while True:
        try:
            number = int(input("Number: "))
            if number > 0:
                return number
        except ValueError:
            pass

def luhn_check(card_number):
    """
    RU: Функция для проверки корректности номера по алгоритму Луна.
    EN: Function to check the validity of the card number using Luhn's algorithm.
    FR: Fonction pour vérifier la validité du numéro de carte en utilisant l'algorithme de Luhn.
    ES: Función para verificar la validez del número de tarjeta utilizando el algoritmo de Luhn.
    """
    sum = 0
    alternate = False

    while card_number > 0:
        digit = card_number % 10

        if alternate:
            digit *= 2
            if digit > 9:
                digit -= 9

        sum += digit
        alternate = not alternate
        card_number //= 10

    return (sum % 10) == 0

def check_card_type(card_number):
    """
    RU: Функция для определения типа карты.
    EN: Function to determine the card type.
    FR: Fonction pour déterminer le type de carte.
    ES: Función para determinar el tipo de tarjeta.
    """
    # RU: Проверяем первые цифры и длину номера карты.
    # EN: Check the first digits and length of the card number.
    # FR: Vérifiez les premiers chiffres et la longueur du numéro de la carte.
    # ES: Verifique los primeros dígitos y la longitud del número de la tarjeta.
    length = len(str(card_number))
    start_digits = int(str(card_number)[:2])

    if (start_digits == 34 or start_digits == 37) and length == 15:
        print("AMEX")
    elif 51 <= start_digits <= 55 and length == 16:
        print("MASTERCARD")
    elif str(card_number).startswith('4') and (length == 13 or length == 16):
        print("VISA")
    else:
        print("INVALID")

if __name__ == "__main__":
    # RU: Получаем номер кредитной карты от пользователя.
    # EN: Get the credit card number from the user.
    # FR: Obtenez le numéro de carte de crédit de l'utilisateur.
    # ES: Obtenga el número de tarjeta de crédito del usuario.
    card_number = get_card_number()

    # RU: Проверяем номер карты по алгоритму Луна.
    # EN: Check the card number using the Luhn algorithm.
    # FR: Vérifiez le numéro de la carte en utilisant l'algorithme de Luhn.
    # ES: Verifique el número de tarjeta utilizando el algoritmo de Luhn.
    if luhn_check(card_number):
        # RU: Проверяем тип карты (AMEX, MASTERCARD, VISA).
        # EN: Check the card type (AMEX, MASTERCARD, VISA).
        # FR: Vérifiez le type de carte (AMEX, MASTERCARD, VISA).
        # ES: Verifique el tipo de tarjeta (AMEX, MASTERCARD, VISA).
        check_card_type(card_number)
    else:
        print("INVALID")
