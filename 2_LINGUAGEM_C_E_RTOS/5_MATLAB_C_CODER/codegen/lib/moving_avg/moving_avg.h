/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 * File: moving_avg.h
 *
 * MATLAB Coder version            : 25.2
 * C/C++ source code generated on  : 03-Oct-2025 15:00:11
 */

#ifndef MOVING_AVG_H
#define MOVING_AVG_H

/* Include Files */
#include "moving_avg_types.h"
#include "rtwtypes.h"
#include <stddef.h>
#include <stdlib.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Function Declarations */
extern void moving_avg(double num_terms, const double matrix_in[3000],
                       emxArray_real_T *data_out);

#ifdef __cplusplus
}
#endif

#endif
/*
 * File trailer for moving_avg.h
 *
 * [EOF]
 */
