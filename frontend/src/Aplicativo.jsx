import React, { useEffect, useState } from "react";

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
function TelaPedir({ perfil, aoCriar, aoVoltar }) {
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
      <button className="voltar" type="button" onClick={aoVoltar}>← Voltar para minhas tatuagens</button>
      <div className="titulo-secao">
        <span className="sobretitulo">UM NOVO PROJETO</span>
        <h2>Conte sua ideia.</h2>
        <p>Não precisa saber explicar tudo. Dê os primeiros detalhes e a equipe constrói o desenho com você.</p>
      </div>
      <form onSubmit={enviarPedido} className="formulario">
        <label htmlFor="ideia">O que você imagina?</label>
        <textarea id="ideia" value={ideia} onChange={(evento) => definirIdeia(evento.target.value)} minLength="3" required placeholder="Ex.: flores brasileiras e uma mariposa ao centro..." />
        <div className="linha-campos">
          <div>
            <label htmlFor="local">Local do corpo</label>
            <input id="local" value={localCorpo} onChange={(evento) => definirLocalCorpo(evento.target.value)} minLength="2" required placeholder="Ex.: costela esquerda" />
          </div>
          <div>
            <label htmlFor="tamanho">Tamanho aproximado</label>
            <input id="tamanho" value={tamanho} onChange={(evento) => definirTamanho(evento.target.value)} required placeholder="Ex.: 20 cm" />
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
    <section className="painel-cliente">
      <div className="cabecalho-projetos">
        <div><span className="sobretitulo">ACOMPANHE CADA HISTÓRIA</span><h2>Minhas tatuagens.</h2></div>
        <p>Do primeiro traço até o último retoque.</p>
      </div>
      <div className="grade-cliente">
        <div className="lista-projetos">
          <h3>Seus projetos</h3>
          {carregando && <p className="estado">Carregando suas tatuagens…</p>}
          {erro && <p className="aviso aviso-erro" role="alert">{erro}</p>}
          {!carregando && !erro && tatuagens.length === 0 && <p className="estado estado-vazio">Ainda não há tatuagens no seu histórico. Seu primeiro pedido começa em “Pedir tatuagem”.</p>}
          {!carregando && !erro && tatuagens.length > 0 && <div className="grade-tatuagens">
            {tatuagens.map((tatuagem) => (
              <button key={tatuagem.id} data-initials={tatuagem.ideia.slice(0, 2).toUpperCase()} className={`cartao-tatuagem ${selecionada?.id === tatuagem.id ? "cartao-selecionado" : ""}`} onClick={() => abrirHistorico(tatuagem)}>
                <span className="numero-cartao">PROJETO · {String(tatuagem.id).padStart(3, "0")}</span>
                <strong>{tatuagem.ideia}</strong>
                <span>{tatuagem.local_corpo} · {tatuagem.tamanho}</span>
                <span className="selo-etapa"><i />{nomeDaEtapa(tatuagem.etapa)}</span>
              </button>
            ))}
          </div>}
        </div>
        <section className="historico painel-linha-tempo">
          <div className="historico-cabecalho">
            <div><h3>{selecionada?.ideia || "Seu caminho até aqui"}</h3>{selecionada && <p>{selecionada.local_corpo} · {selecionada.tamanho}</p>}</div>
            {selecionada && <span className="selo-etapa etapa-historico"><i />{nomeDaEtapa(selecionada.etapa)}</span>}
          </div>
          {!selecionada && <p className="estado">Selecione uma tatuagem para acompanhar as etapas registradas pelo estúdio.</p>}
          {selecionada && <>
            <div className="divisor-historico"><span className="sobretitulo">LINHA DO TEMPO</span></div>
            {carregandoPassos && <p className="estado">Carregando o histórico…</p>}
            {erroPassos && <p className="aviso aviso-erro" role="alert">{erroPassos}</p>}
            {!carregandoPassos && !erroPassos && passos.length === 0 && <p className="estado">Nenhum passo registrado ainda. O estúdio atualizará esta linha do tempo.</p>}
            {!carregandoPassos && !erroPassos && passos.map((passo) => <div className="item-historico" key={passo.id}><span className="ponto-historico" /><div><strong>{TIPOS_DE_PASSO.find((tipo) => tipo.valor === passo.tipo)?.nome || passo.tipo}</strong><p>{passo.data} · {passo.observacao}</p></div></div>)}
          </>}
        </section>
      </div>
    </section>
  );
}

// Carrega a agenda da equipe com filtro opcional pela etapa.
function TelaAgenda({ aoAbrirFicha, atualizacao }) {
  const [tatuagens, definirTatuagens] = useState([]);
  const [etapa, definirEtapa] = useState("");
  const [carregando, definirCarregando] = useState(true);
  const [erro, definirErro] = useState("");
  const filtros = [
    { valor: "", nome: "Todas" },
    { valor: "pedida", nome: "Pedida" },
    { valor: "desenho aprovado", nome: "Desenho aprovado" },
    { valor: "em sessões", nome: "Em sessões" },
    { valor: "finalizada", nome: "Finalizada" },
  ];

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
    <section id="projetos" className="painel-agenda">
      <div className="cabecalho-agenda">
        <div><span className="sobretitulo">VISÃO DO ESTÚDIO</span><h2>Projetos.</h2><p>Acompanhe cada história, do traço ao retoque.</p></div>
        <div className="filtros-etapa" role="group" aria-label="Filtrar tatuagens por etapa">
          {filtros.map((filtro) => <button key={filtro.valor} className={etapa === filtro.valor ? "filtro-ativo" : ""} onClick={() => definirEtapa(filtro.valor)}>{filtro.nome}</button>)}
        </div>
      </div>
      {carregando && <p className="estado">Carregando agenda…</p>}
      {erro && <p className="aviso aviso-erro" role="alert">{erro}</p>}
      {!carregando && !erro && tatuagens.length === 0 && <p className="estado estado-vazio">Não há tatuagens nesta etapa.</p>}
      {!carregando && !erro && <div className="grade-tatuagens grade-agenda">
        {tatuagens.map((tatuagem) => (
          <article key={tatuagem.id} className="cartao-tatuagem cartao-agenda">
            <div className="cartao-agenda-topo"><span className="cartao-inicial">{tatuagem.ideia.slice(0, 2).toUpperCase()}</span><span className="numero-cartao">PROJETO · {String(tatuagem.id).padStart(3, "0")}</span></div>
            <strong>{tatuagem.ideia}</strong>
            <span>{tatuagem.local_corpo} · {tatuagem.tamanho}</span>
            <span className="selo-etapa"><i />{nomeDaEtapa(tatuagem.etapa)}</span>
            <button className="botao botao-claro" onClick={() => aoAbrirFicha(tatuagem)}>Abrir ficha <span aria-hidden="true">↗</span></button>
          </article>
        ))}
      </div>}
    </section>
  );
}

// Resume os projetos do estúdio e encaminha os atalhos para as telas correspondentes.
function TelaVisaoGeral({ atualizacao, aoVerAgenda, aoAbrirFicha, aoRegistrarPasso }) {
  const [tatuagens, definirTatuagens] = useState([]);
  const [erro, definirErro] = useState("");

  useEffect(() => {
    pedirApi("/tatuagens")
      .then(definirTatuagens)
      .catch((erroApi) => definirErro(erroApi.message));
  }, [atualizacao]);

  const pendentes = tatuagens.filter((tatuagem) => tatuagem.etapa !== "finalizada");
  const emSessoes = tatuagens.filter((tatuagem) => tatuagem.etapa === "em sessões");

  return (
    <>
      <section className="banner-estudio">
        <img className="banner-ornamento" src="/imagens/arabesco-floral.png" alt="" />
        <div className="banner-conteudo">
          <span className="sobretitulo">ATELIÊ TINTA NEGRA</span>
          <h1>Arte viva,<br /><em>agenda em ordem.</em></h1>
          <p>Bom dia, Vitor. Acompanhe os projetos e escolha o próximo passo do estúdio.</p>
          <div className="acoes-banner">
            <button className="botao botao-contorno" onClick={aoVerAgenda}>Ver agenda <span aria-hidden="true">→</span></button>
            <button className="botao botao-ember" onClick={() => aoRegistrarPasso(pendentes)}>＋ Registrar passo</button>
          </div>
        </div>
        <span className="banner-selo" aria-hidden="true">TN<br />✳</span>
      </section>
      {erro && <p className="aviso aviso-erro" role="alert">{erro}</p>}
      <section className="resumo-estudio" aria-label="Resumo do estúdio">
        <article><strong>{String(pendentes.length).padStart(2, "0")}</strong><h2>Ações pendentes</h2><p>Projetos que precisam de atenção</p></article>
        <article><strong>{String(emSessoes.length).padStart(2, "0")}</strong><h2>Sessões em andamento</h2><p>Projetos em fase de sessão</p></article>
        <article><strong>{String(tatuagens.length).padStart(2, "0")}</strong><h2>Projetos ativos</h2><p>Pedidos registrados no estúdio</p></article>
      </section>
      <TelaAgenda atualizacao={atualizacao} aoAbrirFicha={aoAbrirFicha} />
    </>
  );
}

// Registra a aprovação do desenho, uma sessão ou um retoque na ficha escolhida.
function TelaFicha({ tatuagem, aoVoltar, aoSalvar }) {
  const [tipo, definirTipo] = useState(tatuagem.etapa === "pedida" ? "desenho_aprovado" : "sessao");
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
  const [perfilNome, definirPerfilNome] = useState("Vitor");
  const [tela, definirTela] = useState("visao-geral");
  const [telaAnteriorFicha, definirTelaAnteriorFicha] = useState("agenda");
  const [ficha, definirFicha] = useState(null);
  const [atualizacao, definirAtualizacao] = useState(0);
  const perfil = PERFIS.find((opcao) => opcao.nome === perfilNome);

  // Muda a tela inicial para combinar com a pessoa escolhida na lista.
  function escolherPerfil(evento) {
    const nome = evento.target.value;
    definirPerfilNome(nome);
    definirFicha(null);
    definirTela(nome === "Vitor" ? "visao-geral" : "minhas");
  }

  function abrirAgenda() {
    definirFicha(null);
    definirTela("agenda");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function abrirVisaoGeral() {
    definirFicha(null);
    definirTela("visao-geral");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function abrirProjetos() {
    definirFicha(null);
    definirTela("agenda");
    window.setTimeout(() => document.getElementById("projetos")?.scrollIntoView({ behavior: "smooth" }), 0);
  }

  function registrarProximoPasso(pendentes) {
    if (pendentes.length > 0) {
      definirTelaAnteriorFicha("visao-geral");
      definirFicha(pendentes[0]);
      definirTela("ficha");
      return;
    }
    abrirAgenda();
  }

  function abrirFicha(tatuagem) {
    definirTelaAnteriorFicha(tela);
    definirFicha(tatuagem);
    definirTela("ficha");
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
        <a className="marca" href="#inicio" onClick={() => definirTela(perfil.tipo === "cliente" ? "minhas" : "agenda")} aria-label="Tinta Negra Tattoo Studio">
          <span className="marca-simbolo" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round"><path d="M14.5 4.5 19 9 9 19H4.5v-4.5l10-10Z" /><path d="m12 7 5 5M4.5 19 3 21l2-1" /></svg></span>
          <span className="marca-texto"><strong>Tinta Negra</strong><small>Tattoo Studio</small></span>
        </a>
        <nav className="navegacao" aria-label="Navegação principal">
          {perfil.tipo === "tatuador" && <>
            <button className={tela === "visao-geral" ? "ativo" : "nav-inicio"} onClick={abrirVisaoGeral}><span className="icone-grade" aria-hidden="true">▦</span> Visão geral</button>
            <button className={tela === "agenda" || tela === "ficha" ? "ativo" : "nav-agenda"} onClick={abrirAgenda}><span className="icone-grade" aria-hidden="true">▤</span> Agenda</button>
            <button className="nav-projetos" onClick={abrirProjetos}><span className="icone-grade" aria-hidden="true">☷</span> Projetos</button>
            <div className="selo-estudio"><span>DESDE 2018</span></div>
          </>}
        </nav>
        <label className="seletor-perfil">
          <span className="avatar-perfil" aria-hidden="true">{perfil.tipo === "cliente" ? "BM" : "VS"}</span>
          <span className="dados-perfil"><span>{perfil.tipo === "cliente" ? `Olá, ${perfil.nome}` : perfil.nome === "Vitor" ? "Vitor Sales" : perfil.nome}</span><select aria-label="Escolher perfil" value={perfilNome} onChange={escolherPerfil}>{PERFIS.map((opcao) => <option key={opcao.nome} value={opcao.nome}>{opcao.nome} · {opcao.tipo}</option>)}</select></span>
        </label>
      </header>
      <main id="inicio" className="conteudo-principal">
        {tela === "minhas" && <section className="banner-cliente">
          <img className="banner-ornamento" src="/imagens/arabesco.png" alt="" />
          <div className="banner-conteudo"><span className="sobretitulo">SUA JORNADA NA PELE</span><h1>Histórias que ficam.</h1><p>Acompanhe cada traço, cada sessão e tudo o que vem depois.</p><button className="botao botao-ember" onClick={() => definirTela("pedir")}><span aria-hidden="true">＋</span> Pedir tatuagem</button></div>
        </section>}
        {tela === "visao-geral" && <TelaVisaoGeral atualizacao={atualizacao} aoVerAgenda={abrirAgenda} aoAbrirFicha={abrirFicha} aoRegistrarPasso={registrarProximoPasso} />}
        <div className="coluna-conteudo">
          {tela === "pedir" && <TelaPedir perfil={perfil} aoVoltar={() => definirTela("minhas")} aoCriar={() => definirAtualizacao((valor) => valor + 1)} />}
          {tela === "minhas" && <TelaMinhasTatuagens key={atualizacao} perfil={perfil} />}
          {tela === "agenda" && <TelaAgenda atualizacao={atualizacao} aoAbrirFicha={abrirFicha} />}
          {tela === "ficha" && ficha && <TelaFicha tatuagem={ficha} aoVoltar={() => definirTela(telaAnteriorFicha)} aoSalvar={salvarPasso} />}
        </div>
      </main>
      {perfil.tipo === "cliente" && <nav className="navegacao-mobile" aria-label="Navegação da cliente">
        <button className={tela === "minhas" ? "ativo" : ""} onClick={() => definirTela("minhas")}>☷ <span>Minhas tatuagens</span></button>
        <button className={tela === "pedir" ? "ativo" : ""} onClick={() => definirTela("pedir")}>＋ <span>Novo pedido</span></button>
      </nav>}
      <footer className="rodape"><span>UM PASSO DE CADA VEZ.</span><span>TINTA NEGRA · TATTOO STUDIO</span></footer>
    </div>
  );
}
