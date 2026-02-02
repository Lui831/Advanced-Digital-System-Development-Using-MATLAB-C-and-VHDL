/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 * File: main.c
 *
 * MATLAB Coder version            : 25.1
 * C/C++ source code generated on  : 22-Jan-2026 19:21:49
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
#include "doFilter.h"
#include "iir_filter.h"
#include "iir_filter_initialize.h"
#include "iir_filter_terminate.h"

/* Function Declarations */
static void argInit_1x1001_real_T(double result[1001]);

static double argInit_real_T(void);

/* Function Definitions */
/*
 * Arguments    : double result[1001]
 * Return Type  : void
 */
static void argInit_1x1001_real_T(double result[1001])
{
  int idx1;
  /* Loop over the array to initialize each element. */
  for (idx1 = 0; idx1 < 1001; idx1++) {
    /* Set the value of the array element.
Change this value to the value that the application requires. */
    result[idx1] = argInit_real_T();
  }
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
  iir_filter_initialize();
  /* Invoke the entry-point functions.
You can call entry-point functions multiple times. */
  main_iir_filter();
  main_doFilter();
  /* Terminate the application.
You do not need to do this more than one time. */
  iir_filter_terminate();
  return 0;
}

/*
 * Arguments    : void
 * Return Type  : void
 */
void main_doFilter(void)
{
  double dv[1001];
  /* Initialize function 'doFilter' input arguments. */
  /* Initialize function input argument 'x'. */
  /* Call the entry-point 'doFilter'. */
  argInit_1x1001_real_T(dv);
  doFilter(dv);
}

/*
 * Arguments    : void
 * Return Type  : void
 */
void main_iir_filter(void)
{
  double dv[1001];
  double y[1001];
  /* Initialize function 'iir_filter' input arguments. */
  /* Initialize function input argument 'x'. */
  /* Call the entry-point 'iir_filter'. */
  argInit_1x1001_real_T(dv);
  iir_filter(dv, y);
}

/*
 * File trailer for main.c
 *
 * [EOF]
 */
