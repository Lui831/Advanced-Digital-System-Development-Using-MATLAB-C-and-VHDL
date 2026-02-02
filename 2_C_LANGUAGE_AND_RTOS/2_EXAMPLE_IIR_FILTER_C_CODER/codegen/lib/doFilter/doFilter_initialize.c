/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 * File: doFilter_initialize.c
 *
 * MATLAB Coder version            : 25.1
 * C/C++ source code generated on  : 22-Jan-2026 22:38:08
 */

/* Include Files */
#include "doFilter_initialize.h"
#include "doFilter.h"
#include "doFilter_data.h"

/* Function Definitions */
/*
 * Arguments    : void
 * Return Type  : void
 */
void doFilter_initialize(void)
{
  doFilter_init();
  isInitialized_doFilter = true;
}

/*
 * File trailer for doFilter_initialize.c
 *
 * [EOF]
 */
