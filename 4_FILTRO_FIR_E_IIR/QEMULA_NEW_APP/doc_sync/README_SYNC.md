# QEMULA Document Synchronization System

Sistema automatizado de sincronização entre documentos `.docx` e o `help_tab.py` da aplicação QEMULA.

## � Estrutura Organizada

Este sistema agora está organizadamente localizado na pasta `doc_sync/` do projeto QEMULA:

```
QEMULA_NEW_APP/
├── doc_sync/                     # 🆕 Sistema de sincronização
│   ├── __init__.py              # Módulo Python
│   ├── docs_sync.py             # Motor principal
│   ├── qemula_auto_sync.py      # Serviço automático
│   ├── sync_integration.py      # Interface de integração
│   ├── sync_config.json         # Configurações
│   ├── start_sync_service.bat   # Script de inicialização
│   ├── test_sync.py             # Testes
│   └── README_SYNC.md           # Esta documentação
├── docs/                        # Documentos .docx fonte
├── frontend/                    # Interface do usuário
│   └── help_tab.py             # Arquivo destino (atualizado automaticamente)
├── sync_docs.bat               # 🆕 Script principal de controle
└── update_resources.py         # Sistema de atualização integrado
```

## 🚀 Como Usar

### Método 1: Script Principal (Recomendado)

Na pasta raiz do projeto QEMULA:
```cmd
sync_docs.bat
```

Este script oferece um menu interativo com as opções:
- `sync` - Sincronização manual
- `service` - Serviço automático
- `status` - Verificar status
- `help` - Ajuda

### Método 2: Execução Direta

1. **Sincronização única:**
   ```cmd
   cd doc_sync
   ..\venv\Scripts\python.exe sync_integration.py --sync
   ```

2. **Serviço automático:**
   ```cmd
   cd doc_sync
   ..\venv\Scripts\python.exe qemula_auto_sync.py
   ```

3. **Verificar status:**
   ```cmd
   cd doc_sync
   ..\venv\Scripts\python.exe sync_integration.py --status
   ```

## 📁 Estrutura de Arquivos

```
QEMULA_NEW_APP/
├── docs/                          # Documentos .docx fonte
│   ├── Official Requirements.docx
│   └── QEMULA_User_Manual.docx
├── frontend/
│   └── help_tab.py               # Arquivo destino (será atualizado)
├── logs/                         # Logs do sistema (criado automaticamente)
├── docs_sync.py                  # Motor de sincronização
├── qemula_auto_sync.py          # Serviço automático
├── sync_config.json             # Configurações
├── start_sync_service.bat       # Script de inicialização
└── README_SYNC.md               # Este arquivo
```

## ⚙️ Configuração

O arquivo `sync_config.json` permite customizar o comportamento:

```json
{
  "docs_path": "docs",                    // Pasta dos documentos .docx
  "help_tab_path": "frontend/help_tab.py", // Arquivo destino
  "auto_sync": true,                      // Sincronização automática
  "sync_interval": 5,                     // Intervalo de debounce (segundos)
  "log_level": "INFO",                    // Nível de log (DEBUG/INFO/WARNING/ERROR)
  "notifications": true,                  // Notificações do sistema
  "backup_enabled": true,                 // Criar backups
  "max_backups": 5                        // Máximo de backups mantidos
}
```

## 🔄 Como Funciona

1. **Detecção de Mudanças**: O sistema monitora continuamente a pasta `docs/` por mudanças em arquivos `.docx`

2. **Extração de Conteúdo**: Quando detectada uma mudança:
   - Extrai texto e estrutura dos documentos
   - Identifica seções e títulos automaticamente
   - Mantém formatação e hierarquia

3. **Atualização do Help**: 
   - Gera novos itens de ajuda baseados no conteúdo extraído
   - Substitui a seção `help_items` no `help_tab.py`
   - Adiciona metadados (data de atualização, arquivo fonte)

4. **Backup e Segurança**:
   - Cria backup antes de qualquer alteração
   - Restaura automaticamente em caso de erro
   - Mantém histórico de alterações nos logs

## 📊 Monitoramento

### Logs
Os logs são salvos automaticamente em `logs/qemula_sync_YYYYMMDD.log` e incluem:
- Timestamp de cada operação
- Status de sincronização
- Erros e avisos
- Informações de debug

### Status do Sistema
Use o comando `status` no serviço para ver:
- Estado atual do monitoramento
- Última sincronização realizada
- Configuração ativa
- Tempo de atividade

## 🛠️ Resolução de Problemas

### Problema: Sincronização não funciona
**Solução**: 
1. Verifique se os documentos estão na pasta `docs/`
2. Confirme que não há arquivos temporários (começando com `~`)
3. Execute `sync` manualmente para testar

### Problema: Erro ao processar documento
**Solução**:
1. Verifique se o documento não está aberto em outro programa
2. Confirme que o arquivo não está corrompido
3. Veja os logs para detalhes específicos

### Problema: help_tab.py não foi atualizado
**Solução**:
1. Verifique permissões de escrita no arquivo
2. Confirme se existe backup (`.backup`)
3. Execute teste manual: `python test_sync.py`

## 🔧 Desenvolvimento

### Dependências
- `python-docx`: Para processar documentos Word
- `watchdog`: Para monitoramento de arquivos
- `PySide6`: Para interface gráfica do QEMULA

### Extensões Futuras
- Interface web para controle remoto
- Suporte a múltiplos formatos (PDF, MD)
- Integração com sistema de versionamento
- Notificações por email/Slack

## 📞 Suporte

Para problemas ou sugestões:
1. Verifique os logs em `logs/`
2. Execute teste diagnóstico: `python test_sync.py`
3. Consulte a documentação do QEMULA

---

**Desenvolvido para o projeto QEMULA**  
*Sistema de sincronização automática v1.0*
