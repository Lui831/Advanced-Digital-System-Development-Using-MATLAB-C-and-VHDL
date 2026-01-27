# Use uma imagem base do Debian Slim
FROM debian:bookworm-slim

# Atualizar pacotes e instalar as dependências necessárias para Python e QEMU
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libpixman-1-0 \
    python3 \
    libncurses5 \
    python3-pip \
    python3-venv \
    gdb \
    ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Crie um diretório no contêiner para o QEMU
RUN mkdir -p /qemu-8.1.1/build/

# Adicionar os arquivos necessários ao contêiner
COPY qemu-system-sparc /qemu-8.1.1/build/
# COPY kernel /qemu-8.1.1/build/src-interface

# Adiciona o gdb da gaisler na pasta bin do container
COPY sparc-gaisler-elf-gdb /bin
 
#Colocar código de comunicação com o usuário
WORKDIR /qemu-8.1.1/build/

RUN chmod +x ./qemu-system-sparc
RUN ls -l ./qemu-system-sparc
RUN chmod +x /bin/sparc-gaisler-elf-gdb
RUN ls -l /bin/sparc-gaisler-elf-gdb


# Copiar o script para dentro do contêiner
COPY ./src-interface/leitor_dados.py ./src-interface/respostas_dados.py ./src-interface/main.py ./src-interface/client_qemu.py ./

# Inicializa o ambiente virtual
RUN python3 -m venv venv

# Instala o fastcrc
RUN ./venv/bin/pip3 install fastcrc
RUN ./venv/bin/pip3 install pexpect
