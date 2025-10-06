/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 * File: conv.c
 *
 * MATLAB Coder version            : 25.2
 * C/C++ source code generated on  : 06-Oct-2025 08:12:02
 */

/* Include Files */
#include "conv.h"
#include "moving_avg_emxutil.h"
#include "moving_avg_types.h"
#include <emmintrin.h>

/* Function Definitions */
/*
 * Arguments    : const emxArray_real_T *A
 *                const emxArray_real_T *B
 *                emxArray_real_T *C
 * Return Type  : void
 */
void conv(const emxArray_real_T *A, const emxArray_real_T *B,
          emxArray_real_T *C)
{
  const double *A_data;
  const double *B_data;
  double *C_data;
  int C_tmp;
  int b_k;
  int k;
  int nA;
  int nApnB;
  int nB;
  B_data = B->data;
  A_data = A->data;
  nA = A->size[1] - 1;
  nB = B->size[1] - 1;
  nApnB = A->size[1] + B->size[1];
  if ((A->size[1] != 0) && (B->size[1] != 0)) {
    nApnB--;
  }
  C_tmp = C->size[0] * C->size[1];
  C->size[0] = 1;
  C->size[1] = nApnB;
  emxEnsureCapacity_real_T(C, C_tmp);
  C_data = C->data;
  for (k = 0; k < nApnB; k++) {
    C_data[k] = 0.0;
  }
  if ((A->size[1] > 0) && (B->size[1] > 0)) {
    if (B->size[1] > A->size[1]) {
      int vectorUB;
      nApnB = (B->size[1] / 2) << 1;
      vectorUB = nApnB - 2;
      for (k = 0; k <= nA; k++) {
        for (b_k = 0; b_k <= vectorUB; b_k += 2) {
          __m128d r;
          C_tmp = k + b_k;
          r = _mm_loadu_pd(&C_data[C_tmp]);
          _mm_storeu_pd(&C_data[C_tmp],
                        _mm_add_pd(r, _mm_mul_pd(_mm_set1_pd(A_data[k]),
                                                 _mm_loadu_pd(&B_data[b_k]))));
        }
        for (b_k = nApnB; b_k <= nB; b_k++) {
          C_tmp = k + b_k;
          C_data[C_tmp] += A_data[k] * B_data[b_k];
        }
      }
    } else {
      int vectorUB;
      C_tmp = (A->size[1] / 2) << 1;
      vectorUB = C_tmp - 2;
      for (k = 0; k <= nB; k++) {
        for (b_k = 0; b_k <= vectorUB; b_k += 2) {
          __m128d r;
          nApnB = k + b_k;
          r = _mm_loadu_pd(&C_data[nApnB]);
          _mm_storeu_pd(&C_data[nApnB],
                        _mm_add_pd(r, _mm_mul_pd(_mm_set1_pd(B_data[k]),
                                                 _mm_loadu_pd(&A_data[b_k]))));
        }
        for (b_k = C_tmp; b_k <= nA; b_k++) {
          nApnB = k + b_k;
          C_data[nApnB] += B_data[k] * A_data[b_k];
        }
      }
    }
  }
}

/*
 * File trailer for conv.c
 *
 * [EOF]
 */
