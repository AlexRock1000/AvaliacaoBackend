// Mantém em um só lugar o endereço local da API usada durante o desenvolvimento.
export const ENDERECO_API = import.meta.env.DEV ? "" : "http://localhost:8000";

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
  return fetch(`${ENDERECO_API}${caminho}`, montarOpcoesAutenticadas(opcoes)).then((resposta) => {
    if (resposta.ok) {
      return resposta.json();
    }

    return resposta.json().then((dados) => {
      const erroTamanho = Array.isArray(dados.detail)
        ? dados.detail.find((erro) => erro.loc?.includes("tamanho"))
        : null;
      const mensagem = typeof dados.detail === "string"
        ? dados.detail
        : erroTamanho
          ? "Informe o tamanho usando apenas números positivos, em centímetros."
          : "Não foi possível concluir a solicitação. Confira os dados e tente novamente.";
      const erro = new Error(mensagem);
      if (erroTamanho) erro.campo = "tamanho";
      throw erro;
    });
  });
}
