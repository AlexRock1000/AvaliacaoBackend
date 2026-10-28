"""Consultas de autorização dos grupos persistidos no banco local."""

from banco import conectar


# GRUPOS E PERMISSÕES: retorna as permissões efetivas do grupo associado à conta.
def listar_permissoes_usuario(usuario_id: int) -> set[str]:
    conexao = conectar()
    try:
        linhas = conexao.execute(
            """
            SELECT permissoes.codigo
            FROM usuario_grupos
            JOIN grupo_permissoes
              ON grupo_permissoes.grupo_id = usuario_grupos.grupo_id
            JOIN permissoes
              ON permissoes.id = grupo_permissoes.permissao_id
            WHERE usuario_grupos.usuario_id = %s
            """,
            (int(usuario_id),),
        ).fetchall()
        return {linha["codigo"] for linha in linhas}
    finally:
        conexao.close()
