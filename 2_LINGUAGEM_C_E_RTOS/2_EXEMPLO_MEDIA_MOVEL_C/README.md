# Exemplo de Filtro Media Movel em C


## Introdução

O intuito dessa seção é o de programar, baseando-se nos recursos fornecidos a partir da Linguagem C de programação, um filtro média móvel simples de `n` parâmetros. O principal objetivo desse exemplo é mostrar o fluxo de programação, compilação e execução básico da linguagem C em um sistema operacional Windows, fazendo uso do compilador GCC (GNU C Compiller).

O entendimento desse exemplo será fundamental para a compreensão das próximas etapas dessa seção, especialmente para a integração e geração de códigos C com o auxílio da ferramenta **MATLAB Coder**.


## Requisitos

Para a execução e compreensão dessa seção, o usuário deve ter conhecimento:

- Do conceito de um filtro média móvel simples (já abordado anteriormente).
- De programação básica usando a linguagem C, envolvendo variáveis, funções, _arrays_, entre outros.
- De compiladores no geral.
- De manuseio básico, importação de dados .csv e criação de gráficos usando a ferramenta Microsoft Excel.


## Passo à Passo


### 1° Instalação do GCC e adição ao PATH do sistema

Primeiramente, é preciso instalar o compilador do GCC ao sistema operacional. Há algumas formas gerais para fazê-lo, mas iremos adotar o gerenciador de binários `Cygwin`. Basicamente, o `Cygwin` figurativamente representa um gerenciador de pacotes, tal como o `apt-get` do Debian/Ubuntu, mas para o Windows. Dessa forma, permite a instalação de binários como o próprio `gcc` e muitos outros, como o `make` e o `cmake`, por exemplo.

Para isso, sigla o tutorial segundo o vídeo [aqui.](https://www.youtube.com/watch?v=2INdPM0Y7pI).

Ao final do tutorial, abra um Cygwin Terminal e digite o seguinte comando:

```bash
gcc --version
```

O resultado esperado deve ser algo como:

```bash
gcc (GCC) 13.4.0
Copyright (C) 2023 Free Software Foundation, Inc.
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
```

Nesse caso, a versão do gcc utilizada foi a 13.4.0, mas pode ser virtualmente qualquer uma.


### 2° Criação de um código média móvel simples

Agora que temos o gcc instalado corretamente, é possível programar um código C simples que realize a média móvel de, por exemplo, `4 termos`.

Para fins didáticos, as entradas e saídas do filtro média móvel serão feitas a partir da biblioteca `stdio.h` do C, fazendo o uso das funções `printf()` (para a saída de dados) e `scanf()` (para a entrada de dados). O filtro promoverá uma filtragem dos dados em tempo real, calculando sua saída a cada entrada recebida.

Antes de tudo, é preciso criar uma função que faça essa tarefa de filtragem, recebendo sempre uma variável `float` de entrada e retornando um `float`. Dessa forma, a função abaixo é criada:

```C
#define NUM_TERMS 4

float moving_avg_function(float current_input){

    // Creates an empty array for holding the last terms - It must be static to hold the last items
    static float last_terms[NUM_TERMS] = {0};
    float acc_value = 0;

    // For loop to right shift last terms
    for(int i = NUM_TERMS - 1; i > 0; i--) last_terms[i] = last_terms[i - 1];
    
    // Stores the current term
    last_terms[0] = current_input;

    // Accumulates the last terms values and returns the function
    for(int i = 0; i < NUM_TERMS; i++) acc_value += last_terms[i];

    return acc_value / NUM_TERMS;

}
```

Por conta da variável estática `last_terms[NUM_TERMS]`, cada vez que a função é chamada, os últimos termos do filtro são atualizados, garantindo a sua operação contínua e correta.

Agora, é preciso criar um código que repetidamente receba inputs do usuário, aplique a função `moving_avg_function` e exiba a saída atual do filtro. Para isso, o seguinte código é gerado:

```C
int main(){

    // Creates float variables for the input and output values
    float input_value, output_value;

    // Enters a continuous loop
    while(1){

        // Asks the user for a input value and stores it
        printf("Please, enter an input value: ");
        scanf("%f", &input_value);

        // Executes the moving avg function
        output_value = moving_avg_function(input_value);

        // Prints the current value
        printf("\nThe current moving avg value is: %.4f\n", output_value);

    }

    return 0;
}

```

Para facilitar a elaboração do código, tanto a declaração da função `moving_avg_function()` quanto a função `main()` e outros pontos importantes já estão contidas no código `main.c` desse mesmo repositório.


### 3° Compilação e execução do código

Como todas as funções do código que temos, incluindo a função `main()`, estão inclusas no arquivo `main.c`, basta o compilarmos e executarmos.

Para compilar o código, abra um Cygwin Terminal e aponte-o para a pasta do código `main.c` (caso tenha dúvidas, pesquise pelo comando `cd`). Agora, basta executarmos o comando abaixo:

```bash
gcc main.c -o main
```

O comando em questão compilará todo o código C do arquivo `main.c` para a arquitetura do computador atual, gerando um executável binário `main`. Caso nenhum erro tenha sido gerado, basta executar o código e fornecer valores de entrada e verificar os valores de saída gerados, tal como mostrado abaixo:

```bash
$ ./main
Please, enter an input value: 10

The current moving avg value is: 2.5000
Please, enter an input value: 0

The current moving avg value is: 2.5000
Please, enter an input value: 10

The current moving avg value is: 5.0000
Please, enter an input value: 0

The current moving avg value is: 5.0000
Please, enter an input value: 10

The current moving avg value is: 5.0000
Please, enter an input value: 0

The current moving avg value is: 5.0000
Please, enter an input value: 10

The current moving avg value is: 5.0000
Please, enter an input value: 0

The current moving avg value is: 5.0000
Please, enter an input value: 10

The current moving avg value is: 5.0000
Please, enter an input value: 0

The current moving avg value is: 5.0000
Please, enter an input value: 10

The current moving avg value is: 5.0000
Please, enter an input value: 0

The current moving avg value is: 5.0000
Please, enter an input value: -7

The current moving avg value is: 0.7500
Please, enter an input value: -8

The current moving avg value is: -1.2500
Please, enter an input value: -9

The current moving avg value is: -6.0000
Please, enter an input value: -10

The current moving avg value is: -8.5000
Please, enter an input value:
```

Para terminar a execução do código, basta interrompê-lo com `Cntrl + C`.

Assim, ao digitar valores de entrada, é perceptível que as saídas fazem uma média das últimas 4 entradas colocadas, suavizando o sinal.


### 4° Investigação e visualização dos sinais

De forma a visualizar isso de forma facilitada, é possível a compilação manual de uma tabela no Microsoft Excel segundo os valores de entrada e de saída do filtro.

Para isso, primeiro vamos executar o código para que filtre uma onda quadrada simulada, de amplitude 1 e período de 20 iterações. Vamos repetir essa onda quadrada ao menos 2 ciclos, para que os efeitos do filtro possam ser observados com maior clareza.

De forma a tornar a tarefa mais facilitada, vamos inserir primeiro um array com os valores da onda quadrada de forma a simular uma entrada do código, alterando-o:

```C

float square_wave[40] = {1, 1, 1, 1, 1, 1, 1, 1, 1, 1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1};

int main(){

    // Creates float variables for the input and output values
    float input_value, output_value;

    // Initializes an itrt for the square_wave
    int square_wave_itrt = 0;

    // Enters a continuous loop
    while(1){

        // Asks the user for a input value and stores it
        printf("Entering the %ith value from the square_wave...", square_wave_itrt);
        input_value = square_wave[square_wave_itrt];
        square_wave_itrt++;

        // Executes the moving avg function
        output_value = moving_avg_function(input_value);

        // Prints the current value
        printf("\nThe current moving avg value is: %.4f\n\n", output_value);

        // If the square_wave_itrt is equal or greater than 40, stops the code
        if (square_wave_itrt >= 40) break;

    }

    return 0;
}

```

No entanto, o código em questão ainda apresenta uma dificuldade na obtenção dos dados de entrada e de saída. Para isso, vamos criar um arquivo `data.txt` para que o código coloque os dados no formato csv:

```C

float square_wave[40] = {1, 1, 1, 1, 1, 1, 1, 1, 1, 1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1};

int main(){

    // Creates float variables for the input and output values
    float input_value, output_value;

    // Initializes an itrt for the square_wave
    int square_wave_itrt = 0;

    // Initializes a file and writes the firts line
    FILE* file_pointer = fopen("data.txt", "w");
    fputs("iterator,input_value, output_value\n", file_pointer);

    // Creates a str to write into the file
    char file_string[100];

    // Enters a continuous loop
    while(1){

        // Asks the user for a input value and stores it
        printf("Entering the %ith value from the square_wave...", square_wave_itrt);
        input_value = square_wave[square_wave_itrt];
        square_wave_itrt++;

        // Executes the moving avg function
        output_value = moving_avg_function(input_value);

        // Prints the current value
        printf("\nThe current moving avg value is: %.4f\n\n", output_value);

        // Puts the values into the file string and puts the file string into the file
        sprintf(file_string, "%d, %.4f, %.4f\n",square_wave_itrt, input_value, output_value);
        fputs(file_string, file_pointer);

        // If the square_wave_itrt is equal or greater than 40, stops the code
        if (square_wave_itrt >= 40) break;

    }

    return 0;
}

```

Esse código adaptado para a análise da onda quadrada pode ser encontrado segundo o arquivo `main_modified.c`. Compilando o código segundo o comando:

```bash
gcc main_modified.c -o main_modified
```

É possível executar o código e verificar a seguinte saída segundo o arquivo `data.txt`:

```bash
iterator,input_value, output_value
1, 1.0000, 0.2500
2, 1.0000, 0.5000
3, 1.0000, 0.7500
4, 1.0000, 1.0000
5, 1.0000, 1.0000
6, 1.0000, 1.0000
7, 1.0000, 1.0000
8, 1.0000, 1.0000
9, 1.0000, 1.0000
10, 1.0000, 1.0000
11, -1.0000, 0.5000
12, -1.0000, 0.0000
13, -1.0000, -0.5000
14, -1.0000, -1.0000
15, -1.0000, -1.0000
16, -1.0000, -1.0000
17, -1.0000, -1.0000
18, -1.0000, -1.0000
19, -1.0000, -1.0000
20, -1.0000, -1.0000
21, 1.0000, -0.5000
22, 1.0000, 0.0000
23, 1.0000, 0.5000
24, 1.0000, 1.0000
25, 1.0000, 1.0000
26, 1.0000, 1.0000
27, 1.0000, 1.0000
28, 1.0000, 1.0000
29, 1.0000, 1.0000
30, 1.0000, 1.0000
31, -1.0000, 0.5000
32, -1.0000, 0.0000
33, -1.0000, -0.5000
34, -1.0000, -1.0000
35, -1.0000, -1.0000
36, -1.0000, -1.0000
37, -1.0000, -1.0000
38, -1.0000, -1.0000
39, -1.0000, -1.0000
40, -1.0000, -1.0000
```

Após isso, basta abrir o arquivo `data.txt` no Microsoft Excel, com as seguintes considerações:

- Considere o caractere `.` como separador decimal;
- Considere o caractere `,` como separador de linhas;

Assim, a seguinte planilha é gerada:

![alt text](/images/image.png)

A planilha em questão pode ser visualizada segundo o arquivo `data.xlsx`. Para visualizarmos os dados ao longo das iterações, basta selecionar os dados e criar um gráfico de dispersão com interligações, gerando a seguinte imagem:

![alt text](/images/image-1.png)

É possível visualizar que a saída, em laranja, apresenta uma transição mais suavizada para quando a onda quadrada da entrada, em azul, realiza uma transição abrupta. Isso evidencia o caráter `passa-baixas` do filtro média móvel, filtrando as frequências mais altas e suavizando, poranto, transições abruptas.


## Investigações adicionais

Com o código proveniente desse exemplo e os dados capturados, é possível realizar algumas possíveis investigações adicionais, como sugestão:

- Realize um processamento dos sinais digitais de entrada e saída usando o Python ou o MATLAB de forma a encontrar uma função de transferência aproximada ao filtro média móvel construído.
- Plote o diagrama de Bode para a função de transferência encontrada. É esperado que, por uma análise principalmente do diagrama de amplitude, uma tendência de filtro passa-baixas seja visualizada.
- Altere o código para inserir ondas senoidais de frequências distintas, verificando o valor da saída do filtro perante as entradas colocadas. É esperado que frequências mais altas gerem saídas gradativamente menores, por conta do caráter passa-baixas do filtro.










