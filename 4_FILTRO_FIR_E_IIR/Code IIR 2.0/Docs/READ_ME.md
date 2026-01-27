# ModulatedEMUREALTest

## Description

Source-code that configures a general test closed loop between an arbitrary number of real and emulated APBUARTs.

## Related Files

- <u>src/main.c</u>: Main *.C* code that implements the tests.
- <u>src/uart.c and src/include/uart.h</u>: APBUART library for transmitting, receiving and transforming data (see Libraries/apbuart for more information).

The structure of the `main.c` file of the test source-code is going to be analyzed and explained in the next topic.

### main.c

- <u>Description</u>: Source-code that implements an arbitrary number of APBUARTs, verify it's FIFOs, receives an character array through an APBUART, apply a transformation to it and sends it back through the same APBUART.

``` C
/* Inclusão de bibliotecas */

#include <stdio.h>
#include <drv/apbuart.h>
#include "include/uart.h"
#include <string.h>



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

    while(1){

       /* Se, para a UART em questão, DR estiver pronto, então continue */
       status = apbuart_get_status(oDevices[u32Cont]);

       if(apbuart_get_status(oDevices[u32Cont]) & U32_DR_MASK != U32_DR_COMPARE){

    	   status = apbuart_get_status(oDevices[u32Cont]);
          /* Recebe string, delimitada pelo caractere de exclamação. Transforma string utilizando a cifra de César. */
          apbuartReceiveString(oDevices[u32Cont], strReceive, 1, 0x21);
		  CipherCaesar(strReceive, strSend, numOffset);
		  apbuartSendString(oDevices[u32Cont], strSend);

       }

	   u32Cont = (u32Cont + 1) % U32_MAX_DEVICE;

	}

	return 0;
}
```

- <u>Functioning</u>: First, the program includes the necessary and implemented libraries, initializes the variables, and configures all the APBUARTs of the system based on the define `U32_MAX_DEVICE`. Then, it remains in an infinite loop where it checks the FIFOs of the configured APBUARTs: if it is empty, it moves on to the next APBUART; if there is data, it acquires it and stores it in the character array `strReceive`, applies the Caesar Cipher algorithm to it, and re-sends the transformed character array from the same APBUART.