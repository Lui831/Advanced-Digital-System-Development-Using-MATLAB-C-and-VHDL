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

int main(){

    // Creates float variables for the input and output values
    float input_value, output_value;

    // Enters a continuous loop
    while(1){

        // Asks the user for a input value and stores it
        printf("Please, enter an input value: ");
        scanf("%f", &input_value);

        // Executes the moving avg function
        output_value = moving_avg_function(input_value);

        // Prints the current value
        printf("\nThe current moving avg value is: %.4f\n", output_value);

    }

    return 0;
}