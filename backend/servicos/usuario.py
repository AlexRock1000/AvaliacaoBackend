from modelos.usuario import Usuario
from repositorios import usuario as repositorio_usuario
from seguranca import hashear_senha, verificar_senha


def _cadastrar_com_tipo(nome: str, email: str, senha: str, tipo: str) -> dict:
    nome_normalizado = nome.strip()
    email_normalizado = email.strip().lower()
    if repositorio_usuario.buscar_por_email(email_normalizado):
        raise ValueError("Este e-mail já está cadastrado.")

    usuario = Usuario(
        id=None,
        nome=nome_normalizado,
        tipo=tipo,
        username=email_normalizado,
        email=email_normalizado,
        senha_hash=hashear_senha(senha),
    )
    return repositorio_usuario.salvar(usuario).para_publico()


def cadastrar(nome: str, email: str, senha: str) -> dict:
    """Cria conta cliente; o tipo de perfil não é controlado pelo formulário."""
    return _cadastrar_com_tipo(nome, email, senha, "cliente")


def cadastrar_tatuador(nome: str, email: str, senha: str) -> dict:
    """Cria conta de tatuador para uso exclusivo da rota protegida da equipe."""
    return _cadastrar_com_tipo(nome, email, senha, "tatuador")


def autenticar(identificador: str, senha: str) -> dict | None:
    """Autentica com e-mail ou username das contas legadas de demonstração."""
    valor = (identificador or "").strip().lower()
    usuario = (
        repositorio_usuario.buscar_por_email(valor)
        if "@" in valor
        else repositorio_usuario.buscar_por_username(valor)
    )
    if usuario is None or not verificar_senha(senha or "", usuario.senha_hash):
        return None
    return usuario.para_publico()


def buscar_por_id(usuario_id) -> dict | None:
    """Recupera somente os campos públicos de um usuário autenticado."""
    if usuario_id is None:
        return None
    try:
        return repositorio_usuario.buscar_usuario_por_id(usuario_id)
    except (TypeError, ValueError):
        return None
