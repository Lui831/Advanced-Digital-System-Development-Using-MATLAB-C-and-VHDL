/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 * File: iir_filter.c
 *
 * MATLAB Coder version            : 25.1
 * C/C++ source code generated on  : 22-Jan-2026 19:21:49
 */

/* Include Files */
#include "iir_filter.h"
#include "filter.h"
#include "iir_filter_data.h"
#include "iir_filter_initialize.h"

/* Function Definitions */
/*
 * IIR_FILTER Aplica um filtro IIR passa-baixas a um sinal de entrada
 *
 *  Entrada:
 *    x - vetor de amostras do sinal de entrada
 *
 *  Saída:
 *    y - vetor de amostras do sinal filtrado
 *
 * Arguments    : const double x[1001]
 *                double y[1001]
 * Return Type  : void
 */
void iir_filter(const double x[1001], double y[1001])
{
  if (!isInitialized_iir_filter) {
    iir_filter_initialize();
  }
  /*  Coeficientes do filtro IIR (biquad passa-baixas) */
  /*  Aplicação do filtro */
  filter(x, y);
}

/*
 * File trailer for iir_filter.c
 *
 * [EOF]
 */
