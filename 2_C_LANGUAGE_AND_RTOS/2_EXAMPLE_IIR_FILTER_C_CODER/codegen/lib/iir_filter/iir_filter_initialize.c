/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 * File: iir_filter_initialize.c
 *
 * MATLAB Coder version            : 25.1
 * C/C++ source code generated on  : 22-Jan-2026 19:21:49
 */

/* Include Files */
#include "iir_filter_initialize.h"
#include "doFilter.h"
#include "iir_filter_data.h"

/* Function Definitions */
/*
 * Arguments    : void
 * Return Type  : void
 */
void iir_filter_initialize(void)
{
  doFilter_init();
  isInitialized_iir_filter = true;
}

/*
 * File trailer for iir_filter_initialize.c
 *
 * [EOF]
 */
