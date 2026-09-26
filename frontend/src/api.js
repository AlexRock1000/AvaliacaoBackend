// Mantém em um só lugar o endereço local da API usada durante o desenvolvimento.
const ENDERECO_API = "http://localhost:8000";


// Confere o status HTTP antes de entregar os dados para a tela.
export function pedirApi(caminho, opcoes = {}) {
  return fetch(`${ENDERECO_API}${caminho}`, opcoes).then((resposta) =>
    resposta.json().then((dados) => {
      if (!resposta.ok) {
        throw new Error(dados.detail || "Não foi possível concluir a solicitação.");
      }

      return dados;
    }),
  );
}
