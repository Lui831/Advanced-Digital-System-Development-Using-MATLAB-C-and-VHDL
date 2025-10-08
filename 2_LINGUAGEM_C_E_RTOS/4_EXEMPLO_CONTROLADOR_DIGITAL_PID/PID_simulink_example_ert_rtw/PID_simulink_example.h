//
// Academic License - for use in teaching, academic research, and meeting
// course requirements at degree granting institutions only.  Not for
// government, commercial, or other organizational use.
//
// File: PID_simulink_example.h
//
// Code generated for Simulink model 'PID_simulink_example'.
//
// Model version                  : 1.7
// Simulink Coder version         : 25.2 (R2025b) 28-Jul-2025
// C/C++ source code generated on : Wed Oct  8 07:31:24 2025
//
// Target selection: ert.tlc
// Embedded hardware selection: Intel->x86-64 (Windows64)
// Code generation objectives:
//    1. Execution efficiency
//    2. RAM efficiency
// Validation result: Not run
//
#ifndef PID_simulink_example_h_
#define PID_simulink_example_h_
#include <cmath>
#include "rtwtypes.h"

// Class declaration for model PID_simulink_example
class PID_simulink_example final
{
  // public data and function members
 public:
  // Block signals and states (default storage) for system '<Root>'
  struct DW {
    real_T FilterDifferentiatorTF_states;// '<S31>/Filter Differentiator TF'
    real_T Integrator_DSTATE;          // '<S38>/Integrator'
  };

  // External inputs (root inport signals with default storage)
  struct ExtU {
    real_T In1;                        // '<Root>/In1'
  };

  // External outputs (root outports fed by signals with default storage)
  struct ExtY {
    real_T Out1;                       // '<Root>/Out1'
  };

  // Copy Constructor
  PID_simulink_example(PID_simulink_example const&) = delete;

  // Assignment Operator
  PID_simulink_example& operator= (PID_simulink_example const&) & = delete;

  // Move Constructor
  PID_simulink_example(PID_simulink_example &&) = delete;

  // Move Assignment Operator
  PID_simulink_example& operator= (PID_simulink_example &&) = delete;

  // External inputs
  ExtU rtU;

  // External outputs
  ExtY rtY;

  // model initialize function
  static void initialize();

  // model step function
  void step();

  // Constructor
  PID_simulink_example();

  // Destructor
  ~PID_simulink_example();

  // private data and function members
 private:
  // Block states
  DW rtDW;
};

//-
//  These blocks were eliminated from the model due to optimizations:
//
//  Block '<S31>/Passthrough for tuning' : Eliminate redundant data type conversion


//-
//  The generated code includes comments that allow you to trace directly
//  back to the appropriate location in the model.  The basic format
//  is <system>/block_name, where system is the system number (uniquely
//  assigned by Simulink) and block_name is the name of the block.
//
//  Use the MATLAB hilite_system command to trace the generated code back
//  to the model.  For example,
//
//  hilite_system('<S3>')    - opens system 3
//  hilite_system('<S3>/Kp') - opens and selects block Kp which resides in S3
//
//  Here is the system hierarchy for this model
//
//  '<Root>' : 'PID_simulink_example'
//  '<S1>'   : 'PID_simulink_example/Discrete PID Controller1'
//  '<S2>'   : 'PID_simulink_example/Discrete PID Controller1/Anti-windup'
//  '<S3>'   : 'PID_simulink_example/Discrete PID Controller1/D Gain'
//  '<S4>'   : 'PID_simulink_example/Discrete PID Controller1/External Derivative'
//  '<S5>'   : 'PID_simulink_example/Discrete PID Controller1/Filter'
//  '<S6>'   : 'PID_simulink_example/Discrete PID Controller1/Filter ICs'
//  '<S7>'   : 'PID_simulink_example/Discrete PID Controller1/I Gain'
//  '<S8>'   : 'PID_simulink_example/Discrete PID Controller1/Ideal P Gain'
//  '<S9>'   : 'PID_simulink_example/Discrete PID Controller1/Ideal P Gain Fdbk'
//  '<S10>'  : 'PID_simulink_example/Discrete PID Controller1/Integrator'
//  '<S11>'  : 'PID_simulink_example/Discrete PID Controller1/Integrator ICs'
//  '<S12>'  : 'PID_simulink_example/Discrete PID Controller1/N Copy'
//  '<S13>'  : 'PID_simulink_example/Discrete PID Controller1/N Gain'
//  '<S14>'  : 'PID_simulink_example/Discrete PID Controller1/P Copy'
//  '<S15>'  : 'PID_simulink_example/Discrete PID Controller1/Parallel P Gain'
//  '<S16>'  : 'PID_simulink_example/Discrete PID Controller1/Reset Signal'
//  '<S17>'  : 'PID_simulink_example/Discrete PID Controller1/Saturation'
//  '<S18>'  : 'PID_simulink_example/Discrete PID Controller1/Saturation Fdbk'
//  '<S19>'  : 'PID_simulink_example/Discrete PID Controller1/Sum'
//  '<S20>'  : 'PID_simulink_example/Discrete PID Controller1/Sum Fdbk'
//  '<S21>'  : 'PID_simulink_example/Discrete PID Controller1/Tracking Mode'
//  '<S22>'  : 'PID_simulink_example/Discrete PID Controller1/Tracking Mode Sum'
//  '<S23>'  : 'PID_simulink_example/Discrete PID Controller1/Tsamp - Integral'
//  '<S24>'  : 'PID_simulink_example/Discrete PID Controller1/Tsamp - Ngain'
//  '<S25>'  : 'PID_simulink_example/Discrete PID Controller1/postSat Signal'
//  '<S26>'  : 'PID_simulink_example/Discrete PID Controller1/preInt Signal'
//  '<S27>'  : 'PID_simulink_example/Discrete PID Controller1/preSat Signal'
//  '<S28>'  : 'PID_simulink_example/Discrete PID Controller1/Anti-windup/Passthrough'
//  '<S29>'  : 'PID_simulink_example/Discrete PID Controller1/D Gain/Internal Parameters'
//  '<S30>'  : 'PID_simulink_example/Discrete PID Controller1/External Derivative/Error'
//  '<S31>'  : 'PID_simulink_example/Discrete PID Controller1/Filter/Disc. Backward Euler Filter'
//  '<S32>'  : 'PID_simulink_example/Discrete PID Controller1/Filter/Disc. Backward Euler Filter/Tsamp'
//  '<S33>'  : 'PID_simulink_example/Discrete PID Controller1/Filter/Disc. Backward Euler Filter/Tsamp/Internal Ts'
//  '<S34>'  : 'PID_simulink_example/Discrete PID Controller1/Filter ICs/Internal IC - Filter'
//  '<S35>'  : 'PID_simulink_example/Discrete PID Controller1/I Gain/Internal Parameters'
//  '<S36>'  : 'PID_simulink_example/Discrete PID Controller1/Ideal P Gain/Passthrough'
//  '<S37>'  : 'PID_simulink_example/Discrete PID Controller1/Ideal P Gain Fdbk/Disabled'
//  '<S38>'  : 'PID_simulink_example/Discrete PID Controller1/Integrator/Discrete'
//  '<S39>'  : 'PID_simulink_example/Discrete PID Controller1/Integrator ICs/Internal IC'
//  '<S40>'  : 'PID_simulink_example/Discrete PID Controller1/N Copy/Internal Parameters'
//  '<S41>'  : 'PID_simulink_example/Discrete PID Controller1/N Gain/Internal Parameters'
//  '<S42>'  : 'PID_simulink_example/Discrete PID Controller1/P Copy/Disabled'
//  '<S43>'  : 'PID_simulink_example/Discrete PID Controller1/Parallel P Gain/Internal Parameters'
//  '<S44>'  : 'PID_simulink_example/Discrete PID Controller1/Reset Signal/Disabled'
//  '<S45>'  : 'PID_simulink_example/Discrete PID Controller1/Saturation/Passthrough'
//  '<S46>'  : 'PID_simulink_example/Discrete PID Controller1/Saturation Fdbk/Disabled'
//  '<S47>'  : 'PID_simulink_example/Discrete PID Controller1/Sum/Sum_PID'
//  '<S48>'  : 'PID_simulink_example/Discrete PID Controller1/Sum Fdbk/Disabled'
//  '<S49>'  : 'PID_simulink_example/Discrete PID Controller1/Tracking Mode/Disabled'
//  '<S50>'  : 'PID_simulink_example/Discrete PID Controller1/Tracking Mode Sum/Passthrough'
//  '<S51>'  : 'PID_simulink_example/Discrete PID Controller1/Tsamp - Integral/TsSignalSpecification'
//  '<S52>'  : 'PID_simulink_example/Discrete PID Controller1/Tsamp - Ngain/Passthrough'
//  '<S53>'  : 'PID_simulink_example/Discrete PID Controller1/postSat Signal/Forward_Path'
//  '<S54>'  : 'PID_simulink_example/Discrete PID Controller1/preInt Signal/Internal PreInt'
//  '<S55>'  : 'PID_simulink_example/Discrete PID Controller1/preSat Signal/Forward_Path'

#endif                                 // PID_simulink_example_h_

//
// File trailer for generated code.
//
// [EOF]
//
