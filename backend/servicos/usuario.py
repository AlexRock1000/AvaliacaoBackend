from esquemas.usuario import UsuarioCadastroEntrada
from modelos.usuario import Usuario
from repositorios import usuario as repositorio_usuario
from seguranca import hashear_senha


def cadastrar_usuario(entrada: UsuarioCadastroEntrada):
    """Cria uma conta de cliente com senha protegida e perfil não controlado pelo usuário."""
    email = str(entrada.email).strip().lower()
    conta = Usuario(
        nome=entrada.nome.strip(),
        tipo="cliente",
        username=email,
        email=email,
        senha_hash=hashear_senha(entrada.senha),
    )
    try:
        return repositorio_usuario.salvar(conta)
    except ValueError as erro:
        raise ValueError("Já existe uma conta com esse email.") from erro


def autenticar_usuario(username: str | None, email: str | None, senha: str):
    """Valida credenciais e mantém compatibilidade com logins pelo username legado."""
    identificador = email or username or ""
    return repositorio_usuario.autenticar(identificador, senha)
