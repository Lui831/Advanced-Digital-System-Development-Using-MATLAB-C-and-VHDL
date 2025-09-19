/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * File: iir_filter_simulink.c
 *
 * Code generated for Simulink model 'iir_filter_simulink'.
 *
 * Model version                  : 1.49
 * Simulink Coder version         : 25.1 (R2025a) 21-Nov-2024
 * C/C++ source code generated on : Thu Sep 18 11:36:47 2025
 *
 * Target selection: ert.tlc
 * Embedded hardware selection: ARM Compatible->ARM Cortex-A (32-bit)
 * Emulation hardware selection:
 *    Differs from embedded hardware (Custom Processor->MATLAB Host Computer)
 * Code generation objectives: Unspecified
 * Validation result: Not run
 */

#include "iir_filter_simulink.h"
#include "rtwtypes.h"

/* Block signals (default storage) */
B_iir_filter_simulink_T iir_filter_simulink_B;

/* Block states (default storage) */
DW_iir_filter_simulink_T iir_filter_simulink_DW;

/* External inputs (root inport signals with default storage) */
ExtU_iir_filter_simulink_T iir_filter_simulink_U;

/* External outputs (root outports fed by signals with default storage) */
ExtY_iir_filter_simulink_T iir_filter_simulink_Y;

/* Real-time model */
static RT_MODEL_iir_filter_simulink_T iir_filter_simulink_M_;
RT_MODEL_iir_filter_simulink_T *const iir_filter_simulink_M =
  &iir_filter_simulink_M_;

/* Model step function */
void iir_filter_simulink_step(void)
{
  real_T rtb_Delay12;
  real_T rtb_Delay13;
  real_T rtb_Delay14;
  real_T rtb_Delay15;
  real_T rtb_SumA32;
  real_T rtb_SumA33;
  real_T rtb_SumA34;
  real_T rtb_SumA35;

  /* Delay: '<S1>/Delay11' */
  iir_filter_simulink_B.Delay11 = iir_filter_simulink_DW.Delay11_DSTATE;

  /* Sum: '<S1>/SumA31' incorporates:
   *  Delay: '<S1>/Delay11'
   *  Delay: '<S1>/Delay21'
   *  Gain: '<S1>/a(2)(1)'
   *  Gain: '<S1>/a(3)(1)'
   *  Gain: '<S1>/s(1)'
   *  Inport: '<Root>/In1'
   *  Sum: '<S1>/SumA21'
   */
  iir_filter_simulink_B.SumA31 = (0.30207843389004441 *
    iir_filter_simulink_U.In1 - -0.53242498807547933 *
    iir_filter_simulink_DW.Delay11_DSTATE) - 0.740738723635657 *
    iir_filter_simulink_DW.Delay21_DSTATE;

  /* Delay: '<S1>/Delay12' */
  rtb_Delay12 = iir_filter_simulink_DW.Delay12_DSTATE;

  /* Sum: '<S1>/SumA32' incorporates:
   *  Delay: '<S1>/Delay11'
   *  Delay: '<S1>/Delay12'
   *  Delay: '<S1>/Delay21'
   *  Delay: '<S1>/Delay22'
   *  Gain: '<S1>/a(2)(2)'
   *  Gain: '<S1>/a(3)(2)'
   *  Gain: '<S1>/b(2)(1)'
   *  Gain: '<S1>/s(2)'
   *  Sum: '<S1>/SumA22'
   *  Sum: '<S1>/SumB21'
   *  Sum: '<S1>/SumB31'
   */
  rtb_SumA32 = (((2.0 * iir_filter_simulink_DW.Delay11_DSTATE +
                  iir_filter_simulink_B.SumA31) +
                 iir_filter_simulink_DW.Delay21_DSTATE) * 0.24232728096078959 -
                -0.42711125721366466 * iir_filter_simulink_DW.Delay12_DSTATE) -
    0.396420381056823 * iir_filter_simulink_DW.Delay22_DSTATE;

  /* Delay: '<S1>/Delay13' */
  rtb_Delay13 = iir_filter_simulink_DW.Delay13_DSTATE;

  /* Sum: '<S1>/SumA33' incorporates:
   *  Delay: '<S1>/Delay12'
   *  Delay: '<S1>/Delay13'
   *  Delay: '<S1>/Delay22'
   *  Delay: '<S1>/Delay23'
   *  Gain: '<S1>/a(2)(3)'
   *  Gain: '<S1>/a(3)(3)'
   *  Gain: '<S1>/b(2)(2)'
   *  Gain: '<S1>/s(3)'
   *  Sum: '<S1>/SumA23'
   *  Sum: '<S1>/SumB22'
   *  Sum: '<S1>/SumB32'
   */
  rtb_SumA33 = (((2.0 * iir_filter_simulink_DW.Delay12_DSTATE + rtb_SumA32) +
                 iir_filter_simulink_DW.Delay22_DSTATE) * 0.20742601972657851 -
                -0.36559642691893418 * iir_filter_simulink_DW.Delay13_DSTATE) -
    0.19530050582524824 * iir_filter_simulink_DW.Delay23_DSTATE;

  /* Delay: '<S1>/Delay14' */
  rtb_Delay14 = iir_filter_simulink_DW.Delay14_DSTATE;

  /* Sum: '<S1>/SumA34' incorporates:
   *  Delay: '<S1>/Delay13'
   *  Delay: '<S1>/Delay14'
   *  Delay: '<S1>/Delay23'
   *  Delay: '<S1>/Delay24'
   *  Gain: '<S1>/a(2)(4)'
   *  Gain: '<S1>/a(3)(4)'
   *  Gain: '<S1>/b(2)(3)'
   *  Gain: '<S1>/s(4)'
   *  Sum: '<S1>/SumA24'
   *  Sum: '<S1>/SumB23'
   *  Sum: '<S1>/SumB33'
   */
  rtb_SumA34 = (((2.0 * iir_filter_simulink_DW.Delay13_DSTATE + rtb_SumA33) +
                 iir_filter_simulink_DW.Delay23_DSTATE) * 0.18777694427783956 -
                -0.33096416725455496 * iir_filter_simulink_DW.Delay14_DSTATE) -
    0.082071944365913224 * iir_filter_simulink_DW.Delay24_DSTATE;

  /* Delay: '<S1>/Delay15' */
  rtb_Delay15 = iir_filter_simulink_DW.Delay15_DSTATE;

  /* Sum: '<S1>/SumA35' incorporates:
   *  Delay: '<S1>/Delay14'
   *  Delay: '<S1>/Delay15'
   *  Delay: '<S1>/Delay24'
   *  Delay: '<S1>/Delay25'
   *  Gain: '<S1>/a(2)(5)'
   *  Gain: '<S1>/a(3)(5)'
   *  Gain: '<S1>/b(2)(4)'
   *  Gain: '<S1>/s(5)'
   *  Sum: '<S1>/SumA25'
   *  Sum: '<S1>/SumB24'
   *  Sum: '<S1>/SumB34'
   */
  rtb_SumA35 = (((2.0 * iir_filter_simulink_DW.Delay14_DSTATE + rtb_SumA34) +
                 iir_filter_simulink_DW.Delay24_DSTATE) * 0.178868997019849 -
                -0.315263563767121 * iir_filter_simulink_DW.Delay15_DSTATE) -
    0.030739551846517135 * iir_filter_simulink_DW.Delay25_DSTATE;

  /* Outport: '<Root>/Out1' incorporates:
   *  Delay: '<S1>/Delay15'
   *  Delay: '<S1>/Delay25'
   *  Gain: '<S1>/b(2)(5)'
   *  Sum: '<S1>/SumB25'
   *  Sum: '<S1>/SumB35'
   */
  iir_filter_simulink_Y.Out1 = (2.0 * iir_filter_simulink_DW.Delay15_DSTATE +
    rtb_SumA35) + iir_filter_simulink_DW.Delay25_DSTATE;

  /* Update for Delay: '<S1>/Delay11' */
  iir_filter_simulink_DW.Delay11_DSTATE = iir_filter_simulink_B.SumA31;

  /* Update for Delay: '<S1>/Delay21' */
  iir_filter_simulink_DW.Delay21_DSTATE = iir_filter_simulink_B.Delay11;

  /* Update for Delay: '<S1>/Delay12' */
  iir_filter_simulink_DW.Delay12_DSTATE = rtb_SumA32;

  /* Update for Delay: '<S1>/Delay22' */
  iir_filter_simulink_DW.Delay22_DSTATE = rtb_Delay12;

  /* Update for Delay: '<S1>/Delay13' */
  iir_filter_simulink_DW.Delay13_DSTATE = rtb_SumA33;

  /* Update for Delay: '<S1>/Delay23' */
  iir_filter_simulink_DW.Delay23_DSTATE = rtb_Delay13;

  /* Update for Delay: '<S1>/Delay14' */
  iir_filter_simulink_DW.Delay14_DSTATE = rtb_SumA34;

  /* Update for Delay: '<S1>/Delay24' */
  iir_filter_simulink_DW.Delay24_DSTATE = rtb_Delay14;

  /* Update for Delay: '<S1>/Delay15' */
  iir_filter_simulink_DW.Delay15_DSTATE = rtb_SumA35;

  /* Update for Delay: '<S1>/Delay25' */
  iir_filter_simulink_DW.Delay25_DSTATE = rtb_Delay15;
}

/* Model initialize function */
void iir_filter_simulink_initialize(void)
{
  /* (no initialization code required) */
}

/* Model terminate function */
void iir_filter_simulink_terminate(void)
{
  /* (no terminate code required) */
}

/*
 * File trailer for generated code.
 *
 * [EOF]
 */
