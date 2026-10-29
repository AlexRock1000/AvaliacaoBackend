from sqlalchemy.exc import IntegrityError

from banco import conectar, inicializar_banco
from modelos.usuario import Usuario, usuario_da_linha

inicializar_banco()


# GRUPOS E PERMISSÕES: centraliza o JOIN usado para devolver o grupo associado.
_CONSULTA_USUARIO_COM_GRUPO = """
    SELECT usuarios.*,
           grupos.id AS grupo_id,
           grupos.codigo AS grupo_codigo,
           grupos.nome AS grupo_nome
    FROM usuarios
    LEFT JOIN usuario_grupos ON usuario_grupos.usuario_id = usuarios.id
    LEFT JOIN grupos ON grupos.id = usuario_grupos.grupo_id
"""


def buscar_usuario_por_id(usuario_id) -> dict | None:
    """Busca uma conta por identificador sem expor seu hash de senha."""
    conexao = conectar()
    try:
        # GRUPOS E PERMISSÕES: /me recebe a associação atual persistida da conta.
        linha = conexao.execute(
            _CONSULTA_USUARIO_COM_GRUPO + " WHERE usuarios.id = %s",
            (int(usuario_id),),
        ).fetchone()
        usuario = usuario_da_linha(linha)
        return usuario.para_publico() if usuario else None
    finally:
        conexao.close()


def buscar_por_email(email: str) -> Usuario | None:
    """Busca modelo interno pelo e-mail normalizado, incluindo hash privado."""
    conexao = conectar()
    try:
        # GRUPOS E PERMISSÕES: o login também carrega o grupo para uso do serviço.
        linha = conexao.execute(
            _CONSULTA_USUARIO_COM_GRUPO + " WHERE LOWER(usuarios.email) = %s",
            (email.strip().lower(),),
        ).fetchone()
        return usuario_da_linha(linha)
    finally:
        conexao.close()


def buscar_por_username(username: str) -> Usuario | None:
    """Busca modelo interno pelo username demonstrativo ou legado."""
    conexao = conectar()
    try:
        # GRUPOS E PERMISSÕES: a busca por username mantém a mesma associação do login por e-mail.
        linha = conexao.execute(
            _CONSULTA_USUARIO_COM_GRUPO + " WHERE LOWER(usuarios.username) = %s",
            (username.strip().lower(),),
        ).fetchone()
        return usuario_da_linha(linha)
    finally:
        conexao.close()


def salvar(usuario: Usuario) -> Usuario:
    """Persiste usuário já validado e hasheado pelo serviço."""
    conexao = conectar()
    try:
        # GRUPOS E PERMISSÕES: só permite salvar se houver grupo correspondente à persona.
        grupo = conexao.execute(
            "SELECT id FROM grupos WHERE codigo = %s", (usuario.tipo,)
        ).fetchone()
        if grupo is None:
            raise ValueError("Não existe grupo cadastrado para esta persona.")

        cursor = conexao.execute(
            """
            INSERT INTO usuarios (nome, tipo, username, email, senha_hash)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
            """,
            (usuario.nome, usuario.tipo, usuario.username, usuario.email, usuario.senha_hash),
        )
        # GRUPOS E PERMISSÕES: vínculo único garante que cada conta pertença a um grupo.
        usuario_id = cursor.fetchone()["id"]
        conexao.execute(
            "INSERT INTO usuario_grupos (usuario_id, grupo_id) VALUES (%s, %s)",
            (usuario_id, grupo["id"]),
        )
        conexao.commit()
        linha = conexao.execute(
            _CONSULTA_USUARIO_COM_GRUPO + " WHERE usuarios.id = %s",
            (usuario_id,),
        ).fetchone()
        salvo = usuario_da_linha(linha)
        if salvo is None:
            raise RuntimeError("Não foi possível recuperar o usuário salvo.")
        return salvo
    except IntegrityError as erro:
        conexao.rollback()
        raise ValueError("Este e-mail já está cadastrado.") from erro
    finally:
        conexao.close()
