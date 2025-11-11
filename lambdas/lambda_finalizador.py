"""
Lambda 2: Finalizador de Leilões
Verifica leilões expirados e define vencedores
"""

import sys
import os
import time
from datetime import datetime

# Adiciona o diretório raiz ao path para importar utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.storage import ler_json, atualizar_leilao

def obter_ultimo_lance_vencedor(leilao_id):
    """
    Retorna o último lance processado do leilão
    (que representa o maior lance vencedor)
    """
    lances = ler_json("lances.json")
    
    # Filtra lances processados do leilão
    lances_validos = [
        lance for lance in lances
        if lance.get('leilao_id') == leilao_id 
        and lance.get('status') == 'processado'
    ]
    
    if not lances_validos:
        return None
    
    # Ordena por data e retorna o mais recente
    lances_validos.sort(key=lambda x: x.get('data_hora', ''))
    return lances_validos[-1]

def finalizar_leilao(leilao_id, leilao):
    """
    Finaliza um leilão específico, definindo o vencedor
    """
    print(f"\n🔨 Finalizando leilão: {leilao['titulo']}")
    print(f"   ID: {leilao_id}")
    print(f"   Data fim: {leilao['data_fim']}")
    
    # Busca o último lance (vencedor)
    lance_vencedor = obter_ultimo_lance_vencedor(leilao_id)
    
    if lance_vencedor:
        usuario_id = lance_vencedor['usuario_id']
        valor_final = lance_vencedor['valor']
        
        # Atualiza leilão com vencedor
        atualizar_leilao(leilao_id, {
            "status": "finalizado",
            "vencedor_id": usuario_id,
            "preco_atual": valor_final
        })
        
        # Busca informações do vencedor
        usuarios = ler_json("usuarios.json")
        vencedor = usuarios.get(usuario_id, {})
        
        print(f"🏆 VENCEDOR: {vencedor.get('nome', usuario_id)}")
        print(f"   Valor final: R$ {valor_final:.2f}")
        
    else:
        # Nenhum lance foi feito
        atualizar_leilao(leilao_id, {
            "status": "finalizado",
            "vencedor_id": None
        })
        print(f"📭 Leilão finalizado sem lances")

def verificar_leiloes_expirados():
    """
    Verifica todos os leilões ativos e finaliza os que expiraram
    """
    print("\n🔍 Verificando leilões expirados...")
    
    leiloes = ler_json("leiloes.json")
    agora = datetime.now()
    
    leiloes_finalizados = 0
    
    for leilao_id, leilao in leiloes.items():
        # Verifica apenas leilões ativos
        if leilao['status'] != 'ativo':
            continue
        
        # Verifica se já passou da data fim
        data_fim = datetime.fromisoformat(leilao['data_fim'])
        
        if agora > data_fim:
            finalizar_leilao(leilao_id, leilao)
            leiloes_finalizados += 1
    
    if leiloes_finalizados == 0:
        print("✓ Nenhum leilão expirado encontrado")
    else:
        print(f"\n📊 Total de leilões finalizados: {leiloes_finalizados}")
    
    return leiloes_finalizados

def executar_finalizador(modo='continuo'):
    """
    Executa o finalizador de leilões.
    
    Modos:
    - 'continuo': executa a cada 10 segundos indefinidamente
    - 'unico': executa uma vez e encerra
    """
    print("=" * 60)
    print("⚡ LAMBDA 2 - FINALIZADOR DE LEILÕES")
    print("=" * 60)
    
    if modo == 'continuo':
        print("Modo: Execução contínua (a cada 10 segundos)")
        print("Pressione Ctrl+C para parar\n")
        
        try:
            while True:
                verificar_leiloes_expirados()
                print("\n⏳ Aguardando 10 segundos...\n")
                time.sleep(10)
        
        except KeyboardInterrupt:
            print("\n\n🛑 Finalizador parado pelo usuário")
    
    else:
        print("Modo: Execução única\n")
        verificar_leiloes_expirados()
        print("\n✓ Execução concluída")

def executar_agora():
    """
    Executa uma verificação imediata (útil para testes)
    """
    print("⚡ Executando verificação imediata...")
    verificar_leiloes_expirados()

if __name__ == "__main__":
    # Verifica argumentos de linha de comando
    if len(sys.argv) > 1:
        if sys.argv[1] == '--once' or sys.argv[1] == '-o':
            executar_finalizador('unico')
        elif sys.argv[1] == '--now' or sys.argv[1] == '-n':
            executar_agora()
        else:
            print("Uso:")
            print("  python lambda_finalizador.py           (modo contínuo)")
            print("  python lambda_finalizador.py --once    (executa uma vez)")
            print("  python lambda_finalizador.py --now     (verificação imediata)")
    else:
        executar_finalizador('continuo')