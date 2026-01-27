# Simple Makefile to build programs based on bcc/Sparc3
# NOTE: indentation is always with TAB character -> do not use spaces

# Detecta se é Windows ou Linux baseado na existência do compilador
ifeq ($(shell test -f D:/bcc2/bcc-2.0.7-gcc/bin/sparc-gaisler-elf-gcc.exe && echo yes),yes)
	# Windows path to the bcc compiler
	CC=D:/bcc2/bcc-2.0.7-gcc/bin/sparc-gaisler-elf-gcc.exe
else
	# Linux path to the bcc compiler
	CC=sparc-gaisler-elf-gcc
endif

# typical flags for the bcc compiler
# -DCORE_DEBUG
# CFLAGS=-g -O0 -Wall
# CFLAGS=-g -O2 -DPERFORMANCE_RUN=1 -DITERATIONS=1000
CFLAGS=-gdwarf-3 -O2 -msoft-float -Isrc/include -Isrc -Ibutter_4_low -I.

# Gaisler driver library
LDFLAGS=-ldrv -lm

# Pastas
SRC_DIR = src
OBJ_DIR = obj
BIN_DIR = bin


# Arquivo final
TARGET = $(BIN_DIR)/programa

# Lista arquivos fonte do projeto
SRC_FILES = $(SRC_DIR)/uart.c $(SRC_DIR)/main.c

# Todos os arquivos fonte
ALL_SRCS = $(SRC_FILES)

# Transforma em .o dentro de OBJ_DIR
OBJS = $(SRC_FILES:$(SRC_DIR)/%.c=$(OBJ_DIR)/%.o)

# Regra padrão
all: $(TARGET)

# Compila o executável
$(TARGET): $(OBJS)
	@mkdir -p $(BIN_DIR)
	$(CC) $(CFLAGS) $^ -o $@ $(LDFLAGS)

# Compila objetos do diretório src
$(OBJ_DIR)/%.o: $(SRC_DIR)/%.c
	@mkdir -p $(OBJ_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

# Compila objetos do diretório butter_4_low
$(OBJ_DIR)/%.o: $(BUTTER_DIR)/%.c
	@mkdir -p $(OBJ_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

# Limpeza
clean:
	@rm -rf $(OBJ_DIR) $(BIN_DIR)

# Executar
run: all
	./$(TARGET)

# Mostra informações de compilação
info:
	@echo "Compiler: $(CC)"
	@echo "CFLAGS: $(CFLAGS)"
	@echo "LDFLAGS: $(LDFLAGS)"
	@echo "Source files: $(ALL_SRCS)"
	@echo "Object files: $(OBJS)"
	@echo "Target: $(TARGET)"

# Força recompilação
rebuild: clean all

.PHONY: all clean run info rebuild