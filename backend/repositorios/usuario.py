from banco import conectar, inicializar_banco
from seguranca_senhas import verificar_senha

inicializar_banco()


def _row_para_usuario(row):
    if row is None:
        return None
    return {
        "id": row["id"],
        "nome": row["nome"],
        "tipo": row["tipo"],
        "username": row["username"],
    }


def buscar_usuario_por_id(usuario_id):
    conexao = conectar()
    try:
        linha = conexao.execute(
            "SELECT id, nome, tipo, username FROM usuarios WHERE id = ?",
            (int(usuario_id),),
        ).fetchone()
        return _row_para_usuario(linha)
    finally:
        conexao.close()


def autenticar(username, password):
    username_normalizado = (username or "").strip().lower()
    conexao = conectar()
    try:
        linha = conexao.execute(
            "SELECT id, nome, tipo, username, password_hash FROM usuarios WHERE username = ?",
            (username_normalizado,),
        ).fetchone()
        if linha is None or not verificar_senha(password or "", linha["password_hash"]):
            return None
        return _row_para_usuario(linha)
    finally:
        conexao.close()
