from datetime import date, datetime, time

from banco import conectar, inicializar_banco

inicializar_banco()


class _TatuagensCache(list):
    def clear(self):
        conexao = conectar()
        try:
            conexao.execute("DELETE FROM passos")
            conexao.execute("DELETE FROM tatuagens")
            conexao.execute("DELETE FROM sqlite_sequence WHERE name IN ('tatuagens', 'passos')")
            conexao.commit()
        finally:
            conexao.close()
        super().clear()


# Mantém a compatibilidade com os testes e com trechos legados do projeto.
_tatuagens = _TatuagensCache()


def _normalizar_passo(row):
    if row is None:
        return None
    passo = {
        "id": row["id"],
        "tatuagem_id": row["tatuagem_id"],
        "tipo": row["tipo"],
        "data": row["data"],
        "horario": row["horario"],
        "duracao_horas": row["duracao_horas"],
        "observacao": row["observacao"],
        "imagem": row["imagem"],
        "situacao": row["situacao"],
    }
    if passo["data"] is not None and isinstance(passo["data"], str):
        passo["data"] = date.fromisoformat(passo["data"])
    if passo["horario"] is not None and isinstance(passo["horario"], str):
        try:
            passo["horario"] = time.fromisoformat(passo["horario"])
        except ValueError:
            passo["horario"] = datetime.strptime(passo["horario"], "%H:%M").time()
    return passo


def _normalizar_tatuagem(row, passos=None):
    if row is None:
        return None
    tatuagem = {
        "id": row["id"],
        "ideia": row["ideia"],
        "local_corpo": row["local_corpo"],
        "tamanho": row["tamanho"],
        "cliente_id": row["cliente_id"],
        "etapa": row["etapa"],
        "imagem_referencia": row["imagem_referencia"],
        "passos": passos or [],
    }
    return tatuagem


def _sincronizar_cache():
    global _tatuagens
    _tatuagens[:] = listar_tatuagens()


def _serializar_dados_passo(dados):
    serializado = dict(dados)
    if serializado.get("data") is not None and hasattr(serializado["data"], "isoformat"):
        serializado["data"] = serializado["data"].isoformat()
    if serializado.get("horario") is not None and hasattr(serializado["horario"], "strftime"):
        serializado["horario"] = serializado["horario"].strftime("%H:%M")
    return serializado


def listar_tatuagens():
    conexao = conectar()
    try:
        linhas = conexao.execute(
            "SELECT * FROM tatuagens ORDER BY id DESC"
        ).fetchall()
        tatuagens = []
        for linha in linhas:
            passos = conexao.execute(
                "SELECT * FROM passos WHERE tatuagem_id = ? ORDER BY id ASC",
                (linha["id"],),
            ).fetchall()
            tatuagens.append(_normalizar_tatuagem(linha, [_normalizar_passo(passo) for passo in passos]))
        return tatuagens
    finally:
        conexao.close()


def buscar_tatuagem_por_id(tatuagem_id):
    conexao = conectar()
    try:
        linha = conexao.execute(
            "SELECT * FROM tatuagens WHERE id = ?",
            (int(tatuagem_id),),
        ).fetchone()
        if linha is None:
            return None
        passos = conexao.execute(
            "SELECT * FROM passos WHERE tatuagem_id = ? ORDER BY id ASC",
            (linha["id"],),
        ).fetchall()
        return _normalizar_tatuagem(linha, [_normalizar_passo(passo) for passo in passos])
    finally:
        conexao.close()


def adicionar_tatuagem(dados):
    conexao = conectar()
    try:
        cursor = conexao.execute(
            """
            INSERT INTO tatuagens (ideia, local_corpo, tamanho, cliente_id, etapa, imagem_referencia)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                dados["ideia"],
                dados["local_corpo"],
                dados["tamanho"],
                dados["cliente_id"],
                dados["etapa"],
                dados.get("imagem_referencia"),
            ),
        )
        conexao.commit()
        tatuagem_id = cursor.lastrowid
        tatuagem = buscar_tatuagem_por_id(tatuagem_id)
        _sincronizar_cache()
        return tatuagem
    finally:
        conexao.close()


def atualizar_pedido(tatuagem_id, dados):
    conexao = conectar()
    try:
        conexao.execute(
            """
            UPDATE tatuagens
            SET ideia = ?, local_corpo = ?, tamanho = ?, imagem_referencia = ?
            WHERE id = ?
            """,
            (
                dados.get("ideia"),
                dados.get("local_corpo"),
                dados.get("tamanho"),
                dados.get("imagem_referencia"),
                tatuagem_id,
            ),
        )
        conexao.commit()
        tatuagem = buscar_tatuagem_por_id(tatuagem_id)
        _sincronizar_cache()
        return tatuagem
    finally:
        conexao.close()


def listar_passos(tatuagem_id):
    tatuagem = buscar_tatuagem_por_id(tatuagem_id)
    if tatuagem is None:
        return None
    return tatuagem["passos"]


def adicionar_passo(tatuagem_id, dados):
    serializado = _serializar_dados_passo(dados)
    conexao = conectar()
    try:
        cursor = conexao.execute(
            """
            INSERT INTO passos (
                tatuagem_id, tipo, data, horario, duracao_horas, observacao, imagem, situacao
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                tatuagem_id,
                serializado["tipo"],
                serializado.get("data"),
                serializado.get("horario"),
                serializado.get("duracao_horas"),
                serializado.get("observacao"),
                serializado.get("imagem"),
                serializado.get("situacao") or ("agendada" if serializado["tipo"] in ("sessao", "retoque_combinado") else None),
            ),
        )
        conexao.commit()
        passo_id = cursor.lastrowid
        passo = conexao.execute("SELECT * FROM passos WHERE id = ?", (passo_id,)).fetchone()
        resultado = _normalizar_passo(passo)
        _sincronizar_cache()
        return resultado
    finally:
        conexao.close()


def atualizar_etapa(tatuagem_id, etapa):
    conexao = conectar()
    try:
        conexao.execute(
            "UPDATE tatuagens SET etapa = ? WHERE id = ?",
            (etapa, tatuagem_id),
        )
        conexao.commit()
        _sincronizar_cache()
    finally:
        conexao.close()


def atualizar_situacao_passo(passo_id, situacao):
    conexao = conectar()
    try:
        conexao.execute(
            "UPDATE passos SET situacao = ? WHERE id = ?",
            (situacao, passo_id),
        )
        conexao.commit()
        _sincronizar_cache()
    finally:
        conexao.close()


def atualizar_situacao_passo_com_obs(passo_id, situacao, observacao=None):
    conexao = conectar()
    try:
        if observacao is None:
            conexao.execute(
                "UPDATE passos SET situacao = ? WHERE id = ?",
                (situacao, passo_id),
            )
        else:
            conexao.execute(
                "UPDATE passos SET situacao = ?, observacao = ? WHERE id = ?",
                (situacao, observacao, passo_id),
            )
        conexao.commit()
        _sincronizar_cache()
    finally:
        conexao.close()


# Ajusta o cache legado para manter compatibilidade com testes e scripts de apoio.
_sincronizar_cache()
