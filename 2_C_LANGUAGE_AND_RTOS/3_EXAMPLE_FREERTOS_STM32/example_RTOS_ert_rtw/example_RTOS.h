/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * File: example_RTOS.h
 *
 * Code generated for Simulink model 'example_RTOS'.
 *
 * Model version                  : 1.5
 * Simulink Coder version         : 25.2 (R2025b) 28-Jul-2025
 * C/C++ source code generated on : Wed Oct  1 13:18:18 2025
 *
 * Target selection: ert.tlc
 * Embedded hardware selection: ARM Compatible->ARM Cortex-M
 * Code generation objectives: Unspecified
 * Validation result: Not run
 */

#ifndef example_RTOS_h_
#define example_RTOS_h_
#ifndef example_RTOS_COMMON_INCLUDES_
#define example_RTOS_COMMON_INCLUDES_
#include "rtwtypes.h"
#include "math.h"
#include "main.h"
#include "mw_stm32_utils.h"
#endif                                 /* example_RTOS_COMMON_INCLUDES_ */

#include "example_RTOS_types.h"
#include <stddef.h>

/* Macros for accessing real-time model data structure */
#ifndef rtmGetErrorStatus
#define rtmGetErrorStatus(rtm)         ((rtm)->errorStatus)
#endif

#ifndef rtmSetErrorStatus
#define rtmSetErrorStatus(rtm, val)    ((rtm)->errorStatus = (val))
#endif

#ifndef rtmStepTask
#define rtmStepTask(rtm, idx)          ((rtm)->Timing.TaskCounters.TID[(idx)] == 0)
#endif

#ifndef rtmTaskCounter
#define rtmTaskCounter(rtm, idx)       ((rtm)->Timing.TaskCounters.TID[(idx)])
#endif

/* Block states (default storage) for system '<Root>' */
typedef struct {
  stm32cube_blocks_DigitalPortW_T obj; /* '<S6>/Digital Port Write' */
  stm32cube_blocks_DigitalPortW_T obj_e;/* '<S4>/Digital Port Write' */
  int32_T clockTickCounter;            /* '<Root>/Discrete Pulse Generator' */
  int32_T clockTickCounter_n;          /* '<Root>/Discrete Pulse Generator1' */
} DW_example_RTOS_T;

/* Real-time Model Data Structure */
struct tag_RTM_example_RTOS_T {
  const char_T * volatile errorStatus;

  /*
   * Timing:
   * The following substructure contains information regarding
   * the timing information for the model.
   */
  struct {
    struct {
      uint8_T TID[2];
    } TaskCounters;
  } Timing;
};

/* Block states (default storage) */
extern DW_example_RTOS_T example_RTOS_DW;

/* External function called from main */
extern void example_RTOS_SetEventsForThisBaseStep(boolean_T *eventFlags);

/* Model entry point functions */
extern void example_RTOS_initialize(void);
extern void example_RTOS_step0(void);  /* Sample time: [0.05s, 0.0s] */
extern void example_RTOS_step1(void);  /* Sample time: [0.1s, 0.0s] */
extern void example_RTOS_terminate(void);

/* Real-time Model object */
extern RT_MODEL_example_RTOS_T *const example_RTOS_M;
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
 * '<Root>' : 'example_RTOS'
 * '<S1>'   : 'example_RTOS/Digital Port Write'
 * '<S2>'   : 'example_RTOS/Digital Port Write1'
 * '<S3>'   : 'example_RTOS/Digital Port Write/ECSoC'
 * '<S4>'   : 'example_RTOS/Digital Port Write/ECSoC/ECSimCodegen'
 * '<S5>'   : 'example_RTOS/Digital Port Write1/ECSoC'
 * '<S6>'   : 'example_RTOS/Digital Port Write1/ECSoC/ECSimCodegen'
 */
#endif                                 /* example_RTOS_h_ */

/*
 * File trailer for generated code.
 *
 * [EOF]
 */
