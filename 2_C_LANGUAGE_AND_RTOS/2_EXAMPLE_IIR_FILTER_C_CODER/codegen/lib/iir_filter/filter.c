/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 * File: filter.c
 *
 * MATLAB Coder version            : 25.1
 * C/C++ source code generated on  : 22-Jan-2026 19:21:49
 */

/* Include Files */
#include "filter.h"
#include <string.h>

/* Function Definitions */
/*
 * Arguments    : const double x[1001]
 *                double y[1001]
 * Return Type  : void
 */
void filter(const double x[1001], double y[1001])
{
  static const double dv[3] = {0.0675, 0.1349, 0.0675};
  static const double dv1[3] = {1.0, -1.143, 0.4128};
  int j;
  int k;
  memset(&y[0], 0, 1001U * sizeof(double));
  for (k = 0; k < 1001; k++) {
    double as;
    int naxpy;
    int y_tmp;
    if (1001 - k < 3) {
      naxpy = 1000 - k;
    } else {
      naxpy = 2;
    }
    for (j = 0; j <= naxpy; j++) {
      y_tmp = k + j;
      y[y_tmp] += x[k] * dv[j];
    }
    if (1000 - k < 2) {
      naxpy = 999 - k;
    } else {
      naxpy = 1;
    }
    as = -y[k];
    for (j = 0; j <= naxpy; j++) {
      y_tmp = (k + j) + 1;
      y[y_tmp] += as * dv1[j + 1];
    }
  }
}

/*
 * File trailer for filter.c
 *
 * [EOF]
 */
