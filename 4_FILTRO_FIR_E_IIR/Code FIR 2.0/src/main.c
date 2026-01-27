/* Inclusão de bibliotecas */

#include <stdio.h>
#include <drv/apbuart.h>
#include "include/uart.h"
#include <string.h>
#include <stdlib.h>



/* Função main */

int main(void){

/* 	Declaração das variáveis principais */

	struct apbuart_priv* oDevices[U32_MAX_DEVICE];
	struct apbuart_config oConfigs[U32_MAX_DEVICE];
	char strSend[U32_MAX_STRING], strReceive[U32_MAX_STRING];
	
    uint32_t numTest = 1000; /*DIGITE O NÚMERO DE TESTES*/
	uint32_t numOffset = 23; /*DIGITE O OFFSET UTILIZADO NA CIFRA DE CÉSAR*/
	uint32_t u32Cont;
	uint32_t status;

/* Inicialização dos drivers das APBUARTs e inicialização das APBUARTs */

	apbuart_autoinit();

	for(u32Cont = 0; u32Cont < U32_MAX_DEVICE; u32Cont++){

       oDevices[u32Cont] = apbuart_open(u32Cont);

	}

/* Configurações das APBUARTs */

    for(u32Cont = 0; u32Cont < U32_MAX_DEVICE; u32Cont++){

	oConfigs[u32Cont].baud = 115200; /* Baud rate configurado para cada uma das APBUARTs */
	oConfigs[u32Cont].parity = APBUART_PAR_NONE; /* Desativa paridade */
	oConfigs[u32Cont].flow = 0; /* Desativa controle de fluxo */
	oConfigs[u32Cont].mode = APBUART_MODE_NONINT; /* Non blocking mode */
	oConfigs[u32Cont].rxfifobuflen = 10; /* 10 bytes para o buffer da fifo de recebimento */
	apbuart_config(oDevices[u32Cont], &(oConfigs[u32Cont]));

	}

/* Loop de recebimento, transformação e envio de strings */

    u32Cont = 0;
    
    // Debug: Sistema iniciado
    apbuartSendString(oDevices[0], "DEBUG: Sistema de filtro iniciado\r\n");

    while(1){

       /* Se, para a UART em questão, DR estiver pronto, então continue */
       status = apbuart_get_status(oDevices[u32Cont]);

       if(apbuart_get_status(oDevices[u32Cont]) & U32_DR_MASK != U32_DR_COMPARE){

    	   status = apbuart_get_status(oDevices[u32Cont]);
          
          // Debug: Processando UART
          char debugMsg[U32_MAX_STRING];
          sprintf(debugMsg, "DEBUG: Processando UART %d\r\n", u32Cont);
          apbuartSendString(oDevices[u32Cont], debugMsg);
          
          /* Recebe string, delimitada pelo caractere de exclamação. Transforma string utilizando a cifra de césar. */
          apbuartReceiveString(oDevices[u32Cont], strReceive, 1, 0x21);
          
          // Debug: String recebida com informações detalhadas
          sprintf(debugMsg, "DEBUG: Recebido: '%s' (len=%d)\r\n", strReceive, strlen(strReceive));
          apbuartSendString(oDevices[u32Cont], debugMsg);
          
          // Debug: Mostra bytes individuais da string para diagnóstico
          sprintf(debugMsg, "DEBUG: Bytes hex: ");
          apbuartSendString(oDevices[u32Cont], debugMsg);
          for(int j = 0; j < strlen(strReceive) && j < 10; j++) {
              char hexByte[10];
              sprintf(hexByte, "%02X ", (unsigned char)strReceive[j]);
              apbuartSendString(oDevices[u32Cont], hexByte);
          }
          apbuartSendString(oDevices[u32Cont], "\r\n");

		  //Converte string para float, aplique média móvel e converta de volta para string
		  float floatValue = string_to_float(strReceive);
		  
		  // Debug: Valor convertido para float
		  char floatStr[50];
		  float_to_string(floatValue, floatStr, 6);
		  sprintf(debugMsg, "DEBUG: Valor float: %s\r\n", floatStr);
		  apbuartSendString(oDevices[u32Cont], debugMsg);
		  
		  float smoothedValue = moving_average(floatValue);
		  
		  // Debug: Valor após filtro
		  char smoothedStr[50];
		  float_to_string(smoothedValue, smoothedStr, 6);
		  sprintf(debugMsg, "DEBUG: Valor filtrado: %s\r\n", smoothedStr);
		  apbuartSendString(oDevices[u32Cont], debugMsg);
		  
		  float_to_string(smoothedValue, strSend, 8);
		  
		  // Debug: Enviando resultado
		  sprintf(debugMsg, "DEBUG: Enviando: '%s'\r\n", strSend);
		  apbuartSendString(oDevices[u32Cont], debugMsg);
		  
		  //CipherCaesar(strReceive, strSend, numOffset);
		  apbuartSendString(oDevices[u32Cont], strSend);
		  
		  // Debug: Processamento concluído
		  apbuartSendString(oDevices[u32Cont], "DEBUG: Processamento concluido\r\n\r\n");

       }

	   u32Cont = (u32Cont + 1) % U32_MAX_DEVICE;

	}

	return 0;
}