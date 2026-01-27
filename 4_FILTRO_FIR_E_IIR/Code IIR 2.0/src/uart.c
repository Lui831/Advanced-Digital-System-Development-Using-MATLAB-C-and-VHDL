#include <stdio.h>
#include <drv/apbuart.h>
#include "include/uart.h"
#include <string.h>

#define INPUT_PARAMS_SIZE  5
#define OUTPUT_PARAMS_SIZE 5

void apbuartSendString(struct apbuart_priv *device, char strSend[U32_MAX_STRING]){

/* Inicializa as variáveis */

	uint32_t strLen, cont, confirm, statsRegister;
	const uint32_t mask = (1 << 1) | (1 << 2);

/* Contabiliza o número de bytes da string */

	strLen = strlen(strSend);

/* Realiza um laço de repetição para envio de byte a byte */

	for(cont = 0 ;cont < strLen;cont++){

          confirm = 0;

/* Enquanto o byte não for enviado, continua no laço de repetição*/

          while(confirm != 1){
			
			 confirm = apbuart_outbyte(device, strSend[cont]);
			 
			 }

	}

}

void apbuartReceiveString(struct apbuart_priv *device, char strReceive[U32_MAX_STRING], uint32_t cntrl, uint32_t stopnumBytes){

/* Inicializa as variáveis */

	uint32_t cont = 0, statsRegister;
	int32_t confirm;
    const uint32_t mask = (0b111111 << 26);

    strcpy(strReceive, "");

/* Dita a maneira de recebimento da string a partir da variável 'control' */

	switch(cntrl){

/* Para o caso 0, limita o recebimento da string pelo número de bytes informado */

	  case 0:

	     	for(cont=0;cont < stopnumBytes;cont++){

          	  confirm = -1;

/* Enquanto não recebe o byte, continua no laço de repetição*/

          	  while(confirm == -1){

          		 confirm = apbuart_inbyte(device);

          	  }

/* Adiciona os byte à string pela passagem por referência*/

	         *(strReceive + strlen(strReceive) + 1) = '\0';

	         *(strReceive + strlen(strReceive)) = (char) confirm;
		}

	     	break;

/* Para o caso 1, limita o recebimento da string pelo stopbyte informado */

	  case 1:

	     	while(1){

          	  confirm = -1;
			  
/* Enquanto não recebe o byte, continua no laço de repetição*/			  

          	  while(confirm == -1){
				
			     confirm = apbuart_inbyte(device);

			  }

/* Se o byte recebido for o do stopbyte, para o recebimento e não inclui o stopbyte na string */

			  if((char) confirm == (char) stopnumBytes){

                 break;

			  }

/* Adiciona o byte à string pela passagem por referência*/

              *(strReceive + strlen(strReceive) + 1) = '\0';

	          *(strReceive + strlen(strReceive)) = (char) confirm;

              cont++;

			};

	     	break;

	}

	return;    
}

void apbtToApbtString(struct apbuart_priv *deviceSend, struct apbuart_priv *deviceRecv, char strSend[U32_MAX_STRING], char strRecv[U32_MAX_STRING]){

/* Inicializa as variáveis */

   uint32_t cont;
   int32_t confirm;

/* Envio e recebimento de cada caractere */

   for(cont = 0; cont < strlen(strSend); cont++){

      confirm = 0;

/* Enquanto o caractere não é enviado, repete a função de envio de dados */

      while(confirm == 0){

         confirm = apbuart_outbyte(deviceSend, strSend[cont]);

      }

	  confirm = -1;

/* Enquanto o caractere não é recebido, repete a função de recebimento de dados */

	  while(confirm == -1){

         confirm = apbuart_inbyte(deviceRecv);

	  }

/* Insere o caractere recebido na string de recebimento */

      strRecv[cont] = confirm;

   }

	return;
}

int iFindChar(char str[U32_MAX_STRING], char chr){
/* Desc: Função utilizada para encontrar a primeira ocorrência de um caractere em uma string.
   Return: index onde o caracter foi encontrado.
   Parameters: str --> String onde o caracter será procurado.
               chr --> Caractere a ser procurado

*/

    int cont = 0;
	int index;

	for(cont = 0; cont < strlen(str) ; cont++){

       if(str[cont] == chr){

          index = cont;

		  break;

	   }


	}

	return index;
}

// Calcula a média móvel de 4 termos
float moving_average(float current_value){

    static float last_values[4] = {0, 0, 0, 0};
    float output_value;

    // Realiza o shift de valores antigos
    for(int i = 3; i > 0; i--) last_values[i] = last_values[i - 1];

    // Recebe o valor atual
    last_values[0] = current_value;

    // Calcula o valor de saida atual
    output_value = (last_values[0] + last_values[1] + last_values[2] + last_values[3]) * 0.25;

    // Retorna o valor de saida atual
    return output_value;
}

float iir_filter(float* input_params, float* output_params, float current_input_value) {
    float output_value = 0;
    static float last_values_input[INPUT_PARAMS_SIZE] = {0};
    static float last_values_output[OUTPUT_PARAMS_SIZE] = {0};
 
    // Shift histórico
    for (int i = INPUT_PARAMS_SIZE - 1; i > 0; i--) {
        last_values_input[i] = last_values_input[i - 1];
    }
    for (int i = OUTPUT_PARAMS_SIZE - 1; i > 0; i--) {
        last_values_output[i] = last_values_output[i - 1];
    }
 
    // Novo input
    last_values_input[0] = current_input_value;
 
    // Parte feedforward (inputs)
    for (int i = 0; i < INPUT_PARAMS_SIZE; i++)
        output_value += last_values_input[i] * input_params[i];
 
    // Parte feedback (outputs anteriores, com sinal negativo)
    for (int i = 1; i < OUTPUT_PARAMS_SIZE; i++)
        output_value -= last_values_output[i] * output_params[i];
 
    // Armazena saída
    last_values_output[0] = output_value;
 
    return output_value;
}

//Converte uma string para float
float string_to_float(const char *str) {
	float output_value = 0.0;
	int decimal_found = 0;
	float decimal_place = 0.1;
	int negative = 0;
	int i = 0;

	// Pula espaços em branco e caracteres de controle no início
	while (str[i] == ' ' || str[i] == '\t' || str[i] == '\r' || str[i] == '\n') {
		i++;
	}

	// Verifica se é negativo
	if (str[i] == '-') {
		negative = 1;
		i++;
	} else if (str[i] == '+') {
		i++;
	}

	// Percorre cada caractere da string até encontrar um terminador
	while (str[i] != '\0' && str[i] != '!' && str[i] != '\r' && str[i] != '\n' && str[i] != ' ') {
		if (str[i] >= '0' && str[i] <= '9') {
			if (decimal_found) {
				output_value += (str[i] - '0') * decimal_place;
				decimal_place *= 0.1;
			} else {
				output_value = output_value * 10 + (str[i] - '0');
			}
		} else if (str[i] == '.' && !decimal_found) {
			decimal_found = 1;
		} else {
			// Para em caractere inválido
			break;
		}
		i++;
	}

	// Aplica o sinal se necessário
	if (negative) {
		output_value = -output_value;
	}

	return output_value;
}

//Converte um float para string
void float_to_string(float value, char *str, int precision) {
	int i = 0;
	int negative = 0;
	
	// Verifica se é negativo
	if (value < 0) {
		negative = 1;
		value = -value;  // Trabalha com valor positivo
		str[i++] = '-';
	}
	
	// Separa parte inteira e fracionária
	int int_part = (int)value;
	float frac_part = value - (float)int_part;
	
	// Converte a parte inteira
	if (int_part == 0) {
		str[i++] = '0';
	} else {
		char int_str[20];
		int j = 0;
		int temp = int_part;
		
		// Extrai dígitos da parte inteira
		while (temp > 0) {
			int_str[j++] = (temp % 10) + '0';
			temp /= 10;
		}
		
		// Inverte a string da parte inteira
		for (int k = j - 1; k >= 0; k--) {
			str[i++] = int_str[k];
		}
	}

	// Adiciona o ponto decimal
	str[i++] = '.';

	// Converte a parte fracionária
	for (int p = 0; p < precision; p++) {
		frac_part *= 10.0;
		int digit = (int)frac_part;
		
		// Garante que o dígito está no range válido
		if (digit >= 0 && digit <= 9) {
			str[i++] = digit + '0';
		} else {
			str[i++] = '0';  // Valor de segurança
		}
		
		frac_part -= (float)digit;
		
		// Evita acumulação de erro de ponto flutuante
		if (frac_part < 0.0) {
			frac_part = 0.0;
		}
	}

	str[i] = '\0'; // Finaliza a string
}