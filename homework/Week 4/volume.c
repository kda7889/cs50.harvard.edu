#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <limits.h>

// Number of bytes in .wav header
const int HEADER_SIZE = 44;

int main(int argc, char *argv[])
{
    // Check command-line arguments
    if (argc != 4)
    {
        printf("Usage: ./volume input.wav output.wav factor\n");
        return 1;
    }

    // Open files and determine scaling factor
    FILE *input = fopen(argv[1], "r");
    if (input == NULL)
    {
        printf("Could not open input file.");
        return 1;
    }

    FILE *output = fopen(argv[2], "w");
    if (output == NULL)
    {
        printf("Could not open output file.");
        fclose(input);
        return 1;
    }

    float factor = atof(argv[3]);

    // Copy header from input file to output file
    uint8_t header[HEADER_SIZE];
    if (fread(header, HEADER_SIZE, 1, input) != 1)
    {
        printf("Error reading WAV header from input file.\n");
        fclose(input);
        fclose(output);
        return 1;
    }
    if (fwrite(header, HEADER_SIZE, 1, output) != 1)
    {
        printf("Error writing WAV header to output file.\n");
        fclose(input);
        fclose(output);
        return 1;
    }

    // Read samples from input file and write updated data to output file
    int16_t buffer;

    while (fread(&buffer, sizeof(int16_t), 1, input) == 1)
    {
        int32_t adjusted_sample = buffer * factor;

        // Clamp the value to prevent overflow
        if (adjusted_sample > INT16_MAX)
        {
            adjusted_sample = INT16_MAX;
        }
        else if (adjusted_sample < INT16_MIN)
        {
            adjusted_sample = INT16_MIN;
        }

        buffer = (int16_t)adjusted_sample;
        if (fwrite(&buffer, sizeof(int16_t), 1, output) != 1)
        {
            printf("Error writing audio data to output file.\n");
            fclose(input);
            fclose(output);
            return 1;
        }
    }

    // Close files
    fclose(input);
    fclose(output);

    return 0;
}
