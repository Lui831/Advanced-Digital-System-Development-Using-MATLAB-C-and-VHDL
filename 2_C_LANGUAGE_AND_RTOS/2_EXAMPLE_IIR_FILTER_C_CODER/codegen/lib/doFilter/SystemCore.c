/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 * File: SystemCore.c
 *
 * MATLAB Coder version            : 25.1
 * C/C++ source code generated on  : 22-Jan-2026 22:38:08
 */

/* Include Files */
#include "SystemCore.h"
#include "doFilter_internal_types.h"

/* Function Definitions */
/*
 * Arguments    : dsp_SOSFilter *obj
 *                const double varargin_1[1000]
 *                double varargout_1[1000]
 * Return Type  : void
 */
void SystemCore_step(dsp_SOSFilter *obj, const double varargin_1[1000],
                     double varargout_1[1000])
{
  double d;
  double d1;
  double d10;
  double d11;
  double d12;
  double d13;
  double d14;
  double d15;
  double d16;
  double d17;
  double d18;
  double d19;
  double d2;
  double d20;
  double d21;
  double d22;
  double d23;
  double d24;
  double d25;
  double d26;
  double d27;
  double d28;
  double d29;
  double d3;
  double d30;
  double d31;
  double d32;
  double d33;
  double d34;
  double d35;
  double d36;
  double d37;
  double d38;
  double d39;
  double d4;
  double d40;
  double d41;
  double d42;
  double d43;
  double d44;
  double d45;
  double d46;
  double d47;
  double d48;
  double d49;
  double d5;
  double d50;
  double d51;
  double d52;
  double d53;
  double d54;
  double d55;
  double d56;
  double d57;
  double d58;
  double d59;
  double d6;
  double d60;
  double d61;
  double d62;
  double d63;
  double d64;
  double d65;
  double d66;
  double d67;
  double d68;
  double d69;
  double d7;
  double d70;
  double d71;
  double d72;
  double d73;
  double d74;
  double d75;
  double d76;
  double d77;
  double d78;
  double d79;
  double d8;
  double d80;
  double d81;
  double d82;
  double d83;
  double d84;
  double d85;
  double d86;
  double d87;
  double d88;
  double d89;
  double d9;
  double d90;
  double d91;
  double d92;
  double d93;
  double d94;
  double d95;
  double d96;
  int i;
  /* System object Outputs function: dsp.SOSFilter */
  d = obj->cSFunObject.P3_RTP3COEFF[0];
  d1 = obj->cSFunObject.W0_FILT_STATES[0];
  d2 = obj->cSFunObject.P2_RTP2COEFF[12];
  d3 = obj->cSFunObject.W0_FILT_STATES[1];
  d4 = obj->cSFunObject.P2_RTP2COEFF[24];
  d5 = obj->cSFunObject.P1_RTP1COEFF[0];
  d6 = obj->cSFunObject.P1_RTP1COEFF[12];
  d7 = obj->cSFunObject.P1_RTP1COEFF[24];
  d8 = obj->cSFunObject.P3_RTP3COEFF[1];
  d9 = obj->cSFunObject.W0_FILT_STATES[2];
  d10 = obj->cSFunObject.P2_RTP2COEFF[13];
  d11 = obj->cSFunObject.W0_FILT_STATES[3];
  d12 = obj->cSFunObject.P2_RTP2COEFF[25];
  d13 = obj->cSFunObject.P1_RTP1COEFF[1];
  d14 = obj->cSFunObject.P1_RTP1COEFF[13];
  d15 = obj->cSFunObject.P1_RTP1COEFF[25];
  d16 = obj->cSFunObject.P3_RTP3COEFF[2];
  d17 = obj->cSFunObject.W0_FILT_STATES[4];
  d18 = obj->cSFunObject.P2_RTP2COEFF[14];
  d19 = obj->cSFunObject.W0_FILT_STATES[5];
  d20 = obj->cSFunObject.P2_RTP2COEFF[26];
  d21 = obj->cSFunObject.P1_RTP1COEFF[2];
  d22 = obj->cSFunObject.P1_RTP1COEFF[14];
  d23 = obj->cSFunObject.P1_RTP1COEFF[26];
  d24 = obj->cSFunObject.P3_RTP3COEFF[3];
  d25 = obj->cSFunObject.W0_FILT_STATES[6];
  d26 = obj->cSFunObject.P2_RTP2COEFF[15];
  d27 = obj->cSFunObject.W0_FILT_STATES[7];
  d28 = obj->cSFunObject.P2_RTP2COEFF[27];
  d29 = obj->cSFunObject.P1_RTP1COEFF[3];
  d30 = obj->cSFunObject.P1_RTP1COEFF[15];
  d31 = obj->cSFunObject.P1_RTP1COEFF[27];
  d32 = obj->cSFunObject.P3_RTP3COEFF[4];
  d33 = obj->cSFunObject.W0_FILT_STATES[8];
  d34 = obj->cSFunObject.P2_RTP2COEFF[16];
  d35 = obj->cSFunObject.W0_FILT_STATES[9];
  d36 = obj->cSFunObject.P2_RTP2COEFF[28];
  d37 = obj->cSFunObject.P1_RTP1COEFF[4];
  d38 = obj->cSFunObject.P1_RTP1COEFF[16];
  d39 = obj->cSFunObject.P1_RTP1COEFF[28];
  d40 = obj->cSFunObject.P3_RTP3COEFF[5];
  d41 = obj->cSFunObject.W0_FILT_STATES[10];
  d42 = obj->cSFunObject.P2_RTP2COEFF[17];
  d43 = obj->cSFunObject.W0_FILT_STATES[11];
  d44 = obj->cSFunObject.P2_RTP2COEFF[29];
  d45 = obj->cSFunObject.P1_RTP1COEFF[5];
  d46 = obj->cSFunObject.P1_RTP1COEFF[17];
  d47 = obj->cSFunObject.P1_RTP1COEFF[29];
  d48 = obj->cSFunObject.P3_RTP3COEFF[6];
  d49 = obj->cSFunObject.W0_FILT_STATES[12];
  d50 = obj->cSFunObject.P2_RTP2COEFF[18];
  d51 = obj->cSFunObject.W0_FILT_STATES[13];
  d52 = obj->cSFunObject.P2_RTP2COEFF[30];
  d53 = obj->cSFunObject.P1_RTP1COEFF[6];
  d54 = obj->cSFunObject.P1_RTP1COEFF[18];
  d55 = obj->cSFunObject.P1_RTP1COEFF[30];
  d56 = obj->cSFunObject.P3_RTP3COEFF[7];
  d57 = obj->cSFunObject.W0_FILT_STATES[14];
  d58 = obj->cSFunObject.P2_RTP2COEFF[19];
  d59 = obj->cSFunObject.W0_FILT_STATES[15];
  d60 = obj->cSFunObject.P2_RTP2COEFF[31];
  d61 = obj->cSFunObject.P1_RTP1COEFF[7];
  d62 = obj->cSFunObject.P1_RTP1COEFF[19];
  d63 = obj->cSFunObject.P1_RTP1COEFF[31];
  d64 = obj->cSFunObject.P3_RTP3COEFF[8];
  d65 = obj->cSFunObject.W0_FILT_STATES[16];
  d66 = obj->cSFunObject.P2_RTP2COEFF[20];
  d67 = obj->cSFunObject.W0_FILT_STATES[17];
  d68 = obj->cSFunObject.P2_RTP2COEFF[32];
  d69 = obj->cSFunObject.P1_RTP1COEFF[8];
  d70 = obj->cSFunObject.P1_RTP1COEFF[20];
  d71 = obj->cSFunObject.P1_RTP1COEFF[32];
  d72 = obj->cSFunObject.P3_RTP3COEFF[9];
  d73 = obj->cSFunObject.W0_FILT_STATES[18];
  d74 = obj->cSFunObject.P2_RTP2COEFF[21];
  d75 = obj->cSFunObject.W0_FILT_STATES[19];
  d76 = obj->cSFunObject.P2_RTP2COEFF[33];
  d77 = obj->cSFunObject.P1_RTP1COEFF[9];
  d78 = obj->cSFunObject.P1_RTP1COEFF[21];
  d79 = obj->cSFunObject.P1_RTP1COEFF[33];
  d80 = obj->cSFunObject.P3_RTP3COEFF[10];
  d81 = obj->cSFunObject.W0_FILT_STATES[20];
  d82 = obj->cSFunObject.P2_RTP2COEFF[22];
  d83 = obj->cSFunObject.W0_FILT_STATES[21];
  d84 = obj->cSFunObject.P2_RTP2COEFF[34];
  d85 = obj->cSFunObject.P1_RTP1COEFF[10];
  d86 = obj->cSFunObject.P1_RTP1COEFF[22];
  d87 = obj->cSFunObject.P1_RTP1COEFF[34];
  d88 = obj->cSFunObject.P3_RTP3COEFF[11];
  d89 = obj->cSFunObject.W0_FILT_STATES[22];
  d90 = obj->cSFunObject.P2_RTP2COEFF[23];
  d91 = obj->cSFunObject.W0_FILT_STATES[23];
  d92 = obj->cSFunObject.P2_RTP2COEFF[35];
  d93 = obj->cSFunObject.P1_RTP1COEFF[11];
  d94 = obj->cSFunObject.P1_RTP1COEFF[23];
  d95 = obj->cSFunObject.P1_RTP1COEFF[35];
  d96 = obj->cSFunObject.P3_RTP3COEFF[12];
  for (i = 0; i < 1000; i++) {
    double stageOut;
    double tmpState;
    tmpState = (d * varargin_1[i] - d1 * d2) - d3 * d4;
    stageOut = (d5 * tmpState + d1 * d6) + d3 * d7;
    d3 = d1;
    d1 = tmpState;
    tmpState = (d8 * stageOut - d9 * d10) - d11 * d12;
    stageOut = (d13 * tmpState + d9 * d14) + d11 * d15;
    d11 = d9;
    d9 = tmpState;
    tmpState = (d16 * stageOut - d17 * d18) - d19 * d20;
    stageOut = (d21 * tmpState + d17 * d22) + d19 * d23;
    d19 = d17;
    d17 = tmpState;
    tmpState = (d24 * stageOut - d25 * d26) - d27 * d28;
    stageOut = (d29 * tmpState + d25 * d30) + d27 * d31;
    d27 = d25;
    d25 = tmpState;
    tmpState = (d32 * stageOut - d33 * d34) - d35 * d36;
    stageOut = (d37 * tmpState + d33 * d38) + d35 * d39;
    d35 = d33;
    d33 = tmpState;
    tmpState = (d40 * stageOut - d41 * d42) - d43 * d44;
    stageOut = (d45 * tmpState + d41 * d46) + d43 * d47;
    d43 = d41;
    d41 = tmpState;
    tmpState = (d48 * stageOut - d49 * d50) - d51 * d52;
    stageOut = (d53 * tmpState + d49 * d54) + d51 * d55;
    d51 = d49;
    d49 = tmpState;
    tmpState = (d56 * stageOut - d57 * d58) - d59 * d60;
    stageOut = (d61 * tmpState + d57 * d62) + d59 * d63;
    d59 = d57;
    d57 = tmpState;
    tmpState = (d64 * stageOut - d65 * d66) - d67 * d68;
    stageOut = (d69 * tmpState + d65 * d70) + d67 * d71;
    d67 = d65;
    d65 = tmpState;
    tmpState = (d72 * stageOut - d73 * d74) - d75 * d76;
    stageOut = (d77 * tmpState + d73 * d78) + d75 * d79;
    d75 = d73;
    d73 = tmpState;
    tmpState = (d80 * stageOut - d81 * d82) - d83 * d84;
    stageOut = (d85 * tmpState + d81 * d86) + d83 * d87;
    d83 = d81;
    d81 = tmpState;
    tmpState = (d88 * stageOut - d89 * d90) - d91 * d92;
    stageOut = (d93 * tmpState + d89 * d94) + d91 * d95;
    d91 = d89;
    d89 = tmpState;
    varargout_1[i] = d96 * stageOut;
  }
  obj->cSFunObject.W0_FILT_STATES[23] = d91;
  obj->cSFunObject.W0_FILT_STATES[22] = d89;
  obj->cSFunObject.W0_FILT_STATES[21] = d83;
  obj->cSFunObject.W0_FILT_STATES[20] = d81;
  obj->cSFunObject.W0_FILT_STATES[19] = d75;
  obj->cSFunObject.W0_FILT_STATES[18] = d73;
  obj->cSFunObject.W0_FILT_STATES[17] = d67;
  obj->cSFunObject.W0_FILT_STATES[16] = d65;
  obj->cSFunObject.W0_FILT_STATES[15] = d59;
  obj->cSFunObject.W0_FILT_STATES[14] = d57;
  obj->cSFunObject.W0_FILT_STATES[13] = d51;
  obj->cSFunObject.W0_FILT_STATES[12] = d49;
  obj->cSFunObject.W0_FILT_STATES[11] = d43;
  obj->cSFunObject.W0_FILT_STATES[10] = d41;
  obj->cSFunObject.W0_FILT_STATES[9] = d35;
  obj->cSFunObject.W0_FILT_STATES[8] = d33;
  obj->cSFunObject.W0_FILT_STATES[7] = d27;
  obj->cSFunObject.W0_FILT_STATES[6] = d25;
  obj->cSFunObject.W0_FILT_STATES[5] = d19;
  obj->cSFunObject.W0_FILT_STATES[4] = d17;
  obj->cSFunObject.W0_FILT_STATES[3] = d11;
  obj->cSFunObject.W0_FILT_STATES[2] = d9;
  obj->cSFunObject.W0_FILT_STATES[1] = d3;
  obj->cSFunObject.W0_FILT_STATES[0] = d1;
}

/*
 * File trailer for SystemCore.c
 *
 * [EOF]
 */
