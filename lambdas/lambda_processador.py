"""
Lambda 1: Processador de Lances
Consome mensagens da fila SQS, valida e processa lances
"""

import sys
import os
import time
from datetime import datetime

# Adiciona o diretório raiz ao path para importar utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.storage import (
    consumir_fila, adicionar_lance, 
    atualizar_leilao, ler_json
)
from utils.validadores import validar_lance_completo

def processar_lance(mensagem):
    """
    Processa uma mensagem de lance da fila.
    Valida e atualiza os dados se válido.
    """
    print(f"\n📨 Processando mensagem: {mensagem['mensagem_id']}")
    
    dados = mensagem['dados']
    leilao_id = dados['leilao_id']
    usuario_id = dados['usuario_id']
    valor = dados['valor']
    
    # Valida o lance completamente
    valido, mensagem_validacao = validar_lance_completo(leilao_id, usuario_id, valor)
    
    if not valido:
        print(f"❌ Lance rejeitado: {mensagem_validacao}")
        # Registra lance como rejeitado
        lance = {
            "id": f"lance_{mensagem['mensagem_id']}",
            "leilao_id": leilao_id,
            "usuario_id": usuario_id,
            "valor": valor,
            "data_hora": mensagem['timestamp'],
            "status": "rejeitado",
            "motivo": mensagem_validacao
        }
        adicionar_lance(lance)
        return False
    
    # Lance válido - processa
    print(f"✅ Lance válido! Processando...")
    
    # Adiciona lance ao histórico
    lance = {
        "id": f"lance_{mensagem['mensagem_id']}",
        "leilao_id": leilao_id,
        "usuario_id": usuario_id,
        "valor": valor,
        "data_hora": mensagem['timestamp'],
        "status": "processado"
    }
    adicionar_lance(lance)
    
    # Atualiza preço atual do leilão
    atualizar_leilao(leilao_id, {"preco_atual": valor})
    
    # Busca informações para log
    usuarios = ler_json("usuarios.json")
    leiloes = ler_json("leiloes.json")
    usuario = usuarios.get(usuario_id, {})
    leilao = leiloes.get(leilao_id, {})
    
    print(f"💰 Novo lance: R$ {valor:.2f}")
    print(f"   Usuário: {usuario.get('nome', usuario_id)}")
    print(f"   Leilão: {leilao.get('titulo', leilao_id)}")
    
    return True

def executar_processamento():
    """
    Função principal que executa continuamente,
    consumindo e processando mensagens da fila.
    """
    print("=" * 60)
    print("⚡ LAMBDA 1 - PROCESSADOR DE LANCES")
    print("=" * 60)
    print("Aguardando mensagens na fila...")
    print("Pressione Ctrl+C para parar\n")
    
    total_processados = 0
    total_rejeitados = 0
    
    try:
        while True:
            # Consome todas as mensagens da fila
            mensagens = consumir_fila()
            
            if mensagens:
                print(f"\n🔔 {len(mensagens)} nova(s) mensagem(ns) na fila")
                
                for mensagem in mensagens:
                    if mensagem['tipo'] == 'novo_lance':
                        sucesso = processar_lance(mensagem)
                        if sucesso:
                            total_processados += 1
                        else:
                            total_rejeitados += 1
                
                print(f"\n📊 Estatísticas:")
                print(f"   Processados: {total_processados}")
                print(f"   Rejeitados: {total_rejeitados}")
            
            # Aguarda 2 segundos antes de verificar novamente
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Processador finalizado pelo usuário")
        print(f"Total processado: {total_processados} lances")
        print(f"Total rejeitado: {total_rejeitados} lances")

if __name__ == "__main__":
    executar_processamento()