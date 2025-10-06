/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 * File: main.c
 *
 * MATLAB Coder version            : 25.2
 * C/C++ source code generated on  : 06-Oct-2025 08:12:02
 */

/*************************************************************************/
/* This automatically generated example C main file shows how to call    */
/* entry-point functions that MATLAB Coder generated. You must customize */
/* this file for your application. Do not modify this file directly.     */
/* Instead, make a copy of this file, modify it, and integrate it into   */
/* your development environment.                                         */
/*                                                                       */
/* This file initializes entry-point function arguments to a default     */
/* size and value before calling the entry-point functions. It does      */
/* not store or use any values returned from the entry-point functions.  */
/* If necessary, it does pre-allocate memory for returned values.        */
/* You can use this file as a starting point for a main function that    */
/* you can deploy in your application.                                   */
/*                                                                       */
/* After you copy the file, and before you deploy it, you must make the  */
/* following changes:                                                    */
/* * For variable-size function arguments, change the example sizes to   */
/* the sizes that your application requires.                             */
/* * Change the example values of function arguments to the values that  */
/* your application requires.                                            */
/* * If the entry-point functions return values, store these values or   */
/* otherwise use them as required by your application.                   */
/*                                                                       */
/*************************************************************************/

/* Include Files */
#include "main.h"
#include "moving_avg.h"
#include "moving_avg_emxAPI.h"
#include "moving_avg_initialize.h"
#include "moving_avg_terminate.h"
#include "moving_avg_types.h"

/* Function Declarations */
static emxArray_real_T *argInit_1xUnbounded_real_T(void);

static double argInit_real_T(void);

static unsigned short argInit_uint16_T(void);

/* Function Definitions */
/*
 * Arguments    : void
 * Return Type  : emxArray_real_T *
 */
static emxArray_real_T *argInit_1xUnbounded_real_T(void)
{
  emxArray_real_T *result;
  double *result_data;
  int idx1;
  /* Set the size of the array.
Change this size to the value that the application requires. */
  result = emxCreate_real_T(1, 2);
  result_data = result->data;
  /* Loop over the array to initialize each element. */
  for (idx1 = 0; idx1 < result->size[1U]; idx1++) {
    /* Set the value of the array element.
Change this value to the value that the application requires. */
    result_data[idx1] = argInit_real_T();
  }
  return result;
}

/*
 * Arguments    : void
 * Return Type  : double
 */
static double argInit_real_T(void)
{
  return 0.0;
}

/*
 * Arguments    : void
 * Return Type  : unsigned short
 */
static unsigned short argInit_uint16_T(void)
{
  return 0U;
}

/*
 * Arguments    : int argc
 *                char **argv
 * Return Type  : int
 */
int main(int argc, char **argv)
{
  (void)argc;
  (void)argv;
  /* Initialize the application.
You do not need to do this more than one time. */
  moving_avg_initialize();
  /* Invoke the entry-point functions.
You can call entry-point functions multiple times. */
  main_moving_avg();
  /* Terminate the application.
You do not need to do this more than one time. */
  moving_avg_terminate();
  return 0;
}

/*
 * Arguments    : void
 * Return Type  : void
 */
void main_moving_avg(void)
{
  emxArray_real_T *data_out;
  emxArray_real_T *matrix_in;
  /* Initialize function 'moving_avg' input arguments. */
  /* Initialize function input argument 'matrix_in'. */
  matrix_in = argInit_1xUnbounded_real_T();
  /* Call the entry-point 'moving_avg'. */
  emxInitArray_real_T(&data_out, 2);
  moving_avg(argInit_uint16_T(), matrix_in, data_out);
  emxDestroyArray_real_T(matrix_in);
  emxDestroyArray_real_T(data_out);
}

/*
 * File trailer for main.c
 *
 * [EOF]
 */
