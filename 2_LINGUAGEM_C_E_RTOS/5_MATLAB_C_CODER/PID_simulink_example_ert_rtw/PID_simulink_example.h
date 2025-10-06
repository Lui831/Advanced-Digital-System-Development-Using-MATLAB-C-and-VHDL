/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * File: PID_simulink_example.h
 *
 * Code generated for Simulink model 'PID_simulink_example'.
 *
 * Model version                  : 1.2
 * Simulink Coder version         : 25.2 (R2025b) 28-Jul-2025
 * C/C++ source code generated on : Mon Oct  6 14:49:22 2025
 *
 * Target selection: ert.tlc
 * Embedded hardware selection: Intel->x86-64 (Windows64)
 * Code generation objectives:
 *    1. Execution efficiency
 *    2. RAM efficiency
 * Validation result: Not run
 */

#ifndef PID_simulink_example_h_
#define PID_simulink_example_h_
#ifndef PID_simulink_example_COMMON_INCLUDES_
#define PID_simulink_example_COMMON_INCLUDES_
#include "rtwtypes.h"
#include "rtw_continuous.h"
#include "rtw_solver.h"
#include "math.h"
#endif                               /* PID_simulink_example_COMMON_INCLUDES_ */

/* Macros for accessing real-time model data structure */
#ifndef rtmGetErrorStatus
#define rtmGetErrorStatus(rtm)         ((rtm)->errorStatus)
#endif

#ifndef rtmSetErrorStatus
#define rtmSetErrorStatus(rtm, val)    ((rtm)->errorStatus = (val))
#endif

/* Forward declaration for rtModel */
typedef struct tag_RTM RT_MODEL;

/* Real-time Model Data Structure */
struct tag_RTM {
  const char_T * volatile errorStatus;
};

/* Model entry point functions */
extern void PID_simulink_example_initialize(void);
extern void PID_simulink_example_step(void);

/* Real-time Model object */
extern RT_MODEL *const rtM;

/*-
 * These blocks were eliminated from the model due to optimizations:
 *
 * Block '<Root>/Discrete Zero-Pole' : Unused code path elimination
 * Block '<S29>/Derivative Gain' : Unused code path elimination
 * Block '<S31>/DenCoefOut' : Unused code path elimination
 * Block '<S31>/Filter Den Constant' : Unused code path elimination
 * Block '<S31>/Filter Differentiator TF' : Unused code path elimination
 * Block '<S31>/Passthrough for tuning' : Unused code path elimination
 * Block '<S31>/Reciprocal' : Unused code path elimination
 * Block '<S31>/SumDen' : Unused code path elimination
 * Block '<S33>/Tsamp' : Unused code path elimination
 * Block '<S31>/Unary Minus' : Unused code path elimination
 * Block '<S35>/Integral Gain' : Unused code path elimination
 * Block '<S38>/Integrator' : Unused code path elimination
 * Block '<S40>/N Copy' : Unused code path elimination
 * Block '<S41>/Filter Coefficient' : Unused code path elimination
 * Block '<S43>/Proportional Gain' : Unused code path elimination
 * Block '<S47>/Sum' : Unused code path elimination
 * Block '<Root>/Scope' : Unused code path elimination
 * Block '<Root>/Step' : Unused code path elimination
 * Block '<Root>/Sum' : Unused code path elimination
 * Block '<Root>/To Workspace' : Unused code path elimination
 */

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
 * '<Root>' : 'PID_simulink_example'
 * '<S1>'   : 'PID_simulink_example/Discrete PID Controller'
 * '<S2>'   : 'PID_simulink_example/Discrete PID Controller/Anti-windup'
 * '<S3>'   : 'PID_simulink_example/Discrete PID Controller/D Gain'
 * '<S4>'   : 'PID_simulink_example/Discrete PID Controller/External Derivative'
 * '<S5>'   : 'PID_simulink_example/Discrete PID Controller/Filter'
 * '<S6>'   : 'PID_simulink_example/Discrete PID Controller/Filter ICs'
 * '<S7>'   : 'PID_simulink_example/Discrete PID Controller/I Gain'
 * '<S8>'   : 'PID_simulink_example/Discrete PID Controller/Ideal P Gain'
 * '<S9>'   : 'PID_simulink_example/Discrete PID Controller/Ideal P Gain Fdbk'
 * '<S10>'  : 'PID_simulink_example/Discrete PID Controller/Integrator'
 * '<S11>'  : 'PID_simulink_example/Discrete PID Controller/Integrator ICs'
 * '<S12>'  : 'PID_simulink_example/Discrete PID Controller/N Copy'
 * '<S13>'  : 'PID_simulink_example/Discrete PID Controller/N Gain'
 * '<S14>'  : 'PID_simulink_example/Discrete PID Controller/P Copy'
 * '<S15>'  : 'PID_simulink_example/Discrete PID Controller/Parallel P Gain'
 * '<S16>'  : 'PID_simulink_example/Discrete PID Controller/Reset Signal'
 * '<S17>'  : 'PID_simulink_example/Discrete PID Controller/Saturation'
 * '<S18>'  : 'PID_simulink_example/Discrete PID Controller/Saturation Fdbk'
 * '<S19>'  : 'PID_simulink_example/Discrete PID Controller/Sum'
 * '<S20>'  : 'PID_simulink_example/Discrete PID Controller/Sum Fdbk'
 * '<S21>'  : 'PID_simulink_example/Discrete PID Controller/Tracking Mode'
 * '<S22>'  : 'PID_simulink_example/Discrete PID Controller/Tracking Mode Sum'
 * '<S23>'  : 'PID_simulink_example/Discrete PID Controller/Tsamp - Integral'
 * '<S24>'  : 'PID_simulink_example/Discrete PID Controller/Tsamp - Ngain'
 * '<S25>'  : 'PID_simulink_example/Discrete PID Controller/postSat Signal'
 * '<S26>'  : 'PID_simulink_example/Discrete PID Controller/preInt Signal'
 * '<S27>'  : 'PID_simulink_example/Discrete PID Controller/preSat Signal'
 * '<S28>'  : 'PID_simulink_example/Discrete PID Controller/Anti-windup/Passthrough'
 * '<S29>'  : 'PID_simulink_example/Discrete PID Controller/D Gain/Internal Parameters'
 * '<S30>'  : 'PID_simulink_example/Discrete PID Controller/External Derivative/Error'
 * '<S31>'  : 'PID_simulink_example/Discrete PID Controller/Filter/Disc. Backward Euler Filter'
 * '<S32>'  : 'PID_simulink_example/Discrete PID Controller/Filter/Disc. Backward Euler Filter/Tsamp'
 * '<S33>'  : 'PID_simulink_example/Discrete PID Controller/Filter/Disc. Backward Euler Filter/Tsamp/Internal Ts'
 * '<S34>'  : 'PID_simulink_example/Discrete PID Controller/Filter ICs/Internal IC - Filter'
 * '<S35>'  : 'PID_simulink_example/Discrete PID Controller/I Gain/Internal Parameters'
 * '<S36>'  : 'PID_simulink_example/Discrete PID Controller/Ideal P Gain/Passthrough'
 * '<S37>'  : 'PID_simulink_example/Discrete PID Controller/Ideal P Gain Fdbk/Disabled'
 * '<S38>'  : 'PID_simulink_example/Discrete PID Controller/Integrator/Discrete'
 * '<S39>'  : 'PID_simulink_example/Discrete PID Controller/Integrator ICs/Internal IC'
 * '<S40>'  : 'PID_simulink_example/Discrete PID Controller/N Copy/Internal Parameters'
 * '<S41>'  : 'PID_simulink_example/Discrete PID Controller/N Gain/Internal Parameters'
 * '<S42>'  : 'PID_simulink_example/Discrete PID Controller/P Copy/Disabled'
 * '<S43>'  : 'PID_simulink_example/Discrete PID Controller/Parallel P Gain/Internal Parameters'
 * '<S44>'  : 'PID_simulink_example/Discrete PID Controller/Reset Signal/Disabled'
 * '<S45>'  : 'PID_simulink_example/Discrete PID Controller/Saturation/Passthrough'
 * '<S46>'  : 'PID_simulink_example/Discrete PID Controller/Saturation Fdbk/Disabled'
 * '<S47>'  : 'PID_simulink_example/Discrete PID Controller/Sum/Sum_PID'
 * '<S48>'  : 'PID_simulink_example/Discrete PID Controller/Sum Fdbk/Disabled'
 * '<S49>'  : 'PID_simulink_example/Discrete PID Controller/Tracking Mode/Disabled'
 * '<S50>'  : 'PID_simulink_example/Discrete PID Controller/Tracking Mode Sum/Passthrough'
 * '<S51>'  : 'PID_simulink_example/Discrete PID Controller/Tsamp - Integral/TsSignalSpecification'
 * '<S52>'  : 'PID_simulink_example/Discrete PID Controller/Tsamp - Ngain/Passthrough'
 * '<S53>'  : 'PID_simulink_example/Discrete PID Controller/postSat Signal/Forward_Path'
 * '<S54>'  : 'PID_simulink_example/Discrete PID Controller/preInt Signal/Internal PreInt'
 * '<S55>'  : 'PID_simulink_example/Discrete PID Controller/preSat Signal/Forward_Path'
 */
#endif                                 /* PID_simulink_example_h_ */

/*
 * File trailer for generated code.
 *
 * [EOF]
 */
