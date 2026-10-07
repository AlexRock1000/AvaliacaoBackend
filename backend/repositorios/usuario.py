from banco import conectar, inicializar_banco

inicializar_banco()


def _row_para_usuario(row):
    if row is None:
        return None
    return {
        "id": row["id"],
        "nome": row["nome"],
        "tipo": row["tipo"],
        "username": row["username"],
        "password": row["password"],
    }


def buscar_usuario_por_id(usuario_id):
    conexao = conectar()
    try:
        linha = conexao.execute(
            "SELECT id, nome, tipo, username, password FROM usuarios WHERE id = ?",
            (int(usuario_id),),
        ).fetchone()
        return _row_para_usuario(linha)
    finally:
        conexao.close()


def autenticar(username, password):
    username_normalizado = (username or "").strip().lower()
    password_normalizado = password or ""
    conexao = conectar()
    try:
        linha = conexao.execute(
            "SELECT id, nome, tipo, username, password FROM usuarios WHERE username = ? AND password = ?",
            (username_normalizado, password_normalizado),
        ).fetchone()
        return _row_para_usuario(linha)
    finally:
        conexao.close()
