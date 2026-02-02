/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 * File: SystemCore.h
 *
 * MATLAB Coder version            : 25.1
 * C/C++ source code generated on  : 22-Jan-2026 19:21:49
 */

#ifndef SYSTEMCORE_H
#define SYSTEMCORE_H

/* Include Files */
#include "iir_filter_internal_types.h"
#include "rtwtypes.h"
#include <stddef.h>
#include <stdlib.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Function Declarations */
void SystemCore_step(dsp_SOSFilter *obj, const double varargin_1[1001],
                     double varargout_1[1001]);

#ifdef __cplusplus
}
#endif

#endif
/*
 * File trailer for SystemCore.h
 *
 * [EOF]
 */
