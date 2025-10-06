/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 * File: moving_avg.c
 *
 * MATLAB Coder version            : 25.2
 * C/C++ source code generated on  : 06-Oct-2025 08:12:02
 */

/* Include Files */
#include "moving_avg.h"
#include "conv.h"
#include "moving_avg_emxutil.h"
#include "moving_avg_types.h"
#include <math.h>

/* Function Declarations */
static double rt_roundd_snf(double u);

/* Function Definitions */
/*
 * Arguments    : double u
 * Return Type  : double
 */
static double rt_roundd_snf(double u)
{
  double y;
  if (fabs(u) < 4.503599627370496E+15) {
    if (u >= 0.5) {
      y = floor(u + 0.5);
    } else if (u > -0.5) {
      y = u * 0.0;
    } else {
      y = ceil(u - 0.5);
    }
  } else {
    y = u;
  }
  return y;
}

/*
 * Arguments    : unsigned short num_terms
 *                const emxArray_real_T *matrix_in
 *                emxArray_real_T *data_out
 * Return Type  : void
 */
void moving_avg(unsigned short num_terms, const emxArray_real_T *matrix_in,
                emxArray_real_T *data_out)
{
  emxArray_real_T *b_z;
  double d;
  double *z_data;
  int i;
  int loop_ub;
  unsigned short z;
  d = rt_roundd_snf(1.0 / (double)num_terms);
  if (d < 65536.0) {
    z = (unsigned short)d;
  } else {
    z = MAX_uint16_T;
  }
  emxInit_real_T(&b_z, 2);
  loop_ub = b_z->size[0] * b_z->size[1];
  b_z->size[0] = 1;
  b_z->size[1] = num_terms;
  emxEnsureCapacity_real_T(b_z, loop_ub);
  z_data = b_z->data;
  loop_ub = num_terms;
  for (i = 0; i < loop_ub; i++) {
    z_data[i] = z;
  }
  conv(b_z, matrix_in, data_out);
  emxFree_real_T(&b_z);
}

/*
 * File trailer for moving_avg.c
 *
 * [EOF]
 */
