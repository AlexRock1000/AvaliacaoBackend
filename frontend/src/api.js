// O endereço da API vem do .env.development ou do .env.production.
export const URL_DA_API = import.meta.env.VITE_URL_DA_API ?? "";

function obterToken() {
  return localStorage.getItem("tinta_negra_token") || "";
}

function montarOpcoesAutenticadas(opcoes = {}) {
  const token = obterToken();
  const headers = new Headers(opcoes.headers || {});

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  return {
    ...opcoes,
    headers,
  };
}

// Confere o status HTTP antes de entregar os dados para a tela.
export function pedirApi(caminho, opcoes = {}) {
  return fetch(`${URL_DA_API}${caminho}`, montarOpcoesAutenticadas(opcoes)).then(async (resposta) => {
    if (resposta.ok) {
      return resposta.json();
    }

    if (resposta.status === 401) {
      localStorage.removeItem("tinta_negra_token");
      localStorage.removeItem("tinta_negra_usuario");
      window.dispatchEvent(new Event("tinta-negra-sessao-expirada"));
    }

    const dados = await resposta.json().catch(() => ({}));
    const erroTamanho = Array.isArray(dados.detail)
      ? dados.detail.find((erro) => erro.loc?.includes("tamanho"))
      : null;
    const mensagem = typeof dados.detail === "string"
      ? dados.detail
      : erroTamanho
        ? "Informe o tamanho usando apenas números positivos, em centímetros."
        : "Não foi possível concluir a solicitação. Confira os dados e tente novamente.";
    const erro = new Error(mensagem);
    erro.status = resposta.status;
    if (erroTamanho) erro.campo = "tamanho";
    throw erro;
  });
}
