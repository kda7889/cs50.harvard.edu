// Программа на языке Си, которая проверяет правильность ввода номера кредитной карты по алгоритму Луна.
// RU: Этот код запрашивает номер кредитной карты и проверяет его на корректность.
// EN: This code requests a credit card number and checks it for validity.
// FR: Ce code demande un numéro de carte de crédit et vérifie sa validité.
// ES: Este código solicita un número de tarjeta de crédito y verifica su validez.

#include <stdio.h>
#include <cs50.h>
#include <math.h>

long get_card_number(void);
bool luhn_check(long card_number);
void check_card_type(long card_number);

int main(void) {
    // RU: Получаем номер кредитной карты от пользователя.
    // EN: Get the credit card number from the user.
    // FR: Obtenez le numéro de carte de crédit de l'utilisateur.
    // ES: Obtenga el número de tarjeta de crédito del usuario.
    long card_number = get_card_number();

    // RU: Проверяем номер карты по алгоритму Луна.
    // EN: Check the card number using the Luhn algorithm.
    // FR: Vérifiez le numéro de la carte en utilisant l'algorithme de Luhn.
    // ES: Verifique el número de tarjeta utilizando el algoritmo de Luhn.
    if (luhn_check(card_number)) {
        // RU: Проверяем тип карты (AMEX, MASTERCARD, VISA).
        // EN: Check the card type (AMEX, MASTERCARD, VISA).
        // FR: Vérifiez le type de carte (AMEX, MASTERCARD, VISA).
        // ES: Verifique el tipo de tarjeta (AMEX, MASTERCARD, VISA).
        check_card_type(card_number);
    } else {
        printf("INVALID\n");
    }

    return 0;
}

// RU: Функция для получения номера кредитной карты от пользователя.
// EN: Function to get the credit card number from the user.
long get_card_number(void) {
    long number;
    do {
        number = get_long("Number: ");
    } while (number < 0);
    return number;
}

// RU: Функция для проверки корректности номера по алгоритму Луна.
// EN: Function to check the validity of the card number using Luhn's algorithm.
bool luhn_check(long card_number) {
    int sum = 0;
    bool alternate = false;

    while (card_number > 0) {
        int digit = card_number % 10;

        if (alternate) {
            digit *= 2;
            if (digit > 9) {
                digit -= 9;
            }
        }

        sum += digit;
        alternate = !alternate;
        card_number /= 10;
    }

    return (sum % 10) == 0;
}

// RU: Функция для определения типа карты.
// EN: Function to determine the card type.
void check_card_type(long card_number) {
    // RU: Проверяем первые цифры и длину номера карты.
    // EN: Check the first digits and length of the card number.
    int length = 0;
    long temp = card_number;
    while (temp > 0) {
        temp /= 10;
        length++;
    }

    int start_digits = card_number / (long) pow(10, length - 2);

    if ((start_digits == 34 || start_digits == 37) && length == 15) {
        printf("AMEX\n");
    } else if (start_digits >= 51 && start_digits <= 55 && length == 16) {
        printf("MASTERCARD\n");
    } else if ((start_digits / 10 == 4) && (length == 13 || length == 16)) {
        printf("VISA\n");
    } else {
        printf("INVALID\n");
    }
}
