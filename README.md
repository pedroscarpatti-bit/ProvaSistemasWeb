# 🏆 Sistema de Leilão Online

Sistema de leilão online desenvolvido com Flask, simulando arquitetura de microsserviços com Lambdas AWS e SQS.

## 📋 Arquitetura

O sistema é composto por:

- **API Flask**: Aplicação principal com endpoints REST
- **Lambda 1 (Processador)**: Consome e processa lances da fila SQS
- **Lambda 2 (Finalizador)**: Verifica e finaliza leilões expirados
- **SQS Simulado**: Fila de mensagens usando arquivo JSON
- **Armazenamento**: Persistência em arquivos JSON

## 🚀 Como Executar

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Criar Estrutura de Dados

Os arquivos JSON na pasta `data/` já vêm com dados de exemplo. Se necessário, você pode recriá-los.

### 3. Iniciar os Serviços

**Terminal 1 - API Flask:**
```bash
python app.py
```
A API estará disponível em `http://localhost:5000`

**Terminal 2 - Lambda Processador:**
```bash
python lambdas/lambda_processador.py
```

**Terminal 3 - Lambda Finalizador:**
```bash
python lambdas/lambda_finalizador.py
```

Ou para execução única:
```bash
python lambdas/lambda_finalizador.py --once
```

## 📡 Endpoints da API

### Usuários

- `GET /usuarios` - Lista todos os usuários
- `POST /usuarios` - Cria novo usuário
  ```json
  {
    "nome": "João Silva",
    "email": "joao@email.com",
    "saldo": 5000.0
  }
  ```
- `GET /usuarios/<usuario_id>` - Detalhes de um usuário

### Leilões

- `GET /leiloes` - Lista todos os leilões
- `POST /leiloes` - Cria novo leilão
  ```json
  {
    "titulo": "Notebook Dell",
    "descricao": "i7, 16GB RAM",
    "preco_inicial": 2000.0,
    "data_fim": "2025-11-15T20:00:00"
  }
  ```
- `GET /leiloes/<leilao_id>` - Detalhes de um leilão

### Lances

- `POST /lances` - Envia novo lance (vai para fila SQS)
  ```json
  {
    "leilao_id": "leilao_1",
    "usuario_id": "user_1",
    "valor": 2100.0
  }
  ```
- `GET /lances/<leilao_id>` - Lista lances de um leilão

### Debug

- `GET /fila` - Visualiza mensagens na fila SQS
- `GET /status` - Status geral do sistema

## 🧪 Testando o Sistema

### 1. Verificar Status Inicial
```bash
curl http://localhost:5000/status
```

### 2. Listar Leilões Disponíveis
```bash
curl http://localhost:5000/leiloes
```

### 3. Fazer um Lance
```bash
curl -X POST http://localhost:5000/lances \
  -H "Content-Type: application/json" \
  -d '{
    "leilao_id": "leilao_1",
    "usuario_id": "user_1",
    "valor": 2100.0
  }'
```

### 4. Ver Lances do Leilão
```bash
curl http://localhost:5000/lances/leilao_1
```

### 5. Verificar Fila
```bash
curl http://localhost:5000/fila
```

## 📊 Estrutura dos Dados

### usuarios.json
```json
{
  "user_1": {
    "nome": "João Silva",
    "email": "joao@email.com",
    "saldo": 5000.0
  }
}
```

### leiloes.json
```json
{
  "leilao_1": {
    "titulo": "Notebook Dell",
    "descricao": "i7, 16GB RAM",
    "preco_inicial": 2000.0,
    "preco_atual": 2000.0,
    "data_fim": "2025-11-15T20:00:00",
    "status": "ativo",
    "vencedor_id": null
  }
}
```

### lances.json
```json
[
  {
    "id": "lance_1",
    "leilao_id": "leilao_1",
    "usuario_id": "user_1",
    "valor": 2100.0,
    "data_hora": "2025-11-10T15:30:00",
    "status": "processado"
  }
]
```

## 🔄 Fluxo de Funcionamento

1. **Usuário faz lance** → POST /lances
2. **Flask valida** → Adiciona mensagem na fila_sqs.json
3. **Lambda Processador** → Consome fila, valida e processa lance
4. **Lambda Finalizador** → Verifica periodicamente leilões expirados
5. **Sistema atualiza** → Define vencedores e finaliza leilões

## 🎯 Regras de Negócio

- Lance deve ser no mínimo 5% maior que o lance atual
- Usuário deve ter saldo suficiente
- Leilão deve estar ativo
- Data de fim não pode ter passado

## 🛠️ Tecnologias

- Python 3.x
- Flask 3.0.0
- JSON (armazenamento)

## 📝 Observações

- Sistema desenvolvido para fins educacionais
- Simula arquitetura AWS (Lambda + SQS) localmente
- Armazenamento em JSON (não recomendado para produção)
- Para produção, considere usar banco de dados real e AWS real

## 👨‍💻 Autor

Sistema de Leilão Online - Projeto de Arquitetura Web