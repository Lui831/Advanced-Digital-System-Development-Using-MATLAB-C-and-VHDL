#include <stdio.h>

#define NUM_TERMS 4

float moving_avg_function(float current_input){

    // Creates an empty array for holding the last terms - It must be static to hold the last items
    static float last_terms[NUM_TERMS] = {0};
    float acc_value = 0;

    // For loop to right shift last terms
    for(int i = NUM_TERMS - 1; i > 0; i--) last_terms[i] = last_terms[i - 1];
    
    // Stores the current term
    last_terms[0] = current_input;

    // Accumulates the last terms values and returns the function
    for(int i = 0; i < NUM_TERMS; i++) acc_value += last_terms[i];

    return acc_value / NUM_TERMS;

}

float square_wave[40] = {1, 1, 1, 1, 1, 1, 1, 1, 1, 1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1};

int main(){

    // Creates float variables for the input and output values
    float input_value, output_value;

    // Initializes an itrt for the square_wave
    int square_wave_itrt = 0;

    // Initializes a file and writes the firts line
    FILE* file_pointer = fopen("data.txt", "w");
    fputs("iterator,input_value, output_value\n", file_pointer);

    // Creates a str to write into the file
    char file_string[100];

    // Enters a continuous loop
    while(1){

        // Asks the user for a input value and stores it
        printf("Entering the %ith value from the square_wave...", square_wave_itrt);
        input_value = square_wave[square_wave_itrt];
        square_wave_itrt++;

        // Executes the moving avg function
        output_value = moving_avg_function(input_value);

        // Prints the current value
        printf("\nThe current moving avg value is: %.4f\n\n", output_value);

        // Puts the values into the file string and puts the file string into the file
        sprintf(file_string, "%d, %.4f, %.4f\n",square_wave_itrt, input_value, output_value);
        fputs(file_string, file_pointer);

        // If the square_wave_itrt is equal or greater than 40, stops the code
        if (square_wave_itrt >= 40) break;

    }

    return 0;
}