#!/usr/bin/env python3
"""
Script simples para enviar dados chirp para localhost:5050 via linha de comando
"""

import socket
import pandas as pd
import re
import time
import sys
import os

def parse_filtered_value(response):
    """Extrai o valor filtrado da resposta do servidor"""
    try:
        # Procurar por "DEBUG: Valor filtrado: X.XXXXXX"
        match = re.search(r'DEBUG: Valor filtrado: ([-+]?\d*\.?\d+)', response)
        if match:
            return float(match.group(1))
        return None
    except Exception as e:
        print(f"Erro ao extrair valor filtrado: {e}")
        return None

def send_value_to_server(value, server="localhost", port=5050, timeout=5):
    """Envia um valor para o servidor e retorna a resposta"""
    try:
        # Criar socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        # Conectar
        sock.connect((server, port))
        
        # Enviar valor com '!' no final
        message = f"{value}!"
        sock.send(message.encode('utf-8'))
        
        # Receber resposta
        response = ""
        while True:
            data = sock.recv(1024).decode('utf-8')
            if not data:
                break
            response += data
            # Verificar se recebemos a resposta completa
            if "DEBUG: Processamento concluido" in response:
                break
        
        sock.close()
        return response
        
    except Exception as e:
        return f"ERRO: {str(e)}"

def main():
    # Configurações padrão
    input_file = "dados_chirp.xlsx"
    output_file = "dados_chirp_filtrados.xlsx"
    server = "localhost"
    port = 5050
    delay_ms = 100
    
    # Verificar argumentos de linha de comando
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    print(f"Cliente TCP Chirp")
    print(f"=================")
    print(f"Servidor: {server}:{port}")
    print(f"Arquivo de entrada: {input_file}")
    print(f"Arquivo de saída: {output_file}")
    print(f"Delay entre envios: {delay_ms}ms")
    print()
    
    # Verificar se arquivo existe
    if not os.path.exists(input_file):
        print(f"ERRO: Arquivo '{input_file}' não encontrado.")
        return
    
    try:
        # Carregar dados
        print("Carregando dados...")
        df = pd.read_excel(input_file)
        
        # Obter primeira coluna numérica
        numeric_columns = []
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                numeric_columns.append(col)
        
        if not numeric_columns:
            print("ERRO: Nenhuma coluna numérica encontrada no arquivo.")
            return
        
        data_column = numeric_columns[0]
        values = df[data_column].dropna().tolist()
        
        print(f"Coluna de dados: '{data_column}'")
        print(f"Total de valores: {len(values)}")
        print()
        
        # Testar conexão
        print("Testando conexão com o servidor...")
        try:
            test_response = send_value_to_server(values[0] if values else 0, server, port, 2)
            if "ERRO:" in test_response:
                print(f"ERRO na conexão: {test_response}")
                return
            print("Conexão OK!")
        except Exception as e:
            print(f"ERRO na conexão: {e}")
            return
        
        print()
        print("Iniciando envio dos dados...")
        print("-" * 50)
        
        # Enviar valores
        filtered_values = []
        successful_sends = 0
        
        for i, value in enumerate(values):
            print(f"[{i+1:4d}/{len(values)}] Enviando: {value}", end=" ")
            
            # Enviar valor
            response = send_value_to_server(value, server, port)
            
            # Processar resposta
            if "ERRO:" not in response:
                filtered_value = parse_filtered_value(response)
                if filtered_value is not None:
                    filtered_values.append(filtered_value)
                    successful_sends += 1
                    print(f"-> Filtrado: {filtered_value}")
                else:
                    filtered_values.append(None)
                    print("-> Erro: valor filtrado não encontrado")
            else:
                filtered_values.append(None)
                print(f"-> {response}")
            
            # Delay entre envios
            if delay_ms > 0 and i < len(values) - 1:  # Não fazer delay no último
                time.sleep(delay_ms / 1000.0)
        
        print("-" * 50)
        print(f"Envio concluído!")
        print(f"Valores processados: {len(values)}")
        print(f"Sucessos: {successful_sends}")
        print(f"Falhas: {len(values) - successful_sends}")
        print()
        
        # Salvar resultados
        print(f"Salvando resultados em '{output_file}'...")
        
        # Criar DataFrame com valores originais e filtrados
        min_length = min(len(values), len(filtered_values))
        
        results_df = pd.DataFrame({
            'Valor_Original': values[:min_length],
            'Valor_Filtrado': filtered_values[:min_length]
        })
        
        # Salvar no Excel
        results_df.to_excel(output_file, index=False)
        
        print(f"Arquivo salvo: {output_file}")
        print(f"Linhas salvas: {len(results_df)}")
        
        # Estatísticas
        valid_filtered = [v for v in filtered_values if v is not None]
        if valid_filtered:
            print()
            print("Estatísticas dos valores filtrados:")
            print(f"- Mínimo: {min(valid_filtered):.6f}")
            print(f"- Máximo: {max(valid_filtered):.6f}")
            print(f"- Média: {sum(valid_filtered)/len(valid_filtered):.6f}")
        
        print()
        print("Processamento concluído com sucesso!")
        
    except Exception as e:
        print(f"ERRO: {str(e)}")

if __name__ == "__main__":
    main()