//
// Academic License - for use in teaching, academic research, and meeting
// course requirements at degree granting institutions only.  Not for
// government, commercial, or other organizational use.
//
// File: PID_simulink_example.cpp
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
#include "PID_simulink_example.h"
#include "rtwtypes.h"

// Model step function
void PID_simulink_example::step()
{
  real_T FilterDifferentiatorTF_tmp;
  real_T rtb_DerivativeGain;

  // DiscreteTransferFcn: '<S31>/Filter Differentiator TF' incorporates:
  //   Gain: '<S29>/Derivative Gain'
  //   Inport: '<Root>/In1'

  FilterDifferentiatorTF_tmp = 0.0007 * rtU.In1 - -0.090909090909090912 *
    rtDW.FilterDifferentiatorTF_states;

  // DiscreteIntegrator: '<S38>/Integrator' incorporates:
  //   Gain: '<S35>/Integral Gain'
  //   Inport: '<Root>/In1'

  rtb_DerivativeGain = 0.3 * rtU.In1 * 0.1 + rtDW.Integrator_DSTATE;

  // Outport: '<Root>/Out1' incorporates:
  //   DiscreteTransferFcn: '<S31>/Filter Differentiator TF'
  //   Gain: '<S41>/Filter Coefficient'
  //   Gain: '<S43>/Proportional Gain'
  //   Inport: '<Root>/In1'
  //   Product: '<S31>/DenCoefOut'
  //   Sum: '<S47>/Sum'

  rtY.Out1 = (FilterDifferentiatorTF_tmp - rtDW.FilterDifferentiatorTF_states) *
    0.090909090909090912 * 100.0 + (0.03 * rtU.In1 + rtb_DerivativeGain);

  // Update for DiscreteTransferFcn: '<S31>/Filter Differentiator TF'
  rtDW.FilterDifferentiatorTF_states = FilterDifferentiatorTF_tmp;

  // Update for DiscreteIntegrator: '<S38>/Integrator'
  rtDW.Integrator_DSTATE = rtb_DerivativeGain;
}

// Model initialize function
void PID_simulink_example::initialize()
{
  // (no initialization code required)
}

// Constructor
PID_simulink_example::PID_simulink_example():
  rtU(),
  rtY(),
  rtDW()
{
  // Currently there is no constructor body generated.
}

// Destructor
// Currently there is no destructor body generated.
PID_simulink_example::~PID_simulink_example() = default;

//
// File trailer for generated code.
//
// [EOF]
//
