/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * File: iir_filter_simulink.h
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

#ifndef iir_filter_simulink_h_
#define iir_filter_simulink_h_
#ifndef iir_filter_simulink_COMMON_INCLUDES_
#define iir_filter_simulink_COMMON_INCLUDES_
#include "rtwtypes.h"
#endif                                /* iir_filter_simulink_COMMON_INCLUDES_ */

#include "iir_filter_simulink_types.h"
#include <stddef.h>

/* Macros for accessing real-time model data structure */
#ifndef rtmGetErrorStatus
#define rtmGetErrorStatus(rtm)         ((rtm)->errorStatus)
#endif

#ifndef rtmSetErrorStatus
#define rtmSetErrorStatus(rtm, val)    ((rtm)->errorStatus = (val))
#endif

/* Block signals (default storage) */
typedef struct {
  real_T Delay11;                      /* '<S1>/Delay11' */
  real_T SumA31;                       /* '<S1>/SumA31' */
} B_iir_filter_simulink_T;

/* Block states (default storage) for system '<Root>' */
typedef struct {
  real_T Delay11_DSTATE;               /* '<S1>/Delay11' */
  real_T Delay21_DSTATE;               /* '<S1>/Delay21' */
  real_T Delay12_DSTATE;               /* '<S1>/Delay12' */
  real_T Delay22_DSTATE;               /* '<S1>/Delay22' */
  real_T Delay13_DSTATE;               /* '<S1>/Delay13' */
  real_T Delay23_DSTATE;               /* '<S1>/Delay23' */
  real_T Delay14_DSTATE;               /* '<S1>/Delay14' */
  real_T Delay24_DSTATE;               /* '<S1>/Delay24' */
  real_T Delay15_DSTATE;               /* '<S1>/Delay15' */
  real_T Delay25_DSTATE;               /* '<S1>/Delay25' */
} DW_iir_filter_simulink_T;

/* External inputs (root inport signals with default storage) */
typedef struct {
  real_T In1;                          /* '<Root>/In1' */
} ExtU_iir_filter_simulink_T;

/* External outputs (root outports fed by signals with default storage) */
typedef struct {
  real_T Out1;                         /* '<Root>/Out1' */
} ExtY_iir_filter_simulink_T;

/* Real-time Model Data Structure */
struct tag_RTM_iir_filter_simulink_T {
  const char_T * volatile errorStatus;
};

/* Block signals (default storage) */
extern B_iir_filter_simulink_T iir_filter_simulink_B;

/* Block states (default storage) */
extern DW_iir_filter_simulink_T iir_filter_simulink_DW;

/* External inputs (root inport signals with default storage) */
extern ExtU_iir_filter_simulink_T iir_filter_simulink_U;

/* External outputs (root outports fed by signals with default storage) */
extern ExtY_iir_filter_simulink_T iir_filter_simulink_Y;

/* Model entry point functions */
extern void iir_filter_simulink_initialize(void);
extern void iir_filter_simulink_step(void);
extern void iir_filter_simulink_terminate(void);

/* Real-time Model object */
extern RT_MODEL_iir_filter_simulink_T *const iir_filter_simulink_M;
extern volatile boolean_T stopRequested;
extern volatile boolean_T runModel;

/*-
 * The generated code includes comments that allow you to trace directly
 * back to the appropriate location in the model.  The basic format
 * is <system>/block_name, where system is the system number (uniquely
 * assigned by Simulink) and block_name is the name of the block.
 *
 * Use the MATLAB hilite_system command to trace the generated code back
 * to the model.  For example,
 *
 * hilite_system('<S3>')    - opens system 3
 * hilite_system('<S3>/Kp') - opens and selects block Kp which resides in S3
 *
 * Here is the system hierarchy for this model
 *
 * '<Root>' : 'iir_filter_simulink'
 * '<S1>'   : 'iir_filter_simulink/Filter'
 */
#endif                                 /* iir_filter_simulink_h_ */

/*
 * File trailer for generated code.
 *
 * [EOF]
 */
