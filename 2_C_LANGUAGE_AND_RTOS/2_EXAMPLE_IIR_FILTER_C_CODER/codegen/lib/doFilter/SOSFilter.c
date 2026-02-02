/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 * File: SOSFilter.c
 *
 * MATLAB Coder version            : 25.1
 * C/C++ source code generated on  : 22-Jan-2026 22:38:08
 */

/* Include Files */
#include "SOSFilter.h"
#include "doFilter_internal_types.h"

/* Function Definitions */
/*
 * Arguments    : dsp_SOSFilter *obj
 * Return Type  : dsp_SOSFilter *
 */
dsp_SOSFilter *SOSFilter_SOSFilter(dsp_SOSFilter *obj)
{
  static const double dv[36] = {1.0,
                                1.0,
                                1.0,
                                1.0,
                                1.0,
                                1.0,
                                1.0,
                                1.0,
                                1.0,
                                1.0,
                                1.0,
                                1.0,
                                -1.81186117392133,
                                -1.73024914725395,
                                -1.65751121811269,
                                -1.5934404835378,
                                -1.53772236493398,
                                -1.48999351202201,
                                -1.44988334461733,
                                -1.41704244230025,
                                -1.39116136179915,
                                -1.37198272020327,
                                -1.3593086824303,
                                -1.35300539195744,
                                0.952425202024228,
                                0.864481721614627,
                                0.786100790424901,
                                0.717059453982174,
                                0.657018728711795,
                                0.605587075652337,
                                0.562365165041593,
                                0.526976468454915,
                                0.499087536039302,
                                0.478421017140759,
                                0.464763728648939,
                                0.457971429463979};
  static const double dv1[13] = {0.941071593986391,
                                 0.898682717217145,
                                 0.860903002134397,
                                 0.827624984379993,
                                 0.798685273411442,
                                 0.773895146918587,
                                 0.753062127414732,
                                 0.736004727688792,
                                 0.722562224459614,
                                 0.712600934336008,
                                 0.706018102769809,
                                 0.702744205355354,
                                 1.0};
  static const signed char iv[36] = {
      1,  1,  1,  1,  1,  1,  1, 1, 1, 1, 1, 1, -2, -2, -2, -2, -2, -2,
      -2, -2, -2, -2, -2, -2, 1, 1, 1, 1, 1, 1, 1,  1,  1,  1,  1,  1};
  dsp_SOSFilter *b_obj;
  int i;
  b_obj = obj;
  /* System object Constructor function: dsp.SOSFilter */
  b_obj->cSFunObject.P0_ICRTP = 0.0;
  for (i = 0; i < 36; i++) {
    b_obj->cSFunObject.P1_RTP1COEFF[i] = iv[i];
    b_obj->cSFunObject.P2_RTP2COEFF[i] = dv[i];
  }
  for (i = 0; i < 13; i++) {
    b_obj->cSFunObject.P3_RTP3COEFF[i] = dv1[i];
  }
  /* System object Initialization function: dsp.SOSFilter */
  for (i = 0; i < 24; i++) {
    obj->cSFunObject.W0_FILT_STATES[i] = obj->cSFunObject.P0_ICRTP;
  }
  return b_obj;
}

/*
 * File trailer for SOSFilter.c
 *
 * [EOF]
 */
