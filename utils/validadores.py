from datetime import datetime
from typing import Dict, Tuple
from utils.storage import ler_json

def validar_usuario_existe(usuario_id: str) -> Tuple[bool, str]:
    """Verifica se o usuário existe"""
    usuarios = ler_json("usuarios.json")
    if usuario_id not in usuarios:
        return False, "Usuário não encontrado"
    return True, ""

def validar_leilao_existe(leilao_id: str) -> Tuple[bool, str]:
    """Verifica se o leilão existe"""
    leiloes = ler_json("leiloes.json")
    if leilao_id not in leiloes:
        return False, "Leilão não encontrado"
    return True, ""

def validar_leilao_ativo(leilao_id: str) -> Tuple[bool, str]:
    """Verifica se o leilão está ativo"""
    leiloes = ler_json("leiloes.json")
    leilao = leiloes.get(leilao_id)
    
    if not leilao:
        return False, "Leilão não encontrado"
    
    if leilao["status"] != "ativo":
        return False, f"Leilão está {leilao['status']}"
    
    # Verifica se já passou da data fim
    data_fim = datetime.fromisoformat(leilao["data_fim"])
    if datetime.now() > data_fim:
        return False, "Leilão já foi encerrado"
    
    return True, ""

def validar_valor_lance(leilao_id: str, valor: float) -> Tuple[bool, str]:
    """Valida se o valor do lance é válido"""
    leiloes = ler_json("leiloes.json")
    leilao = leiloes.get(leilao_id)
    
    if not leilao:
        return False, "Leilão não encontrado"
    
    preco_atual = leilao["preco_atual"]
    incremento_minimo = preco_atual * 0.05  # 5% de incremento mínimo
    
    if valor <= preco_atual:
        return False, f"Lance deve ser maior que o valor atual (R$ {preco_atual:.2f})"
    
    if valor < preco_atual + incremento_minimo:
        return False, f"Lance deve ser no mínimo R$ {incremento_minimo:.2f} maior que o valor atual"
    
    return True, ""

def validar_saldo_usuario(usuario_id: str, valor: float) -> Tuple[bool, str]:
    """Verifica se o usuário tem saldo suficiente"""
    usuarios = ler_json("usuarios.json")
    usuario = usuarios.get(usuario_id)
    
    if not usuario:
        return False, "Usuário não encontrado"
    
    if usuario["saldo"] < valor:
        return False, f"Saldo insuficiente. Disponível: R$ {usuario['saldo']:.2f}"
    
    return True, ""

def validar_lance_completo(leilao_id: str, usuario_id: str, valor: float) -> Tuple[bool, str]:
    """Executa todas as validações de um lance"""
    
    # Valida usuário
    valido, msg = validar_usuario_existe(usuario_id)
    if not valido:
        return False, msg
    
    # Valida leilão
    valido, msg = validar_leilao_existe(leilao_id)
    if not valido:
        return False, msg
    
    # Valida se leilão está ativo
    valido, msg = validar_leilao_ativo(leilao_id)
    if not valido:
        return False, msg
    
    # Valida valor do lance
    valido, msg = validar_valor_lance(leilao_id, valor)
    if not valido:
        return False, msg
    
    # Valida saldo
    valido, msg = validar_saldo_usuario(usuario_id, valor)
    if not valido:
        return False, msg
    
    return True, "Lance válido"