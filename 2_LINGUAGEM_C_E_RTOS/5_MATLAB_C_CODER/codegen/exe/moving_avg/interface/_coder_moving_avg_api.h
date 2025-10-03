/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 * File: _coder_moving_avg_api.h
 *
 * MATLAB Coder version            : 25.2
 * C/C++ source code generated on  : 03-Oct-2025 14:39:57
 */

#ifndef _CODER_MOVING_AVG_API_H
#define _CODER_MOVING_AVG_API_H

/* Include Files */
#include "emlrt.h"
#include "mex.h"
#include "tmwtypes.h"
#include <string.h>

/* Type Definitions */
#ifndef struct_emxArray_real_T
#define struct_emxArray_real_T
struct emxArray_real_T {
  real_T *data;
  int32_T *size;
  int32_T allocatedSize;
  int32_T numDimensions;
  boolean_T canFreeData;
};
#endif /* struct_emxArray_real_T */
#ifndef typedef_emxArray_real_T
#define typedef_emxArray_real_T
typedef struct emxArray_real_T emxArray_real_T;
#endif /* typedef_emxArray_real_T */

/* Variable Declarations */
extern emlrtCTX emlrtRootTLSGlobal;
extern emlrtContext emlrtContextGlobal;

#ifdef __cplusplus
extern "C" {
#endif

/* Function Declarations */
void moving_avg(real_T num_terms, real_T matrix_in[3000],
                emxArray_real_T *data_out);

void moving_avg_api(const mxArray *const prhs[2], const mxArray **plhs);

void moving_avg_atexit(void);

void moving_avg_initialize(void);

void moving_avg_terminate(void);

void moving_avg_xil_shutdown(void);

void moving_avg_xil_terminate(void);

#ifdef __cplusplus
}
#endif

#endif
/*
 * File trailer for _coder_moving_avg_api.h
 *
 * [EOF]
 */
