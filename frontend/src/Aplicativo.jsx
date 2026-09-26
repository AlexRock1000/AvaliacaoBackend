import { useEffect, useState } from "react";

import { pedirApi } from "./api.js";

const PERFIS = [
  { nome: "Bruna", tipo: "cliente", clienteId: 1 },
  { nome: "Vitor", tipo: "tatuador", clienteId: null },
];

const TIPOS_DE_PASSO = [
  { valor: "desenho_aprovado", nome: "Desenho aprovado" },
  { valor: "sessao", nome: "Sessão" },
  { valor: "retoque", nome: "Retoque" },
];

// Mostra a etapa com uma escrita legível para as duas pessoas do estúdio.
function nomeDaEtapa(etapa) {
  const nomes = {
    pedida: "Pedido recebido",
    "desenho aprovado": "Desenho aprovado",
    "em sessões": "Em sessões",
    finalizada: "Finalizada",
  };
  return nomes[etapa] || etapa;
}

// Exibe a tela de pedido para a cliente e mostra recusas da API no próprio formulário.
function TelaPedir({ perfil, aoCriar }) {
  const [ideia, definirIdeia] = useState("");
  const [localCorpo, definirLocalCorpo] = useState("");
  const [tamanho, definirTamanho] = useState("");
  const [enviando, definirEnviando] = useState(false);
  const [erro, definirErro] = useState("");
  const [mensagem, definirMensagem] = useState("");

  // Envia o pedido como JSON e conserva a mensagem de recusa para a pessoa vê-la.
  function enviarPedido(evento) {
    evento.preventDefault();
    definirErro("");
    definirMensagem("");
    definirEnviando(true);

    pedirApi("/tatuagens", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ideia,
          local_corpo: localCorpo,
          tamanho,
          cliente_id: perfil.clienteId,
        }),
      })
      .then((tatuagem) => {
        definirIdeia("");
        definirLocalCorpo("");
        definirTamanho("");
        definirMensagem("Seu pedido foi recebido pelo estúdio.");
        aoCriar(tatuagem);
      })
      .catch((erroApi) => definirErro(erroApi.message))
      .finally(() => {
        definirEnviando(false);
      });
  }

  return (
    <section className="painel-formulario">
      <div className="titulo-secao">
        <span className="sobretitulo">PRIMEIRO PASSO</span>
        <h2>Conte sua ideia.</h2>
        <p>Descreva o que imaginou. A equipe acompanha seu pedido por etapa.</p>
      </div>
      <form onSubmit={enviarPedido} className="formulario">
        <label htmlFor="ideia">Sua ideia</label>
        <textarea id="ideia" value={ideia} onChange={(evento) => definirIdeia(evento.target.value)} minLength="3" required placeholder="Conte um pouco sobre o desenho que tem em mente" />
        <div className="linha-campos">
          <div>
            <label htmlFor="local">Local do corpo</label>
            <input id="local" value={localCorpo} onChange={(evento) => definirLocalCorpo(evento.target.value)} minLength="2" required placeholder="Ex.: antebraço" />
          </div>
          <div>
            <label htmlFor="tamanho">Tamanho aproximado</label>
            <input id="tamanho" value={tamanho} onChange={(evento) => definirTamanho(evento.target.value)} required placeholder="Ex.: 12 cm" />
          </div>
        </div>
        {erro && <p className="aviso aviso-erro" role="alert">{erro}</p>}
        {mensagem && <p className="aviso aviso-sucesso" role="status">{mensagem}</p>}
        <button className="botao botao-escuro" disabled={enviando}>
          {enviando ? "Enviando pedido…" : "Enviar pedido"}<span aria-hidden="true">↗</span>
        </button>
      </form>
    </section>
  );
}

// Carrega as tatuagens da cliente e permite abrir o histórico de cada uma.
function TelaMinhasTatuagens({ perfil }) {
  const [tatuagens, definirTatuagens] = useState([]);
  const [selecionada, definirSelecionada] = useState(null);
  const [passos, definirPassos] = useState([]);
  const [carregando, definirCarregando] = useState(true);
  const [carregandoPassos, definirCarregandoPassos] = useState(false);
  const [erro, definirErro] = useState("");
  const [erroPassos, definirErroPassos] = useState("");

  // Atualiza a lista quando o perfil da pessoa muda.
  useEffect(() => {
    function carregarTatuagens() {
      definirCarregando(true);
      definirErro("");
      pedirApi(`/tatuagens?cliente_id=${perfil.clienteId}`)
        .then((dados) => definirTatuagens(dados))
        .catch((erroApi) => definirErro(erroApi.message))
        .finally(() => definirCarregando(false));
    }
    carregarTatuagens();
  }, [perfil.clienteId]);

  // Abre o histórico da tatuagem escolhida, mostrando erros da API no painel.
  function abrirHistorico(tatuagem) {
    definirSelecionada(tatuagem);
    definirPassos([]);
    definirErroPassos("");
    definirCarregandoPassos(true);
    pedirApi(`/tatuagens/${tatuagem.id}/passos`)
      .then((dados) => definirPassos(dados))
      .catch((erroApi) => definirErroPassos(erroApi.message))
      .finally(() => {
        definirCarregandoPassos(false);
      });
  }

  return (
    <section>
      <div className="titulo-secao">
        <span className="sobretitulo">SEU CAMINHO</span>
        <h2>Minhas tatuagens.</h2>
        <p>Cada desenho tem seu tempo. Acompanhe por onde ele está.</p>
      </div>
      {carregando && <p className="estado">Carregando suas tatuagens…</p>}
      {erro && <p className="aviso aviso-erro" role="alert">{erro}</p>}
      {!carregando && !erro && tatuagens.length === 0 && <p className="estado estado-vazio">Ainda não há tatuagens no seu histórico. Seu primeiro pedido começa pela tela “Pedir tatuagem”.</p>}
      <div className="grade-tatuagens">
        {tatuagens.map((tatuagem) => (
          <button key={tatuagem.id} className={`cartao-tatuagem ${selecionada?.id === tatuagem.id ? "cartao-selecionado" : ""}`} onClick={() => abrirHistorico(tatuagem)}>
            <span className="numero-cartao">ESTÚDIO · {String(tatuagem.id).padStart(2, "0")}</span>
            <strong>{tatuagem.ideia}</strong>
            <span>{tatuagem.local_corpo} · {tatuagem.tamanho}</span>
            <span className="selo-etapa"><i />{nomeDaEtapa(tatuagem.etapa)}</span>
          </button>
        ))}
      </div>
      {selecionada && (
        <div className="historico">
          <div className="historico-cabecalho"><div><span className="sobretitulo">HISTÓRICO</span><h3>{selecionada.ideia}</h3></div><span className="selo-etapa"><i />{nomeDaEtapa(selecionada.etapa)}</span></div>
          {carregandoPassos && <p className="estado">Carregando o histórico…</p>}
          {erroPassos && <p className="aviso aviso-erro" role="alert">{erroPassos}</p>}
          {!carregandoPassos && !erroPassos && passos.length === 0 && <p className="estado">Nenhum passo registrado ainda. O estúdio atualizará esta linha do tempo.</p>}
          {!carregandoPassos && passos.map((passo) => <div className="item-historico" key={passo.id}><span className="ponto-historico" /><div><strong>{TIPOS_DE_PASSO.find((tipo) => tipo.valor === passo.tipo)?.nome || passo.tipo}</strong><p>{passo.data} · {passo.observacao}</p></div></div>)}
        </div>
      )}
    </section>
  );
}

// Carrega a agenda da equipe com filtro opcional pela etapa.
function TelaAgenda({ aoAbrirFicha, atualizacao }) {
  const [tatuagens, definirTatuagens] = useState([]);
  const [etapa, definirEtapa] = useState("");
  const [carregando, definirCarregando] = useState(true);
  const [erro, definirErro] = useState("");

  // Busca a agenda sempre que o filtro ou um registro de passo muda.
  useEffect(() => {
    function carregarAgenda() {
      definirCarregando(true);
      definirErro("");
      const filtro = etapa ? `?etapa=${encodeURIComponent(etapa)}` : "";
      pedirApi(`/tatuagens${filtro}`)
        .then((dados) => definirTatuagens(dados))
        .catch((erroApi) => definirErro(erroApi.message))
        .finally(() => definirCarregando(false));
    }
    carregarAgenda();
  }, [etapa, atualizacao]);

  return (
    <section>
      <div className="cabecalho-agenda">
        <div className="titulo-secao"><span className="sobretitulo">VISÃO DO ESTÚDIO</span><h2>A agenda.</h2><p>Tatuagens em andamento, organizadas por etapa.</p></div>
        <label className="filtro-etapa">Filtrar por etapa
          <select value={etapa} onChange={(evento) => definirEtapa(evento.target.value)}>
            <option value="">Todas as etapas</option><option value="pedida">Pedido recebido</option><option value="desenho aprovado">Desenho aprovado</option><option value="em sessões">Em sessões</option><option value="finalizada">Finalizada</option>
          </select>
        </label>
      </div>
      {carregando && <p className="estado">Carregando agenda…</p>}
      {erro && <p className="aviso aviso-erro" role="alert">{erro}</p>}
      {!carregando && !erro && tatuagens.length === 0 && <p className="estado estado-vazio">Não há tatuagens nesta etapa.</p>}
      <div className="grade-tatuagens grade-agenda">
        {tatuagens.map((tatuagem) => (
          <article key={tatuagem.id} className="cartao-tatuagem cartao-agenda">
            <span className="numero-cartao">FICHA · {String(tatuagem.id).padStart(2, "0")}</span>
            <strong>{tatuagem.ideia}</strong>
            <span>{tatuagem.local_corpo} · {tatuagem.tamanho}</span>
            <span className="selo-etapa"><i />{nomeDaEtapa(tatuagem.etapa)}</span>
            <button className="botao botao-claro" onClick={() => aoAbrirFicha(tatuagem)}>Abrir ficha <span aria-hidden="true">↗</span></button>
          </article>
        ))}
      </div>
    </section>
  );
}

// Registra a aprovação do desenho, uma sessão ou um retoque na ficha escolhida.
function TelaFicha({ tatuagem, aoVoltar, aoSalvar }) {
  const [tipo, definirTipo] = useState("desenho_aprovado");
  const [data, definirData] = useState(new Date().toISOString().slice(0, 10));
  const [observacao, definirObservacao] = useState("");
  const [erro, definirErro] = useState("");
  const [salvando, definirSalvando] = useState(false);

  // Envia o novo passo e deixa a mensagem de recusa visível sem perder os dados.
  function enviarPasso(evento) {
    evento.preventDefault();
    definirErro("");
    definirSalvando(true);
    pedirApi(`/tatuagens/${tatuagem.id}/passos`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tipo, data, observacao }),
      })
      .then(() => aoSalvar())
      .catch((erroApi) => definirErro(erroApi.message))
      .finally(() => {
        definirSalvando(false);
      });
  }

  return (
    <section className="painel-formulario">
      <button className="voltar" onClick={aoVoltar}>← Voltar à agenda</button>
      <div className="titulo-secao"><span className="sobretitulo">FICHA · {String(tatuagem.id).padStart(2, "0")}</span><h2>Registrar um passo.</h2><p>{tatuagem.ideia} · {nomeDaEtapa(tatuagem.etapa)}</p></div>
      <form onSubmit={enviarPasso} className="formulario">
        <label htmlFor="tipo-passo">O que foi feito?</label>
        <select id="tipo-passo" value={tipo} onChange={(evento) => definirTipo(evento.target.value)}>{TIPOS_DE_PASSO.map((opcao) => <option key={opcao.valor} value={opcao.valor}>{opcao.nome}</option>)}</select>
        <label htmlFor="data-passo">Data</label>
        <input id="data-passo" type="date" value={data} onChange={(evento) => definirData(evento.target.value)} required />
        <label htmlFor="observacao">Observação</label>
        <textarea id="observacao" value={observacao} onChange={(evento) => definirObservacao(evento.target.value)} required placeholder="Uma nota para o histórico da tatuagem" />
        {erro && <p className="aviso aviso-erro" role="alert">{erro}</p>}
        <button className="botao botao-escuro" disabled={salvando}>{salvando ? "Salvando…" : "Salvar passo"}<span aria-hidden="true">↗</span></button>
      </form>
    </section>
  );
}

// Apresenta as quatro telas da cartilha e troca os caminhos conforme o perfil escolhido.
export default function Aplicativo() {
  const [perfilNome, definirPerfilNome] = useState("Bruna");
  const [tela, definirTela] = useState("pedir");
  const [ficha, definirFicha] = useState(null);
  const [atualizacao, definirAtualizacao] = useState(0);
  const perfil = PERFIS.find((opcao) => opcao.nome === perfilNome);

  // Muda a tela inicial para combinar com a pessoa escolhida na lista.
  function escolherPerfil(evento) {
    const nome = evento.target.value;
    definirPerfilNome(nome);
    definirFicha(null);
    definirTela(nome === "Vitor" ? "agenda" : "pedir");
  }

  // Atualiza a agenda após gravar um passo e volta para a lista de trabalho.
  function salvarPasso() {
    definirAtualizacao((valor) => valor + 1);
    definirFicha(null);
    definirTela("agenda");
  }

  return (
    <div className={`aplicativo modo-${perfil.tipo}`}>
      <header className="barra-superior">
        <a className="marca" href="#inicio" onClick={() => definirTela(perfil.tipo === "cliente" ? "pedir" : "agenda")}><img src={perfil.tipo === "cliente" ? "/imagens/logo-monocromatico.svg" : "/imagens/logo-colorido.svg"} alt="Nervo Tattoo Studio" /></a>
        <nav className="navegacao" aria-label="Navegação principal">
          {perfil.tipo === "cliente" ? <><button className={tela === "pedir" ? "ativo" : ""} onClick={() => definirTela("pedir")}>Pedir tatuagem</button><button className={tela === "minhas" ? "ativo" : ""} onClick={() => definirTela("minhas")}>Minhas tatuagens</button></> : <button className="ativo" onClick={() => { definirFicha(null); definirTela("agenda"); }}>A agenda</button>}
        </nav>
        <label className="seletor-perfil"><span>PERFIL</span><select aria-label="Escolher perfil" value={perfilNome} onChange={escolherPerfil}>{PERFIS.map((opcao) => <option key={opcao.nome} value={opcao.nome}>{opcao.nome} · {opcao.tipo}</option>)}</select></label>
      </header>
      <main id="inicio" className="conteudo-principal">
        <div className="coluna-conteudo">
          {tela === "pedir" && <TelaPedir perfil={perfil} aoCriar={() => definirAtualizacao((valor) => valor + 1)} />}
          {tela === "minhas" && <TelaMinhasTatuagens key={atualizacao} perfil={perfil} />}
          {tela === "agenda" && <TelaAgenda atualizacao={atualizacao} aoAbrirFicha={(tatuagem) => { definirFicha(tatuagem); definirTela("ficha"); }} />}
          {tela === "ficha" && ficha && <TelaFicha tatuagem={ficha} aoVoltar={() => definirTela("agenda")} aoSalvar={salvarPasso} />}
        </div>
        <aside className="painel-arte" aria-label="Arte de referência do estúdio">
          <img className="arte-imagem" src="/imagens/ornamento.jfif" alt="" />
          <div className="arte-texto"><span>{perfil.tipo === "cliente" ? "SUA JORNADA NA PELE" : "GESTÃO DO ESTÚDIO"}</span><strong>{perfil.tipo === "cliente" ? "Histórias que ficam." : <>Arte viva,<br /><em>agenda em ordem.</em></>}</strong></div>
          <div className="arte-legenda"><span>DESENHO · PELE · TEMPO</span><span>01 / ESTÚDIO</span></div>
        </aside>
      </main>
      <footer className="rodape"><span>UM PASSO DE CADA VEZ.</span><span>ESTÚDIO DE TATUAGEM · 2026</span></footer>
    </div>
  );
}
