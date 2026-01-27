#ifndef INCLUDE_UART_H_
#define INCLUDE_UART_H_

#define U32_MAX_STRING 300
#define U32_MAX_DEVICE 6

#define U32_DR_MASK (0b111111 << 26)
#define U32_DR_COMPARE 0

#define INPUT_PARAMS_SIZE  5
#define OUTPUT_PARAMS_SIZE 5

void apbuartSendString(struct apbuart_priv *device, char strSend[U32_MAX_STRING]);
/* Função para enviar uma string pelo canal serial */

void apbuartReceiveString(struct apbuart_priv *device, char strReceive[U32_MAX_STRING], uint32_t cntrl, uint32_t stopnumBytes);
/* Função para receber uma string a partir do canal serial
 Para cntrl = 0, deve ser informado o número de bytes a serem recebidos a partir da variável stopnumBytes
 Para cntrl = 1, deve ser informado o stop byte da string a ser recebida a partir da variável stopnumBytes */

void apbtToApbtString(struct apbuart_priv *deviceSend, struct apbuart_priv *deviceRecv, char strSend[U32_MAX_STRING], char strRecv[U32_MAX_STRING]);
/* Função de envio e recebimento de strings entre duas APBUARTs */

int iFindChar(char str[U32_MAX_STRING], char chr);
/* Função utilizada para o "achamento" do índice de algum caractere em uma string. Utilizada na CipherCaesar */

float moving_average(float current_value);
/* Função que calcula a média móvel de um valor float*/

float string_to_float(const char *str);
/* Função que converte uma string para float */

void float_to_string(float value, char *str, int precision);
/* Função que converte um float para string com precisão especificada */

float iir_filter(float* input_params, float* output_params, float current_input_value);
/* Função que implementa um filtro IIR com parâmetros configuráveis */

#endif
