/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 * File: moving_avg.c
 *
 * MATLAB Coder version            : 25.2
 * C/C++ source code generated on  : 03-Oct-2025 14:39:57
 */

/* Include Files */
#include "moving_avg.h"
#include "moving_avg_emxutil.h"
#include "moving_avg_types.h"
#include <stdio.h>

/* Function Definitions */
/*
 * Arguments    : double num_terms
 *                const double matrix_in[3000]
 *                emxArray_real_T *data_out
 * Return Type  : void
 */
void moving_avg(double num_terms, const double matrix_in[3000],
                emxArray_real_T *data_out)
{
  double cont;
  double sum;
  double *data_out_data;
  int b_i;
  int i;
  unsigned int j;
  int loop_ub;
  sum = 0.0;
  cont = 0.0;
  i = data_out->size[0] * data_out->size[1];
  data_out->size[0] = 1;
  loop_ub = (int)(1000.0 / num_terms);
  data_out->size[1] = loop_ub;
  emxEnsureCapacity_real_T(data_out, i);
  data_out_data = data_out->data;
  for (b_i = 0; b_i < loop_ub; b_i++) {
    data_out_data[b_i] = 0.0;
  }
  j = 0U;
  for (b_i = 0; b_i < 1000; b_i++) {
    sum += matrix_in[b_i];
    cont++;
    if (cont == num_terms) {
      cont = 0.0;
      j++;
      data_out_data[(int)j - 1] = sum / num_terms;
      sum = 0.0;
    }
  }
}

/*
 * File trailer for moving_avg.c
 *
 * [EOF]
 */
