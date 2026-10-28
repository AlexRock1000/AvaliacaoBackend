"""Catálogo inicial dos grupos e das permissões do sistema."""

# GRUPOS E PERMISSÕES: estas chaves identificam operações protegidas pelas rotas.
PERMISSAO_CONSULTAR_PROPRIA_CONTA = "conta:consultar_propria"
PERMISSAO_CONSULTAR_HORARIOS = "agenda:consultar_horarios"
PERMISSAO_LISTAR_TATUAGENS = "tatuagens:listar"
PERMISSAO_LISTAR_TODAS_TATUAGENS = "tatuagens:listar_todas"
PERMISSAO_CONSULTAR_TATUAGEM = "tatuagens:consultar_detalhe"
PERMISSAO_CRIAR_TATUAGEM = "tatuagens:criar"
PERMISSAO_EDITAR_PEDIDO = "tatuagens:editar_pedido"
PERMISSAO_LISTAR_PASSOS = "passos:listar"
PERMISSAO_REGISTRAR_PASSO = "passos:registrar"
PERMISSAO_DECIDIR_DESENHO = "passos:decidir_desenho"
PERMISSAO_ATUALIZAR_SESSAO = "sessoes:atualizar_situacao"
PERMISSAO_AGENDAR_RETOQUE = "retoques:atualizar_agendamento"
PERMISSAO_CADASTRAR_TATUADOR = "contas:cadastrar_tatuador"

# GRUPOS E PERMISSÕES: descrições usadas para cadastrar o catálogo no SQLite.
PERMISSOES_CADASTRO = {
    PERMISSAO_CONSULTAR_PROPRIA_CONTA: "Consultar a própria identidade autenticada.",
    PERMISSAO_CONSULTAR_HORARIOS: "Consultar horários disponíveis na agenda.",
    PERMISSAO_LISTAR_TATUAGENS: "Listar tatuagens dentro do escopo permitido ao grupo.",
    PERMISSAO_LISTAR_TODAS_TATUAGENS: "Consultar tatuagens de qualquer cliente do estúdio.",
    PERMISSAO_CONSULTAR_TATUAGEM: "Consultar detalhes de uma tatuagem autorizada.",
    PERMISSAO_CRIAR_TATUAGEM: "Criar pedidos de tatuagem.",
    PERMISSAO_EDITAR_PEDIDO: "Editar pedidos próprios ainda não iniciados.",
    PERMISSAO_LISTAR_PASSOS: "Consultar o histórico de passos de uma tatuagem autorizada.",
    PERMISSAO_REGISTRAR_PASSO: "Registrar desenhos, sessões e demais passos do estúdio.",
    PERMISSAO_DECIDIR_DESENHO: "Aprovar o desenho ou solicitar ajustes.",
    PERMISSAO_ATUALIZAR_SESSAO: "Atualizar a situação de uma sessão.",
    PERMISSAO_AGENDAR_RETOQUE: "Ajustar o agendamento de um retoque.",
    PERMISSAO_CADASTRAR_TATUADOR: "Criar contas para outros tatuadores do estúdio.",
}

# GRUPOS E PERMISSÕES: cada persona recebe um grupo e somente as permissões listadas.
GRUPOS_CADASTRO = {
    "cliente": {
        "nome": "Cliente",
        "permissoes": (
            PERMISSAO_CONSULTAR_PROPRIA_CONTA,
            PERMISSAO_CONSULTAR_HORARIOS,
            PERMISSAO_LISTAR_TATUAGENS,
            PERMISSAO_CONSULTAR_TATUAGEM,
            PERMISSAO_CRIAR_TATUAGEM,
            PERMISSAO_EDITAR_PEDIDO,
            PERMISSAO_LISTAR_PASSOS,
            PERMISSAO_DECIDIR_DESENHO,
        ),
    },
    "tatuador": {
        "nome": "Tatuador",
        "permissoes": (
            PERMISSAO_CONSULTAR_PROPRIA_CONTA,
            PERMISSAO_CONSULTAR_HORARIOS,
            PERMISSAO_LISTAR_TATUAGENS,
            PERMISSAO_LISTAR_TODAS_TATUAGENS,
            PERMISSAO_CONSULTAR_TATUAGEM,
            PERMISSAO_LISTAR_PASSOS,
            PERMISSAO_REGISTRAR_PASSO,
            PERMISSAO_ATUALIZAR_SESSAO,
            PERMISSAO_AGENDAR_RETOQUE,
            PERMISSAO_CADASTRAR_TATUADOR,
        ),
    },
}
