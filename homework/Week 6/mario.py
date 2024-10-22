# Программа на языке Python, которая строит пирамиду заданной высоты с использованием хэшей (#).
# RU: Этот код позволяет пользователю ввести высоту пирамиды и строит её.
# EN: This code allows the user to enter the height of the pyramid and builds it.
# FR: Ce code permet à l'utilisateur de saisir la hauteur de la pyramide et la construit.
# ES: Este código permite al usuario ingresar la altura de la pirámide y la construye.

# Запрашиваем высоту пирамиды от пользователя (от 1 до 8).
# RU: Asking the user for the height of the pyramid (from 1 to 8).
# FR: Demande à l'utilisateur la hauteur de la pyramide (de 1 à 8).
# ES: Solicitar al usuario la altura de la pirámide (de 1 a 8).
while True:
    try:
        height = int(input("Height: "))
        if 1 <= height <= 8:
            break
    except ValueError:
        pass

# Строим пирамиду указанной высоты.
# RU: Building a pyramid of the specified height.
# FR: Construire une pyramide de la hauteur spécifiée.
# ES: Construir una pirámide de la altura especificada.
for i in range(1, height + 1):
    # Печатаем пробелы слева.
    # RU: Printing spaces on the left.
    # FR: Impression des espaces à gauche.
    # ES: Imprimir espacios a la izquierda.
    print(" " * (height - i), end="")

    # Печатаем хэши слева.
    # RU: Printing hashes on the left.
    # FR: Impression des hachures à gauche.
    # ES: Imprimir almohadillas a la izquierda.
    print("#" * i, end="")

    # Печатаем промежуток между двумя частями пирамиды.
    # RU: Printing the gap between the two parts of the pyramid.
    # FR: Impression de l'espace entre les deux parties de la pyramide.
    # ES: Imprimir el espacio entre las dos partes de la pirámide.
    print("  ", end="")

    # Печатаем хэши справа.
    # RU: Printing hashes on the right.
    # FR: Impression des hachures à droite.
    # ES: Imprimir almohadillas a la derecha.
    print("#" * i)
