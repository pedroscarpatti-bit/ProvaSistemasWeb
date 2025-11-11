from flask import Flask, request, jsonify
from datetime import datetime
import uuid
from utils.storage import (
    ler_json, escrever_json, adicionar_a_fila, 
    adicionar_lance, atualizar_leilao
)
from utils.validadores import (
    validar_usuario_existe, validar_leilao_existe,
    validar_leilao_ativo
)

app = Flask(__name__)

# ==================== ROTAS DE USUÁRIOS ====================

@app.route('/usuarios', methods=['GET'])
def listar_usuarios():
    """Lista todos os usuários"""
    usuarios = ler_json("usuarios.json")
    return jsonify(usuarios), 200

@app.route('/usuarios', methods=['POST'])
def criar_usuario():
    """Cria um novo usuário"""
    dados = request.get_json()
    
    if not dados or 'nome' not in dados or 'email' not in dados:
        return jsonify({"erro": "Nome e email são obrigatórios"}), 400
    
    usuarios = ler_json("usuarios.json")
    usuario_id = f"user_{uuid.uuid4().hex[:8]}"
    
    usuarios[usuario_id] = {
        "nome": dados['nome'],
        "email": dados['email'],
        "saldo": dados.get('saldo', 1000.0)  # Saldo inicial padrão
    }
    
    escrever_json("usuarios.json", usuarios)
    
    return jsonify({
        "mensagem": "Usuário criado com sucesso",
        "usuario_id": usuario_id,
        "usuario": usuarios[usuario_id]
    }), 201

@app.route('/usuarios/<usuario_id>', methods=['GET'])
def obter_usuario(usuario_id):
    """Obtém detalhes de um usuário específico"""
    usuarios = ler_json("usuarios.json")
    
    if usuario_id not in usuarios:
        return jsonify({"erro": "Usuário não encontrado"}), 404
    
    return jsonify(usuarios[usuario_id]), 200

# ==================== ROTAS DE LEILÕES ====================

@app.route('/leiloes', methods=['GET'])
def listar_leiloes():
    """Lista todos os leilões"""
    leiloes = ler_json("leiloes.json")
    return jsonify(leiloes), 200

@app.route('/leiloes/<leilao_id>', methods=['GET'])
def obter_leilao(leilao_id):
    """Obtém detalhes de um leilão específico"""
    leiloes = ler_json("leiloes.json")
    
    if leilao_id not in leiloes:
        return jsonify({"erro": "Leilão não encontrado"}), 404
    
    return jsonify(leiloes[leilao_id]), 200

@app.route('/leiloes', methods=['POST'])
def criar_leilao():
    """Cria um novo leilão"""
    dados = request.get_json()
    
    campos_obrigatorios = ['titulo', 'descricao', 'preco_inicial', 'data_fim']
    for campo in campos_obrigatorios:
        if campo not in dados:
            return jsonify({"erro": f"Campo '{campo}' é obrigatório"}), 400
    
    # Valida formato da data
    try:
        datetime.fromisoformat(dados['data_fim'])
    except ValueError:
        return jsonify({"erro": "Formato de data inválido. Use: YYYY-MM-DDTHH:MM:SS"}), 400
    
    leiloes = ler_json("leiloes.json")
    leilao_id = f"leilao_{uuid.uuid4().hex[:8]}"
    
    leiloes[leilao_id] = {
        "titulo": dados['titulo'],
        "descricao": dados['descricao'],
        "preco_inicial": float(dados['preco_inicial']),
        "preco_atual": float(dados['preco_inicial']),
        "data_fim": dados['data_fim'],
        "status": "ativo",
        "vencedor_id": None
    }
    
    escrever_json("leiloes.json", leiloes)
    
    return jsonify({
        "mensagem": "Leilão criado com sucesso",
        "leilao_id": leilao_id,
        "leilao": leiloes[leilao_id]
    }), 201

# ==================== ROTAS DE LANCES ====================

@app.route('/lances', methods=['POST'])
def criar_lance():
    """
    Cria um novo lance e adiciona à fila SQS para processamento.
    Validações básicas são feitas aqui, processamento completo na Lambda.
    """
    dados = request.get_json()
    
    campos_obrigatorios = ['leilao_id', 'usuario_id', 'valor']
    for campo in campos_obrigatorios:
        if campo not in dados:
            return jsonify({"erro": f"Campo '{campo}' é obrigatório"}), 400
    
    leilao_id = dados['leilao_id']
    usuario_id = dados['usuario_id']
    valor = float(dados['valor'])
    
    # Validações básicas
    valido, msg = validar_usuario_existe(usuario_id)
    if not valido:
        return jsonify({"erro": msg}), 404
    
    valido, msg = validar_leilao_existe(leilao_id)
    if not valido:
        return jsonify({"erro": msg}), 404
    
    valido, msg = validar_leilao_ativo(leilao_id)
    if not valido:
        return jsonify({"erro": msg}), 400
    
    # Adiciona à fila SQS para processamento assíncrono
    mensagem_id = f"msg_{uuid.uuid4().hex[:8]}"
    mensagem = {
        "mensagem_id": mensagem_id,
        "tipo": "novo_lance",
        "timestamp": datetime.now().isoformat(),
        "dados": {
            "leilao_id": leilao_id,
            "usuario_id": usuario_id,
            "valor": valor
        }
    }
    
    adicionar_a_fila(mensagem)
    
    return jsonify({
        "mensagem": "Lance enviado para processamento",
        "mensagem_id": mensagem_id,
        "status": "pendente"
    }), 202

@app.route('/lances/<leilao_id>', methods=['GET'])
def listar_lances_leilao(leilao_id):
    """Lista todos os lances de um leilão específico"""
    lances = ler_json("lances.json")
    
    lances_leilao = [
        lance for lance in lances 
        if lance.get('leilao_id') == leilao_id
    ]
    
    # Ordena por data (mais recente primeiro)
    lances_leilao.sort(key=lambda x: x.get('data_hora', ''), reverse=True)
    
    return jsonify(lances_leilao), 200

# ==================== ROTAS DE DEBUG ====================

@app.route('/fila', methods=['GET'])
def visualizar_fila():
    """Visualiza mensagens na fila SQS (para debug)"""
    fila = ler_json("fila_sqs.json")
    return jsonify({
        "total_mensagens": len(fila),
        "mensagens": fila
    }), 200

@app.route('/status', methods=['GET'])
def status_sistema():
    """Retorna status geral do sistema"""
    usuarios = ler_json("usuarios.json")
    leiloes = ler_json("leiloes.json")
    lances = ler_json("lances.json")
    fila = ler_json("fila_sqs.json")
    
    leiloes_ativos = sum(1 for l in leiloes.values() if l['status'] == 'ativo')
    leiloes_finalizados = sum(1 for l in leiloes.values() if l['status'] == 'finalizado')
    
    return jsonify({
        "usuarios": len(usuarios),
        "leiloes_total": len(leiloes),
        "leiloes_ativos": leiloes_ativos,
        "leiloes_finalizados": leiloes_finalizados,
        "lances_total": len(lances),
        "mensagens_na_fila": len(fila)
    }), 200

# ==================== EXECUÇÃO ====================

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Sistema de Leilão Online")
    print("=" * 50)
    print("API Flask iniciada em http://localhost:5000")
    print("\nEndpoints disponíveis:")
    print("  GET  /usuarios")
    print("  POST /usuarios")
    print("  GET  /leiloes")
    print("  POST /leiloes")
    print("  POST /lances")
    print("  GET  /lances/<leilao_id>")
    print("  GET  /fila (debug)")
    print("  GET  /status")
    print("=" * 50)
    app.run(debug=True, port=5000)