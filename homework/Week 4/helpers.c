#include "helpers.h"
#include <math.h>

// Convert image to grayscale
// RU: Преобразование изображения в оттенки серого
// EN: Convert image to grayscale
// FR: Convertir l'image en niveaux de gris
// ES: Convertir la imagen a escala de grises
void grayscale(int height, int width, RGBTRIPLE image[height][width])
{
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            // Calculate the average value of RGB
            // RU: Рассчитать среднее значение для RGB
            // EN: Calculate the average value of RGB
            // FR: Calculer la valeur moyenne des canaux RGB
            // ES: Calcular el valor promedio de los canales RGB
            int average = round((image[i][j].rgbtRed + image[i][j].rgbtGreen + image[i][j].rgbtBlue) / 3.0);

            // Set each color channel to the average value
            // RU: Установить каждое значение цвета равным среднему
            // EN: Set each color channel to the average value
            // FR: Définir chaque canal de couleur à la valeur moyenne
            // ES: Establecer cada canal de color al valor promedio
            image[i][j].rgbtRed = average;
            image[i][j].rgbtGreen = average;
            image[i][j].rgbtBlue = average;
        }
    }
}

// Reflect image horizontally
// RU: Отразить изображение по горизонтали
// EN: Reflect image horizontally
// FR: Refléter l'image horizontalement
// ES: Reflejar la imagen horizontalmente
void reflect(int height, int width, RGBTRIPLE image[height][width])
{
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width / 2; j++)
        {
            // Swap pixels horizontally
            // RU: Поменять местами пиксели по горизонтали
            // EN: Swap pixels horizontally
            // FR: Échanger les pixels horizontalement
            // ES: Intercambiar los píxeles horizontalmente
            RGBTRIPLE temp = image[i][j];
            image[i][j] = image[i][width - j - 1];
            image[i][width - j - 1] = temp;
        }
    }
}

// Blur image
// RU: Размытие изображения
// EN: Blur image
// FR: Flouter l'image
// ES: Desenfocar la imagen
void blur(int height, int width, RGBTRIPLE image[height][width])
{
    RGBTRIPLE temp[height][width];

    // Copy image to temp
    // RU: Копировать изображение во временный массив
    // EN: Copy image to temp
    // FR: Copier l'image dans un tableau temporaire
    // ES: Copiar la imagen a un arreglo temporal
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            temp[i][j] = image[i][j];
        }
    }

    // Iterate over each pixel to calculate the blur
    // RU: Перебрать каждый пиксель для расчета размытия
    // EN: Iterate over each pixel to calculate the blur
    // FR: Itérer sur chaque pixel pour calculer le flou
    // ES: Iterar sobre cada píxel para calcular el desenfoque
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            int redSum = 0, greenSum = 0, blueSum = 0;
            int count = 0;

            // Iterate over the neighboring pixels
            // RU: Перебрать соседние пиксели
            // EN: Iterate over the neighboring pixels
            // FR: Itérer sur les pixels voisins
            // ES: Iterar sobre los píxeles vecinos
            for (int di = -1; di <= 1; di++)
            {
                for (int dj = -1; dj <= 1; dj++)
                {
                    int ni = i + di;
                    int nj = j + dj;

                    // Check if neighbor is within bounds
                    // RU: Проверить, находится ли соседний пиксель в пределах изображения
                    // EN: Check if neighbor is within bounds
                    // FR: Vérifier si le voisin est dans les limites de l'image
                    // ES: Verificar si el píxel vecino está dentro de los límites
                    if (ni >= 0 && ni < height && nj >= 0 && nj < width)
                    {
                        redSum += temp[ni][nj].rgbtRed;
                        greenSum += temp[ni][nj].rgbtGreen;
                        blueSum += temp[ni][nj].rgbtBlue;
                        count++;
                    }
                }
            }

            // Calculate average and assign to the pixel
            // RU: Рассчитать среднее значение и назначить его пикселю
            // EN: Calculate average and assign to the pixel
            // FR: Calculer la valeur moyenne et l'attribuer au pixel
            // ES: Calcular el valor promedio y asignarlo al píxel
            image[i][j].rgbtRed = round((float) redSum / count);
            image[i][j].rgbtGreen = round((float) greenSum / count);
            image[i][j].rgbtBlue = round((float) blueSum / count);
        }
    }
}

// Detect edges
// RU: Обнаружение краев
// EN: Detect edges
// FR: Détecter les contours
// ES: Detectar los bordes
void edges(int height, int width, RGBTRIPLE image[height][width])
{
    RGBTRIPLE temp[height][width];

    // Copy image to temp
    // RU: Копировать изображение во временный массив
    // EN: Copy image to temp
    // FR: Copier l'image dans un tableau temporaire
    // ES: Copiar la imagen a un arreglo temporal
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            temp[i][j] = image[i][j];
        }
    }

    // Sobel kernels
    // RU: Ядра Собеля
    // EN: Sobel kernels
    // FR: Noyaux de Sobel
    // ES: Núcleos de Sobel
    int Gx[3][3] = {{-1, 0, 1}, {-2, 0, 2}, {-1, 0, 1}};
    int Gy[3][3] = {{-1, -2, -1}, {0, 0, 0}, {1, 2, 1}};

    // Iterate over each pixel
    // RU: Перебрать каждый пиксель
    // EN: Iterate over each pixel
    // FR: Itérer sur chaque pixel
    // ES: Iterar sobre cada píxel
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            int redGx = 0, redGy = 0;
            int greenGx = 0, greenGy = 0;
            int blueGx = 0, blueGy = 0;

            // Iterate over the neighboring pixels
            // RU: Перебрать соседние пиксели
            // EN: Iterate over the neighboring pixels
            // FR: Itérer sur les pixels voisins
            // ES: Iterar sobre los píxeles vecinos
            for (int di = -1; di <= 1; di++)
            {
                for (int dj = -1; dj <= 1; dj++)
                {
                    int ni = i + di;
                    int nj = j + dj;

                    // Check if neighbor is within bounds
                    // RU: Проверить, находится ли соседний пиксель в пределах изображения
                    // EN: Check if neighbor is within bounds
                    // FR: Vérifier si le voisin est dans les limites de l'image
                    // ES: Verificar si el píxel vecino está dentro de los límites
                    if (ni >= 0 && ni < height && nj >= 0 && nj < width)
                    {
                        redGx += temp[ni][nj].rgbtRed * Gx[di + 1][dj + 1];
                        redGy += temp[ni][nj].rgbtRed * Gy[di + 1][dj + 1];

                        greenGx += temp[ni][nj].rgbtGreen * Gx[di + 1][dj + 1];
                        greenGy += temp[ni][nj].rgbtGreen * Gy[di + 1][dj + 1];

                        blueGx += temp[ni][nj].rgbtBlue * Gx[di + 1][dj + 1];
                        blueGy += temp[ni][nj].rgbtBlue * Gy[di + 1][dj + 1];
                    }
                }
            }

            // Calculate the magnitude of the gradient
            // RU: Рассчитать величину градиента
            // EN: Calculate the magnitude of the gradient
            // FR: Calculer la magnitude du gradient
            // ES: Calcular la magnitud del gradiente
            int red = round(sqrt(redGx * redGx + redGy * redGy));
            int green = round(sqrt(greenGx * greenGx + greenGy * greenGy));
            int blue = round(sqrt(blueGx * blueGx + blueGy * blueGy));

            // Cap the values at 255
            // RU: Ограничить значения 255
            // EN: Cap the values at 255
            // FR: Limiter les valeurs à 255
            // ES: Limitar los valores a 255
            image[i][j].rgbtRed = (red > 255) ? 255 : red;
            image[i][j].rgbtGreen = (green > 255) ? 255 : green;
            image[i][j].rgbtBlue = (blue > 255) ? 255 : blue;
        }
    }
}
