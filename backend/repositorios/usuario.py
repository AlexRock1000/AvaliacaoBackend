_usuarios = {
    1: {
        "id": 1,
        "nome": "Bruna",
        "tipo": "cliente",
        "username": "bruna",
        "password": "bruna123",
    },
    2: {
        "id": 2,
        "nome": "Vitor",
        "tipo": "tatuador",
        "username": "vitor",
        "password": "vitor123",
    },
}


def buscar_usuario_por_id(usuario_id):
    usuario = _usuarios.get(int(usuario_id))
    if usuario is None:
        return None
    return {**usuario}


def autenticar(username, password):
    username_normalizado = (username or "").strip().lower()
    password_normalizado = password or ""
    for usuario in _usuarios.values():
        if usuario["username"] == username_normalizado and usuario["password"] == password_normalizado:
            return {**usuario}
    return None
