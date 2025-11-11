import json
import os
from typing import Any, Dict, List

DATA_DIR = "data"

def garantir_diretorio():
    """Cria o diretório data se não existir"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def ler_json(arquivo: str) -> Any:
    """
    Lê um arquivo JSON e retorna seu conteúdo.
    Se o arquivo não existir, retorna estrutura vazia apropriada.
    """
    garantir_diretorio()
    caminho = os.path.join(DATA_DIR, arquivo)
    
    if not os.path.exists(caminho):
        # Retorna estrutura vazia baseada no nome do arquivo
        if arquivo == "lances.json" or arquivo == "fila_sqs.json":
            return []
        return {}
    
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        # Se arquivo está corrompido, retorna estrutura vazia
        if arquivo == "lances.json" or arquivo == "fila_sqs.json":
            return []
        return {}

def escrever_json(arquivo: str, dados: Any):
    """Escreve dados em um arquivo JSON"""
    garantir_diretorio()
    caminho = os.path.join(DATA_DIR, arquivo)
    
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)

def adicionar_a_fila(mensagem: Dict):
    """Adiciona uma mensagem à fila SQS simulada"""
    fila = ler_json("fila_sqs.json")
    fila.append(mensagem)
    escrever_json("fila_sqs.json", fila)

def consumir_fila() -> List[Dict]:
    """
    Consome todas as mensagens da fila e retorna.
    Limpa a fila após consumir.
    """
    fila = ler_json("fila_sqs.json")
    if fila:
        escrever_json("fila_sqs.json", [])  # Limpa a fila
    return fila

def adicionar_lance(lance: Dict):
    """Adiciona um lance ao histórico"""
    lances = ler_json("lances.json")
    lances.append(lance)
    escrever_json("lances.json", lances)

def atualizar_leilao(leilao_id: str, dados: Dict):
    """Atualiza dados de um leilão específico"""
    leiloes = ler_json("leiloes.json")
    if leilao_id in leiloes:
        leiloes[leilao_id].update(dados)
        escrever_json("leiloes.json", leiloes)
        return True
    return False

def atualizar_usuario(usuario_id: str, dados: Dict):
    """Atualiza dados de um usuário específico"""
    usuarios = ler_json("usuarios.json")
    if usuario_id in usuarios:
        usuarios[usuario_id].update(dados)
        escrever_json("usuarios.json", usuarios)
        return True
    return False