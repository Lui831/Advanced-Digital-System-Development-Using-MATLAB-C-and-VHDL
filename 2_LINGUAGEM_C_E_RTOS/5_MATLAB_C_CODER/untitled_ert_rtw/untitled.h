/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * File: untitled.h
 *
 * Code generated for Simulink model 'untitled'.
 *
 * Model version                  : 1.0
 * Simulink Coder version         : 25.2 (R2025b) 28-Jul-2025
 * C/C++ source code generated on : Mon Oct  6 11:48:38 2025
 *
 * Target selection: ert.tlc
 * Embedded hardware selection: Intel->x86-64 (Windows64)
 * Code generation objectives:
 *    1. Execution efficiency
 *    2. RAM efficiency
 * Validation result: Not run
 */

#ifndef untitled_h_
#define untitled_h_
#ifndef untitled_COMMON_INCLUDES_
#define untitled_COMMON_INCLUDES_
#include "rtwtypes.h"
#include "rtw_continuous.h"
#include "rtw_solver.h"
#include "math.h"
#endif                                 /* untitled_COMMON_INCLUDES_ */

/* Macros for accessing real-time model data structure */
#ifndef rtmGetErrorStatus
#define rtmGetErrorStatus(rtm)         ((rtm)->errorStatus)
#endif

#ifndef rtmSetErrorStatus
#define rtmSetErrorStatus(rtm, val)    ((rtm)->errorStatus = (val))
#endif

#ifndef rtmGetT
#define rtmGetT(rtm)                   (rtmGetTPtr((rtm))[0])
#endif

#ifndef rtmGetTPtr
#define rtmGetTPtr(rtm)                ((rtm)->Timing.t)
#endif

/* Forward declaration for rtModel */
typedef struct tag_RTM RT_MODEL;

/* Real-time Model Data Structure */
struct tag_RTM {
  const char_T *errorStatus;
  RTWSolverInfo solverInfo;

  /*
   * Timing:
   * The following substructure contains information regarding
   * the timing information for the model.
   */
  struct {
    uint32_T clockTick0;
    time_T stepSize0;
    uint32_T clockTick1;
    SimTimeStep simTimeStep;
    time_T *t;
    time_T tArray[2];
  } Timing;
};

/* Model entry point functions */
extern void untitled_initialize(void);
extern void untitled_step(void);

/* Real-time Model object */
extern RT_MODEL *const rtM;

/*-
 * These blocks were eliminated from the model due to optimizations:
 *
 * Block '<S29>/Derivative Gain' : Unused code path elimination
 * Block '<S31>/Filter' : Unused code path elimination
 * Block '<S31>/SumD' : Unused code path elimination
 * Block '<S33>/Integral Gain' : Unused code path elimination
 * Block '<S36>/Integrator' : Unused code path elimination
 * Block '<S39>/Filter Coefficient' : Unused code path elimination
 * Block '<S41>/Proportional Gain' : Unused code path elimination
 * Block '<S45>/Sum' : Unused code path elimination
 * Block '<Root>/Scope' : Unused code path elimination
 * Block '<Root>/Step' : Unused code path elimination
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
 * '<Root>' : 'untitled'
 * '<S1>'   : 'untitled/Discrete PID Controller'
 * '<S2>'   : 'untitled/Discrete PID Controller/Anti-windup'
 * '<S3>'   : 'untitled/Discrete PID Controller/D Gain'
 * '<S4>'   : 'untitled/Discrete PID Controller/External Derivative'
 * '<S5>'   : 'untitled/Discrete PID Controller/Filter'
 * '<S6>'   : 'untitled/Discrete PID Controller/Filter ICs'
 * '<S7>'   : 'untitled/Discrete PID Controller/I Gain'
 * '<S8>'   : 'untitled/Discrete PID Controller/Ideal P Gain'
 * '<S9>'   : 'untitled/Discrete PID Controller/Ideal P Gain Fdbk'
 * '<S10>'  : 'untitled/Discrete PID Controller/Integrator'
 * '<S11>'  : 'untitled/Discrete PID Controller/Integrator ICs'
 * '<S12>'  : 'untitled/Discrete PID Controller/N Copy'
 * '<S13>'  : 'untitled/Discrete PID Controller/N Gain'
 * '<S14>'  : 'untitled/Discrete PID Controller/P Copy'
 * '<S15>'  : 'untitled/Discrete PID Controller/Parallel P Gain'
 * '<S16>'  : 'untitled/Discrete PID Controller/Reset Signal'
 * '<S17>'  : 'untitled/Discrete PID Controller/Saturation'
 * '<S18>'  : 'untitled/Discrete PID Controller/Saturation Fdbk'
 * '<S19>'  : 'untitled/Discrete PID Controller/Sum'
 * '<S20>'  : 'untitled/Discrete PID Controller/Sum Fdbk'
 * '<S21>'  : 'untitled/Discrete PID Controller/Tracking Mode'
 * '<S22>'  : 'untitled/Discrete PID Controller/Tracking Mode Sum'
 * '<S23>'  : 'untitled/Discrete PID Controller/Tsamp - Integral'
 * '<S24>'  : 'untitled/Discrete PID Controller/Tsamp - Ngain'
 * '<S25>'  : 'untitled/Discrete PID Controller/postSat Signal'
 * '<S26>'  : 'untitled/Discrete PID Controller/preInt Signal'
 * '<S27>'  : 'untitled/Discrete PID Controller/preSat Signal'
 * '<S28>'  : 'untitled/Discrete PID Controller/Anti-windup/Passthrough'
 * '<S29>'  : 'untitled/Discrete PID Controller/D Gain/Internal Parameters'
 * '<S30>'  : 'untitled/Discrete PID Controller/External Derivative/Error'
 * '<S31>'  : 'untitled/Discrete PID Controller/Filter/Disc. Forward Euler Filter'
 * '<S32>'  : 'untitled/Discrete PID Controller/Filter ICs/Internal IC - Filter'
 * '<S33>'  : 'untitled/Discrete PID Controller/I Gain/Internal Parameters'
 * '<S34>'  : 'untitled/Discrete PID Controller/Ideal P Gain/Passthrough'
 * '<S35>'  : 'untitled/Discrete PID Controller/Ideal P Gain Fdbk/Disabled'
 * '<S36>'  : 'untitled/Discrete PID Controller/Integrator/Discrete'
 * '<S37>'  : 'untitled/Discrete PID Controller/Integrator ICs/Internal IC'
 * '<S38>'  : 'untitled/Discrete PID Controller/N Copy/Disabled'
 * '<S39>'  : 'untitled/Discrete PID Controller/N Gain/Internal Parameters'
 * '<S40>'  : 'untitled/Discrete PID Controller/P Copy/Disabled'
 * '<S41>'  : 'untitled/Discrete PID Controller/Parallel P Gain/Internal Parameters'
 * '<S42>'  : 'untitled/Discrete PID Controller/Reset Signal/Disabled'
 * '<S43>'  : 'untitled/Discrete PID Controller/Saturation/Passthrough'
 * '<S44>'  : 'untitled/Discrete PID Controller/Saturation Fdbk/Disabled'
 * '<S45>'  : 'untitled/Discrete PID Controller/Sum/Sum_PID'
 * '<S46>'  : 'untitled/Discrete PID Controller/Sum Fdbk/Disabled'
 * '<S47>'  : 'untitled/Discrete PID Controller/Tracking Mode/Disabled'
 * '<S48>'  : 'untitled/Discrete PID Controller/Tracking Mode Sum/Passthrough'
 * '<S49>'  : 'untitled/Discrete PID Controller/Tsamp - Integral/TsSignalSpecification'
 * '<S50>'  : 'untitled/Discrete PID Controller/Tsamp - Ngain/Passthrough'
 * '<S51>'  : 'untitled/Discrete PID Controller/postSat Signal/Forward_Path'
 * '<S52>'  : 'untitled/Discrete PID Controller/preInt Signal/Internal PreInt'
 * '<S53>'  : 'untitled/Discrete PID Controller/preSat Signal/Forward_Path'
 */
#endif                                 /* untitled_h_ */

/*
 * File trailer for generated code.
 *
 * [EOF]
 */
