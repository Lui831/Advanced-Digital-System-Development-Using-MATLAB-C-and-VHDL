/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * File: example_RTOS.c
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

#include "example_RTOS.h"
#include "rtwtypes.h"

/* Block states (default storage) */
DW_example_RTOS_T example_RTOS_DW;

/* Real-time model */
static RT_MODEL_example_RTOS_T example_RTOS_M_;
RT_MODEL_example_RTOS_T *const example_RTOS_M = &example_RTOS_M_;
static void rate_monotonic_scheduler(void);

/*
 * Set which subrates need to run this base step (base rate always runs).
 * This function must be called prior to calling the model step function
 * in order to remember which rates need to run this base step.  The
 * buffering of events allows for overlapping preemption.
 */
void example_RTOS_SetEventsForThisBaseStep(boolean_T *eventFlags)
{
  /* Task runs when its counter is zero, computed via rtmStepTask macro */
  eventFlags[1] = ((boolean_T)rtmStepTask(example_RTOS_M, 1));
}

/*
 *         This function updates active task flag for each subrate
 *         and rate transition flags for tasks that exchange data.
 *         The function assumes rate-monotonic multitasking scheduler.
 *         The function must be called at model base rate so that
 *         the generated code self-manages all its subrates and rate
 *         transition flags.
 */
static void rate_monotonic_scheduler(void)
{
  /* Compute which subrates run during the next base time step.  Subrates
   * are an integer multiple of the base rate counter.  Therefore, the subtask
   * counter is reset when it reaches its limit (zero means run).
   */
  (example_RTOS_M->Timing.TaskCounters.TID[1])++;
  if ((example_RTOS_M->Timing.TaskCounters.TID[1]) > 1) {/* Sample time: [0.1s, 0.0s] */
    example_RTOS_M->Timing.TaskCounters.TID[1] = 0;
  }
}

/* Model step function for TID0 */
void example_RTOS_step0(void)          /* Sample time: [0.05s, 0.0s] */
{
  GPIO_TypeDef * portNameLoc;
  uint32_T shiftVal;
  int32_T rtb_DiscretePulseGenerator;
  uint32_T pinMask;
  uint32_T pinWriteLoc;

  {                                    /* Sample time: [0.05s, 0.0s] */
    rate_monotonic_scheduler();
  }

  /* DiscretePulseGenerator: '<Root>/Discrete Pulse Generator' */
  rtb_DiscretePulseGenerator = ((example_RTOS_DW.clockTickCounter < 5) &&
    (example_RTOS_DW.clockTickCounter >= 0));
  if (example_RTOS_DW.clockTickCounter >= 9) {
    example_RTOS_DW.clockTickCounter = 0;
  } else {
    example_RTOS_DW.clockTickCounter++;
  }

  /* End of DiscretePulseGenerator: '<Root>/Discrete Pulse Generator' */

  /* MATLABSystem: '<S4>/Digital Port Write' */
  portNameLoc = GPIOA;
  shiftVal = MW_GPIO_BIT_SHIFT;
  if (rtb_DiscretePulseGenerator != 0) {
    pinWriteLoc = 32U;
  } else {
    pinWriteLoc = 0U;
  }

  pinWriteLoc = mw_shift(pinWriteLoc, shiftVal);
  pinMask = mw_shift(32U, shiftVal);
  LL_GPIO_SetOutputPin(portNameLoc, pinWriteLoc);
  LL_GPIO_ResetOutputPin(portNameLoc, ~pinWriteLoc & pinMask);

  /* End of MATLABSystem: '<S4>/Digital Port Write' */
}

/* Model step function for TID1 */
void example_RTOS_step1(void)          /* Sample time: [0.1s, 0.0s] */
{
  GPIO_TypeDef * portNameLoc;
  uint32_T shiftVal;
  int32_T rtb_DiscretePulseGenerator1;
  uint32_T pinMask;
  uint32_T pinWriteLoc;

  /* DiscretePulseGenerator: '<Root>/Discrete Pulse Generator1' */
  rtb_DiscretePulseGenerator1 = ((example_RTOS_DW.clockTickCounter_n < 5) &&
    (example_RTOS_DW.clockTickCounter_n >= 0));
  if (example_RTOS_DW.clockTickCounter_n >= 9) {
    example_RTOS_DW.clockTickCounter_n = 0;
  } else {
    example_RTOS_DW.clockTickCounter_n++;
  }

  /* End of DiscretePulseGenerator: '<Root>/Discrete Pulse Generator1' */

  /* MATLABSystem: '<S6>/Digital Port Write' */
  portNameLoc = GPIOA;
  shiftVal = MW_GPIO_BIT_SHIFT;
  if (rtb_DiscretePulseGenerator1 != 0) {
    pinWriteLoc = 512U;
  } else {
    pinWriteLoc = 0U;
  }

  pinWriteLoc = mw_shift(pinWriteLoc, shiftVal);
  pinMask = mw_shift(512U, shiftVal);
  LL_GPIO_SetOutputPin(portNameLoc, pinWriteLoc);
  LL_GPIO_ResetOutputPin(portNameLoc, ~pinWriteLoc & pinMask);

  /* End of MATLABSystem: '<S6>/Digital Port Write' */
}

/* Model initialize function */
void example_RTOS_initialize(void)
{
  /* Start for MATLABSystem: '<S4>/Digital Port Write' */
  example_RTOS_DW.obj_e.matlabCodegenIsDeleted = false;
  example_RTOS_DW.obj_e.isInitialized = 1;
  example_RTOS_DW.obj_e.isSetupComplete = true;

  /* Start for MATLABSystem: '<S6>/Digital Port Write' */
  example_RTOS_DW.obj.matlabCodegenIsDeleted = false;
  example_RTOS_DW.obj.isInitialized = 1;
  example_RTOS_DW.obj.isSetupComplete = true;
}

/* Model terminate function */
void example_RTOS_terminate(void)
{
  /* Terminate for MATLABSystem: '<S4>/Digital Port Write' */
  if (!example_RTOS_DW.obj_e.matlabCodegenIsDeleted) {
    example_RTOS_DW.obj_e.matlabCodegenIsDeleted = true;
  }

  /* End of Terminate for MATLABSystem: '<S4>/Digital Port Write' */

  /* Terminate for MATLABSystem: '<S6>/Digital Port Write' */
  if (!example_RTOS_DW.obj.matlabCodegenIsDeleted) {
    example_RTOS_DW.obj.matlabCodegenIsDeleted = true;
  }

  /* End of Terminate for MATLABSystem: '<S6>/Digital Port Write' */
}

/*
 * File trailer for generated code.
 *
 * [EOF]
 */
