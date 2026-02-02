/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 * File: _coder_doFilter_api.h
 *
 * MATLAB Coder version            : 25.1
 * C/C++ source code generated on  : 22-Jan-2026 22:38:08
 */

#ifndef _CODER_DOFILTER_API_H
#define _CODER_DOFILTER_API_H

/* Include Files */
#include "emlrt.h"
#include "mex.h"
#include "tmwtypes.h"
#include <string.h>

/* Variable Declarations */
extern emlrtCTX emlrtRootTLSGlobal;
extern emlrtContext emlrtContextGlobal;

#ifdef __cplusplus
extern "C" {
#endif

/* Function Declarations */
void doFilter(real_T x[1000], real_T y[1000]);

void doFilter_api(const mxArray *prhs, const mxArray **plhs);

void doFilter_atexit(void);

void doFilter_initialize(void);

void doFilter_terminate(void);

void doFilter_xil_shutdown(void);

void doFilter_xil_terminate(void);

#ifdef __cplusplus
}
#endif

#endif
/*
 * File trailer for _coder_doFilter_api.h
 *
 * [EOF]
 */
