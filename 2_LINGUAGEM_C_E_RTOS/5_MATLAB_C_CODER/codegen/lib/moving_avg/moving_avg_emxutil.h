/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 * File: moving_avg_emxutil.h
 *
 * MATLAB Coder version            : 25.2
 * C/C++ source code generated on  : 03-Oct-2025 15:00:11
 */

#ifndef MOVING_AVG_EMXUTIL_H
#define MOVING_AVG_EMXUTIL_H

/* Include Files */
#include "moving_avg_types.h"
#include "rtwtypes.h"
#include <stddef.h>
#include <stdlib.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Function Declarations */
extern void emxEnsureCapacity_real_T(emxArray_real_T *emxArray, int oldNumel);

extern void emxFree_real_T(emxArray_real_T **pEmxArray);

extern void emxInit_real_T(emxArray_real_T **pEmxArray, int numDimensions);

#ifdef __cplusplus
}
#endif

#endif
/*
 * File trailer for moving_avg_emxutil.h
 *
 * [EOF]
 */
