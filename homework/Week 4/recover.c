#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

// Define a byte type
// RU: Определяем тип данных для байта
// EN: Define a byte type
// FR: Définir un type d'octet
// ES: Definir un tipo de byte
typedef uint8_t BYTE;

// Block size for FAT file system
// RU: Размер блока для файловой системы FAT
// EN: Block size for FAT file system
// FR: Taille de bloc pour le système de fichiers FAT
// ES: Tamaño de bloque para el sistema de archivos FAT
#define BLOCK_SIZE 512

int main(int argc, char *argv[])
{
    // Check for correct usage
    // RU: Проверка правильного использования программы
    // EN: Check for correct usage
    // FR: Vérifier la bonne utilisation
    // ES: Verificar el uso correcto
    if (argc != 2)
    {
        printf("Usage: ./recover image\n");
        return 1;
    }

    // Open the forensic image
    // RU: Открытие криминалистического образа карты памяти
    // EN: Open the forensic image
    // FR: Ouvrir l'image médico-légale
    // ES: Abrir la imagen forense
    FILE *input = fopen(argv[1], "r");
    if (input == NULL)
    {
        printf("Could not open file.");
        return 1;
    }

    BYTE buffer[BLOCK_SIZE];
    FILE *output = NULL;
    int file_count = 0;
    char filename[8];

    // Read the blocks until end of the file
    // RU: Чтение блоков до конца файла
    // EN: Read the blocks until end of the file
    // FR: Lire les blocs jusqu'à la fin du fichier
    // ES: Leer los bloques hasta el final del archivo
    while (fread(buffer, sizeof(BYTE), BLOCK_SIZE, input) == BLOCK_SIZE)
    {
        // Check if the block indicates the start of a new JPEG
        // RU: Проверка, указывает ли блок на начало нового JPEG
        // EN: Check if the block indicates the start of a new JPEG
        // FR: Vérifier si le bloc indique le début d'un nouveau JPEG
        // ES: Verificar si el bloque indica el inicio de un nuevo JPEG
        if (buffer[0] == 0xff && buffer[1] == 0xd8 && buffer[2] == 0xff && (buffer[3] & 0xf0) == 0xe0)
        {
            // If already writing a JPEG, close it
            // RU: Если уже идет запись JPEG, закрыть его
            // EN: If already writing a JPEG, close it
            // FR: Si un JPEG est déjà en cours d'écriture, le fermer
            // ES: Si ya se está escribiendo un JPEG, cerrarlo
            if (output != NULL)
            {
                fclose(output);
            }

            // Create a new filename and open a new file for writing
            // RU: Создать новое имя файла и открыть новый файл для записи
            // EN: Create a new filename and open a new file for writing
            // FR: Créer un nouveau nom de fichier et ouvrir un nouveau fichier pour l'écriture
            // ES: Crear un nuevo nombre de archivo y abrir un nuevo archivo para escribir
            sprintf(filename, "%03i.jpg", file_count);
            output = fopen(filename, "w");
            if (output == NULL)
            {
                printf("Could not create output JPEG file.");
                fclose(input);
                return 1;
            }
            file_count++;
        }

        // If currently writing to a JPEG file, write the buffer to it
        // RU: Если в данный момент идет запись JPEG, записать буфер в файл
        // EN: If currently writing to a JPEG file, write the buffer to it
        // FR: Si un fichier JPEG est en cours d'écriture, écrire le tampon dedans
        // ES: Si actualmente se está escribiendo en un archivo JPEG, escribir el búfer en él
        if (output != NULL)
        {
            fwrite(buffer, sizeof(BYTE), BLOCK_SIZE, output);
        }
    }

    // Close any remaining open files
    // RU: Закрыть все оставшиеся открытые файлы
    // EN: Close any remaining open files
    // FR: Fermer tous les fichiers encore ouverts
    // ES: Cerrar cualquier archivo que quede abierto
    if (output != NULL)
    {
        fclose(output);
    }
    fclose(input);

    return 0;
}
