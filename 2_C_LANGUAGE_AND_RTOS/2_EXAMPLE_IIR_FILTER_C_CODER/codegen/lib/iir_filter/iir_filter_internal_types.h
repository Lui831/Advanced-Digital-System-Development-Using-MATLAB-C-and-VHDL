/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 * File: iir_filter_internal_types.h
 *
 * MATLAB Coder version            : 25.1
 * C/C++ source code generated on  : 22-Jan-2026 19:21:49
 */

#ifndef IIR_FILTER_INTERNAL_TYPES_H
#define IIR_FILTER_INTERNAL_TYPES_H

/* Include Files */
#include "iir_filter_types.h"
#include "rtwtypes.h"

/* Type Definitions */
#ifndef typedef_dsp_SOSFilter_0
#define typedef_dsp_SOSFilter_0
typedef struct {
  int S0_isInitialized;
  double W0_FILT_STATES[182182];
  int W1_PreviousNumChannels;
  double P0_ICRTP;
  double P1_RTP1COEFF[273];
  double P2_RTP2COEFF[273];
  double P3_RTP3COEFF[92];
} dsp_SOSFilter_0;
#endif /* typedef_dsp_SOSFilter_0 */

#ifndef typedef_dsp_SOSFilter
#define typedef_dsp_SOSFilter
typedef struct {
  dsp_SOSFilter_0 cSFunObject;
} dsp_SOSFilter;
#endif /* typedef_dsp_SOSFilter */

#endif
/*
 * File trailer for iir_filter_internal_types.h
 *
 * [EOF]
 */
