/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 * File: _coder_iir_filter_api.h
 *
 * MATLAB Coder version            : 25.1
 * C/C++ source code generated on  : 22-Jan-2026 19:21:49
 */

#ifndef _CODER_IIR_FILTER_API_H
#define _CODER_IIR_FILTER_API_H

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
void doFilter(real_T x[1001]);

void doFilter_api(const mxArray *prhs);

void iir_filter(real_T x[1001], real_T y[1001]);

void iir_filter_api(const mxArray *prhs, const mxArray **plhs);

void iir_filter_atexit(void);

void iir_filter_initialize(void);

void iir_filter_terminate(void);

void iir_filter_xil_shutdown(void);

void iir_filter_xil_terminate(void);

#ifdef __cplusplus
}
#endif

#endif
/*
 * File trailer for _coder_iir_filter_api.h
 *
 * [EOF]
 */
