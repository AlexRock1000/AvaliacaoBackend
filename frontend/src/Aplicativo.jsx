import React, { useEffect, useState } from "react";

import { pedirApi } from "./api.js";

const PERFIS = [
  { nome: "Bruna", tipo: "cliente", clienteId: 1 },
  { nome: "Vitor", tipo: "tatuador", clienteId: null },
];

const TIPOS_DE_PASSO = [
  { valor: "desenho_enviado", nome: "Desenho enviado para aprovação" },
  { valor: "desenho_aprovado", nome: "Desenho aprovado" },
  { valor: "desenho_reprovado", nome: "Ajustes solicitados no desenho" },
  { valor: "sessao", nome: "Sessão" },
  { valor: "retoque_combinado", nome: "Retoque combinado" },
  { valor: "retoque", nome: "Retoque realizado" },
];

const ETAPAS_PREPARACAO = ["aguardando aprovação", "ajustes no desenho"];
const DURACAO_MAXIMA_HORAS = 10;
const TAMANHO_MAXIMO_IMAGEM_BYTES = 5 * 1024 * 1024;

// Mostra a etapa com uma escrita legível para as duas pessoas do estúdio.
function nomeDaEtapa(etapa) {
  const nomes = {
    pedida: "Pedido recebido",
    "aguardando aprovação": "Aguardando aprovação da cliente",
    "ajustes no desenho": "Ajustes no desenho",
    "desenho aprovado": "Desenho aprovado",
    "em sessões": "Sessões",
    "aguardando retoque": "Aguardando retoque",
    finalizada: "Finalizada",
  };
  return nomes[etapa] || etapa;
}

// Explica à cliente o que deve acontecer depois da etapa atual, conforme o fluxo da cartilha.
function proximoPassoDaCliente(etapa) {
  const orientacoes = {
    pedida: "Agora, o estúdio vai preparar e aprovar o desenho. Você acompanha a atualização por aqui.",
    "aguardando aprovação": "O tatuador enviou o desenho. Confira a imagem abaixo e diga se concorda ou se precisa de ajustes.",
    "ajustes no desenho": "O estúdio vai revisar o desenho com base na sua observação e enviar uma nova versão.",
    "desenho aprovado": "O próximo passo é combinar a primeira sessão com o estúdio.",
    "em sessões": "Confira abaixo a data da sua sessão. Depois que ela acontecer, o tatuador confirma por aqui e agenda o retoque.",
    "aguardando retoque": "O retoque já foi combinado. Depois da cicatrização, realize o retoque com o estúdio para concluir o projeto.",
    finalizada: "Seu projeto foi concluído. Não há próximos passos previstos.",
  };
  return orientacoes[etapa] || "Consulte o estúdio para saber qual será o próximo passo.";
}

function formatarDataAgendamento(data) {
  return data?.split("-").reverse().join("/") || "";
}

function extrairTamanhoNumerico(tamanho) {
  return String(tamanho || "").replace(/\s*cm$/i, "").trim().replace(",", ".");
}

function tamanhoValido(tamanho) {
  const numero = extrairTamanhoNumerico(tamanho);
  return /^[0-9]+(?:\.[0-9]+)?$/.test(numero) && Number(numero) > 0;
}

function hojeComoDataISO() {
  const hoje = new Date();
  return `${hoje.getFullYear()}-${String(hoje.getMonth() + 1).padStart(2, "0")}-${String(hoje.getDate()).padStart(2, "0")}`;
}

// Sugere a primeira data que ainda pode ter horário, sem iniciar a ficha numa segunda-feira ou após o último horário.
function dataInicialDaSessao() {
  const agora = new Date();
  const data = new Date(agora.getFullYear(), agora.getMonth(), agora.getDate());
  if (agora.getHours() >= 18) data.setDate(data.getDate() + 1);
  while (data.getDay() === 1) data.setDate(data.getDate() + 1);
  return `${data.getFullYear()}-${String(data.getMonth() + 1).padStart(2, "0")}-${String(data.getDate()).padStart(2, "0")}`;
}

// Explica por que a data escolhida não oferece horário para evitar que a lista vazia pareça um erro.
function mensagemSemHorarios(data) {
  if (data < hojeComoDataISO()) return "Escolha hoje ou uma data futura para consultar os horários.";
  if (new Date(`${data}T00:00:00`).getDay() === 1) return "O estúdio não agenda às segundas-feiras.";
  if (data === hojeComoDataISO()) return "Não há mais horários para hoje. Escolha outra data.";
  return "Não há horários que comportem essa duração nessa data.";
}

function grupoDeProximidade(data) {
  const [ano, mes, dia] = data.split("-").map(Number);
  const hoje = new Date();
  const dataHoje = Date.UTC(hoje.getFullYear(), hoje.getMonth(), hoje.getDate());
  const dataAgendada = Date.UTC(ano, mes - 1, dia);
  const dias = Math.round((dataAgendada - dataHoje) / 86400000);
  if (dias < 0) return "Atrasadas";
  if (dias === 0) return "Hoje";
  if (dias <= 7) return "Próximos 7 dias";
  return "Mais tarde";
}

function agruparPorProximidade(agendamentos) {
  const ordem = ["Atrasadas", "Hoje", "Próximos 7 dias", "Mais tarde"];
  const grupos = new Map(ordem.map((nome) => [nome, []]));
  agendamentos.forEach((agendamento) => grupos.get(grupoDeProximidade(agendamento.data)).push(agendamento));
  return ordem.filter((nome) => grupos.get(nome).length > 0).map((nome) => ({ nome, agendamentos: grupos.get(nome) }));
}

// Exibe a tela de pedido para a cliente e mostra recusas da API no próprio formulário.
function TelaPedir({ perfil, aoCriar, aoAtualizar, tatuagem = null, aoVoltar }) {
  const editando = Boolean(tatuagem);
  const [ideia, definirIdeia] = useState(tatuagem?.ideia || "");
  const [localCorpo, definirLocalCorpo] = useState(tatuagem?.local_corpo || "");
  const [tamanho, definirTamanho] = useState(extrairTamanhoNumerico(tatuagem?.tamanho));
  const [imagemReferencia, definirImagemReferencia] = useState("");
  const [nomeImagemReferencia, definirNomeImagemReferencia] = useState("");
  const [arrastandoReferencia, definirArrastandoReferencia] = useState(false);
  const [lendoReferencia, definirLendoReferencia] = useState(false);
  const [enviando, definirEnviando] = useState(false);
  const [erro, definirErro] = useState("");
  const [erroTamanho, definirErroTamanho] = useState("");
  const [mensagem, definirMensagem] = useState("");

  // Lê a imagem de referência escolhida para enviá-la junto com o pedido.
  function carregarImagemReferencia(arquivo) {
    if (!arquivo) return;
    if (!arquivo.type.startsWith("image/")) {
      definirErro("Escolha um arquivo de imagem para usar como referência.");
      return;
    }
    if (arquivo.size > TAMANHO_MAXIMO_IMAGEM_BYTES) {
      definirErro("A imagem deve ter no máximo 5 MB.");
      return;
    }
    definirErro("");
    definirLendoReferencia(true);
    const leitor = new FileReader();
    leitor.onload = () => {
      definirImagemReferencia(leitor.result);
      definirNomeImagemReferencia(arquivo.name);
      definirLendoReferencia(false);
    };
    leitor.onerror = () => {
      definirErro("Não foi possível ler essa imagem. Escolha o arquivo novamente.");
      definirLendoReferencia(false);
    };
    leitor.readAsDataURL(arquivo);
  }

  // Recebe a imagem de referência pelo seletor de arquivos.
  function selecionarImagemReferencia(evento) {
    carregarImagemReferencia(evento.target.files?.[0]);
  }

  // Recebe a imagem de referência quando ela é solta na área de upload.
  function soltarImagemReferencia(evento) {
    evento.preventDefault();
    definirArrastandoReferencia(false);
    carregarImagemReferencia(evento.dataTransfer.files?.[0]);
  }

  // Envia o pedido como JSON e conserva a mensagem de recusa para a pessoa vê-la.
  function enviarPedido(evento) {
    evento.preventDefault();
    definirErro("");
    definirErroTamanho("");
    definirMensagem("");
    if (!tamanhoValido(tamanho)) {
      definirErroTamanho("Informe um número maior que zero, em centímetros. Ex.: 20.");
      document.getElementById("tamanho")?.focus();
      return;
    }
    definirEnviando(true);

    pedirApi(editando ? `/tatuagens/${tatuagem.id}` : "/tatuagens", {
        method: editando ? "PUT" : "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ideia,
          local_corpo: localCorpo,
          tamanho,
          cliente_id: perfil.clienteId,
          ...(editando
            ? (imagemReferencia ? { imagem_referencia: imagemReferencia } : {})
            : { imagem_referencia: imagemReferencia || null }),
        }),
      })
      .then((tatuagem) => {
        if (editando) {
          aoAtualizar(tatuagem);
          return;
        }
        definirIdeia("");
        definirLocalCorpo("");
        definirTamanho("");
        definirImagemReferencia("");
        definirNomeImagemReferencia("");
        definirMensagem("Seu pedido foi recebido pelo estúdio.");
        aoCriar(tatuagem);
      })
      .catch((erroApi) => {
        if (erroApi.campo === "tamanho") definirErroTamanho(erroApi.message);
        else definirErro(erroApi.message);
      })
      .finally(() => {
        definirEnviando(false);
      });
  }

  return (
    <section className="painel-formulario">
      <button className="voltar" type="button" onClick={aoVoltar}>{editando ? "← Voltar ao pedido" : "← Voltar para minhas tatuagens"}</button>
      <div className="titulo-secao">
        <span className="sobretitulo">{editando ? "PEDIDO RECEBIDO" : "UM NOVO PROJETO"}</span>
        <h2>{editando ? "Editar pedido." : "Conte sua ideia."}</h2>
        <p>{editando ? "Atualize os detalhes enquanto o estúdio ainda não iniciou a preparação do desenho." : "Não precisa saber explicar tudo. Dê os primeiros detalhes e a equipe constrói o desenho com você."}</p>
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
            <label htmlFor="tamanho">Tamanho aproximado (cm)</label>
            <input id="tamanho" type="number" inputMode="decimal" min="0.01" step="any" value={tamanho} onChange={(evento) => { definirTamanho(evento.target.value); definirErroTamanho(""); }} onInvalid={(evento) => { if (evento.currentTarget.validity.badInput || evento.currentTarget.validity.valueMissing) definirErroTamanho("Informe o tamanho usando apenas números, em centímetros."); }} aria-describedby={erroTamanho ? "tamanho-ajuda tamanho-erro" : "tamanho-ajuda"} required placeholder="Ex.: 20" />
            <small id="tamanho-ajuda" className="ajuda-campo">Use apenas números. Medida em centímetros.</small>
            {erroTamanho && <small id="tamanho-erro" className="erro-campo" role="alert">{erroTamanho}</small>}
          </div>
        </div>
        <label htmlFor="imagem-referencia">{editando ? "Nova imagem de referência (opcional)" : "Imagem de referência (opcional)"}</label>
        <div className={`area-upload ${arrastandoReferencia ? "area-upload-ativa" : ""}`} onDragOver={(evento) => { evento.preventDefault(); definirArrastandoReferencia(true); }} onDragLeave={() => definirArrastandoReferencia(false)} onDrop={soltarImagemReferencia}>
          <input id="imagem-referencia" className="entrada-imagem-oculta" type="file" accept="image/*" onChange={selecionarImagemReferencia} />
          <label className="conteudo-upload" htmlFor="imagem-referencia">
            {imagemReferencia ? <img className="previa-desenho" src={imagemReferencia} alt="Prévia da imagem de referência" /> : <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M12 16V4m0 0L8 8m4-4 4 4" /><path d="M5 14v4a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-4" /></svg>}
            <strong>{imagemReferencia ? nomeImagemReferencia : editando ? "Arraste uma nova imagem de referência." : "Arraste e solte uma imagem de referência."}</strong>
            <span>{imagemReferencia ? "Imagem carregada · clique ou solte outra para substituir" : editando ? "A imagem atual será mantida se você não enviar outra." : <>Ou <u>escolha uma imagem</u>. Formatos aceitos: PNG, JPG e outros formatos de imagem, até 5 MB.</>}</span>
          </label>
        </div>
        {erro && <p className="aviso aviso-erro" role="alert">{erro}</p>}
        {mensagem && <p className="aviso aviso-sucesso" role="status">{mensagem}</p>}
        <button className="botao botao-escuro" disabled={enviando || lendoReferencia}>
          {lendoReferencia ? "Lendo imagem…" : enviando ? (editando ? "Salvando alterações…" : "Enviando pedido…") : editando ? "Salvar alterações" : "Enviar pedido"}<span aria-hidden="true">↗</span>
        </button>
      </form>
    </section>
  );
}

// Carrega os projetos da cliente; o cartão encaminha para a tela separada de histórico.
function TelaMinhasTatuagens({ perfil, aoAbrirHistorico }) {
  const [tatuagens, definirTatuagens] = useState([]);
  const [agendamentosPorTatuagem, definirAgendamentosPorTatuagem] = useState({});
  const [carregando, definirCarregando] = useState(true);
  const [erro, definirErro] = useState("");

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

  // Carrega os próximos horários para que a cliente os veja sem abrir cada histórico.
  useEffect(() => {
    let consultaAtiva = true;
    if (tatuagens.length === 0) {
      definirAgendamentosPorTatuagem({});
      return () => { consultaAtiva = false; };
    }
    Promise.all(tatuagens.map((tatuagem) => pedirApi(`/tatuagens/${tatuagem.id}/passos`)
      .then((historico) => {
        const tipo = tatuagem.etapa === "em sessões" ? "sessao" : tatuagem.etapa === "aguardando retoque" ? "retoque_combinado" : null;
        const proximos = historico
          .filter((passo) => passo.tipo === tipo && (passo.situacao || "agendada") === "agendada")
          .sort((primeiro, segundo) => `${primeiro.data} ${primeiro.horario || ""}`.localeCompare(`${segundo.data} ${segundo.horario || ""}`));
        return [tatuagem.id, proximos[0] || null];
      })
      .catch(() => [tatuagem.id, null])))
      .then((entradas) => { if (consultaAtiva) definirAgendamentosPorTatuagem(Object.fromEntries(entradas)); });
    return () => { consultaAtiva = false; };
  }, [tatuagens]);

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
              <button key={tatuagem.id} className="cartao-tatuagem cartao-agenda cartao-agenda-cliente" aria-label={`Abrir histórico de atualizações: ${tatuagem.ideia}`} onClick={() => aoAbrirHistorico(tatuagem)}>
                <div className="cartao-agenda-topo"><span className="cartao-inicial">{tatuagem.ideia.slice(0, 2).toUpperCase()}</span><span className="numero-cartao">PROJETO · {String(tatuagem.id).padStart(3, "0")}</span></div>
                <strong>{tatuagem.ideia}</strong>
                <span>{tatuagem.local_corpo} · {tatuagem.tamanho}</span>
                {agendamentosPorTatuagem[tatuagem.id] && <span className="agendamento-resumo-cliente">{tatuagem.etapa === "aguardando retoque" ? "Retoque" : "Sessão"}: {formatarDataAgendamento(agendamentosPorTatuagem[tatuagem.id].data)}{agendamentosPorTatuagem[tatuagem.id].horario ? ` · ${agendamentosPorTatuagem[tatuagem.id].horario.slice(0, 5)}` : ""}{agendamentosPorTatuagem[tatuagem.id].duracao_horas ? ` · ${agendamentosPorTatuagem[tatuagem.id].duracao_horas}h` : ""}</span>}
                <span className="selo-etapa"><i />{nomeDaEtapa(tatuagem.etapa)}</span>
                <span className="atalho-atualizacoes">Abrir histórico <span aria-hidden="true">↗</span></span>
              </button>
            ))}
          </div>}
        </div>
      </div>
    </section>
  );
}

// Apresenta em uma tela independente o histórico e as ações disponíveis para o projeto da cliente.
function TelaHistoricoCliente({ perfil, tatuagem, aoVoltar }) {
  const [selecionada, definirSelecionada] = useState(tatuagem);
  const [passos, definirPassos] = useState([]);
  const [carregandoPassos, definirCarregandoPassos] = useState(true);
  const [erroPassos, definirErroPassos] = useState("");
  const [observacaoResposta, definirObservacaoResposta] = useState("");
  const [erroResposta, definirErroResposta] = useState("");
  const [salvandoResposta, definirSalvandoResposta] = useState(false);
  const [editandoPedido, definirEditandoPedido] = useState(false);
  const [mensagemEdicao, definirMensagemEdicao] = useState("");

  // Busca os passos ao entrar nesta tela e ignora a resposta se a tela for fechada.
  useEffect(() => {
    let consultaAtiva = true;
    definirCarregandoPassos(true);
    definirErroPassos("");
    pedirApi(`/tatuagens/${tatuagem.id}/passos`)
      .then((dados) => { if (consultaAtiva) definirPassos(dados); })
      .catch((erroApi) => { if (consultaAtiva) definirErroPassos(erroApi.message); })
      .finally(() => { if (consultaAtiva) definirCarregandoPassos(false); });
    return () => { consultaAtiva = false; };
  }, [tatuagem.id]);

  function salvarEdicaoPedido(tatuagemAtualizada) {
    definirSelecionada(tatuagemAtualizada);
    definirEditandoPedido(false);
    definirMensagemEdicao("Pedido atualizado com sucesso.");
  }

  // Envia a decisão da cliente e atualiza a etapa e a linha do tempo após confirmação da API.
  function responderDesenho(tipo) {
    if (tipo === "desenho_reprovado" && !observacaoResposta.trim()) {
      definirErroResposta("Escreva o que você gostaria que o tatuador ajustasse.");
      return;
    }
    definirErroResposta("");
    definirSalvandoResposta(true);
    const observacao = observacaoResposta.trim() || "Desenho aprovado pela cliente.";
    pedirApi(`/tatuagens/${selecionada.id}/passos`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tipo, data: new Date().toISOString().slice(0, 10), observacao }),
    })
      .then((passo) => {
        const etapa = tipo === "desenho_aprovado" ? "desenho aprovado" : "ajustes no desenho";
        definirSelecionada((atual) => ({ ...atual, etapa }));
        definirPassos((atuais) => [...atuais, passo]);
        definirObservacaoResposta("");
      })
      .catch((erroApi) => definirErroResposta(erroApi.message))
      .finally(() => definirSalvandoResposta(false));
  }

  if (editandoPedido) {
    return <TelaPedir
      key={`editar-pedido-${selecionada.id}`}
      perfil={perfil}
      tatuagem={selecionada}
      aoAtualizar={salvarEdicaoPedido}
      aoVoltar={() => definirEditandoPedido(false)}
    />;
  }

  const desenhoEnviado = [...passos].reverse().find((passo) => passo.tipo === "desenho_enviado");
  const sessoesAgendadas = passos
    .filter((passo) => passo.tipo === "sessao" && (passo.situacao || "agendada") === "agendada")
    .sort((primeiro, segundo) => `${primeiro.data} ${primeiro.horario || ""}`.localeCompare(`${segundo.data} ${segundo.horario || ""}`));
  const sessaoAgendada = sessoesAgendadas[0];
  const retoqueAgendado = [...passos].reverse().find((passo) => passo.tipo === "retoque_combinado" && (passo.situacao || "agendada") === "agendada");

  return (
    <section className="painel-cliente tela-historico-cliente">
      <button className="voltar" type="button" onClick={aoVoltar}>← Voltar para minhas tatuagens</button>
      {mensagemEdicao && <p className="aviso aviso-sucesso" role="status">{mensagemEdicao}</p>}
      <div className="cabecalho-projetos">
        <div><span className="sobretitulo">ATUALIZAÇÕES DO PROJETO · {String(selecionada.id).padStart(3, "0")}</span><h2>{selecionada.ideia}</h2></div>
        <p>{selecionada.local_corpo} · {selecionada.tamanho}</p>
      </div>
      <section className="historico painel-linha-tempo">
        <div className="historico-cabecalho">
          <div><h3>Histórico da conversa</h3><p>Etapas, mensagens e registros deste projeto.</p></div>
          <span className="selo-etapa etapa-historico"><i />{nomeDaEtapa(selecionada.etapa)}</span>
        </div>
        <p className="orientacao-proximo-passo" role="status">
          <strong>O que vem agora</strong>
          {proximoPassoDaCliente(selecionada.etapa)}
          {selecionada.etapa === "em sessões" && sessaoAgendada && <span className="horario-proximo-passo">Sua sessão está marcada para <strong>{formatarDataAgendamento(sessaoAgendada.data)} às {sessaoAgendada.horario?.slice(0, 5)} ({sessaoAgendada.duracao_horas} {sessaoAgendada.duracao_horas === 1 ? "hora" : "horas"})</strong>.</span>}
          {selecionada.etapa === "aguardando retoque" && retoqueAgendado && <span className="horario-proximo-passo">O retoque está marcado para <strong>{formatarDataAgendamento(retoqueAgendado.data)} às {retoqueAgendado.horario?.slice(0, 5)} ({retoqueAgendado.duracao_horas} {retoqueAgendado.duracao_horas === 1 ? "hora" : "horas"})</strong>.</span>}
        </p>
        {selecionada.etapa === "pedida" && <button className="botao botao-ember botao-editar-pedido" type="button" onClick={() => { definirMensagemEdicao(""); definirEditandoPedido(true); }}>Editar pedido</button>}
        <div className="divisor-historico"><span className="sobretitulo">LINHA DO TEMPO</span></div>
        {carregandoPassos && <p className="estado">Carregando o histórico…</p>}
        {erroPassos && <p className="aviso aviso-erro" role="alert">{erroPassos}</p>}
        {!carregandoPassos && !erroPassos && passos.length === 0 && <p className="estado">Nenhum passo registrado ainda. O estúdio atualizará esta linha do tempo.</p>}
        {!carregandoPassos && !erroPassos && passos.map((passo) => <div className="item-historico" key={passo.id}><span className="ponto-historico" /><div><strong>{TIPOS_DE_PASSO.find((tipo) => tipo.valor === passo.tipo)?.nome || passo.tipo}</strong><p>{passo.data}{passo.horario ? ` · ${passo.horario.slice(0, 5)}` : ""}{(passo.tipo === "sessao" || passo.tipo === "retoque_combinado") && passo.duracao_horas ? ` · ${passo.duracao_horas} ${passo.duracao_horas === 1 ? "hora" : "horas"}` : ""} · {passo.observacao}</p>{passo.imagem && !(selecionada.etapa === "aguardando aprovação" && passo.id === desenhoEnviado?.id) && <img className="imagem-desenho-historico" src={passo.imagem} alt="Desenho enviado pelo tatuador" />}</div></div>)}
        {!carregandoPassos && !erroPassos && selecionada.etapa === "aguardando aprovação" && desenhoEnviado?.imagem && <section className="resposta-desenho">
          <h4>O que achou do desenho?</h4>
          <img src={desenhoEnviado.imagem} alt="Desenho enviado pelo tatuador para aprovação" />
          <label htmlFor="observacao-resposta-desenho">Sua observação</label>
          <textarea id="observacao-resposta-desenho" value={observacaoResposta} onChange={(evento) => definirObservacaoResposta(evento.target.value)} placeholder="Se precisar de ajustes, conte ao tatuador o que gostaria de mudar." />
          {erroResposta && <p className="aviso aviso-erro" role="alert">{erroResposta}</p>}
          <div className="acoes-resposta-desenho">
            <button className="botao botao-escuro" type="button" disabled={salvandoResposta} onClick={() => responderDesenho("desenho_aprovado")}>Concordo com o desenho</button>
            <button className="botao botao-claro" type="button" disabled={salvandoResposta} onClick={() => responderDesenho("desenho_reprovado")}>Quero pedir ajustes</button>
          </div>
        </section>}
      </section>
    </section>
  );
}

// Reúne a mensagem obrigatória antes de desmarcar uma sessão.
function FormularioCancelamentoSessao({ id, mensagem, aoAlterarMensagem, erro, salvando, aoConfirmar, aoFechar }) {
  return (
    <div className="formulario-cancelamento-sessao">
      <label htmlFor={`mensagem-cancelamento-${id}`}>Mensagem para a cliente (obrigatória)</label>
      <textarea
        id={`mensagem-cancelamento-${id}`}
        value={mensagem}
        onChange={(evento) => aoAlterarMensagem(evento.target.value)}
        placeholder="Explique o motivo do cancelamento."
        rows="3"
        required
      />
      <small>Esta mensagem ficará visível no histórico do pedido da cliente.</small>
      {erro && <p className="aviso aviso-erro" role="alert">{erro}</p>}
      <div className="acoes-cancelamento-sessao">
        <button className="botao botao-ember" type="button" disabled={salvando || !mensagem.trim()} onClick={aoConfirmar}>
          {salvando ? "Desmarcando…" : "Desmarcar e registrar mensagem"}
        </button>
        <button className="botao botao-claro" type="button" disabled={salvando} onClick={aoFechar}>Voltar</button>
      </div>
    </div>
  );
}

// Carrega a agenda da equipe com filtro opcional pela etapa.
function TelaAgenda({ aoAbrirFicha, atualizacao, aoAtualizar, titulo = "Projetos." }) {
  const [tatuagens, definirTatuagens] = useState([]);
  const [etapa, definirEtapa] = useState("");
  const [carregando, definirCarregando] = useState(true);
  const [erro, definirErro] = useState("");
  const [sessoes, definirSessoes] = useState([]);
  const [carregandoSessoes, definirCarregandoSessoes] = useState(false);
  const [erroSessoes, definirErroSessoes] = useState("");
  const [sessaoEmAtualizacao, definirSessaoEmAtualizacao] = useState(null);
  const [sessaoParaCancelar, definirSessaoParaCancelar] = useState(null);
  const [mensagemCancelamento, definirMensagemCancelamento] = useState("");
  const [erroCancelamento, definirErroCancelamento] = useState("");
  const tipoAgendamento = etapa === "em sessões" ? "sessao" : "retoque_combinado";
  const filtros = [
    { valor: "", nome: "Todas" },
    { valor: "pedida", nome: "Pedidos" },
    { valor: "preparacao", nome: "Preparação" },
    { valor: "desenho aprovado", nome: "Desenhos aprovados" },
    { valor: "em sessões", nome: "Sessões" },
    { valor: "aguardando retoque", nome: "Retoques" },
    { valor: "finalizada", nome: "Finalizados" },
  ];
  // Busca a agenda sempre que o filtro ou um registro de passo muda.
  useEffect(() => {
    function carregarAgenda() {
      definirCarregando(true);
      definirErro("");
      const etapasFiltradas = etapa === "preparacao" ? ETAPAS_PREPARACAO : etapa ? [etapa] : [null];
      Promise.all(etapasFiltradas.map((etapaFiltrada) => pedirApi(`/tatuagens${etapaFiltrada ? `?etapa=${encodeURIComponent(etapaFiltrada)}` : ""}`)))
        .then((listas) => definirTatuagens(listas.flat().sort((primeiro, segundo) => segundo.id - primeiro.id)))
        .catch((erroApi) => definirErro(erroApi.message))
        .finally(() => definirCarregando(false));
    }
    carregarAgenda();
  }, [etapa, atualizacao]);

  useEffect(() => {
    if (etapa !== "em sessões" && etapa !== "aguardando retoque") return;
    let consultaAtiva = true;
    definirCarregandoSessoes(true);
    definirSessoes([]);
    definirErroSessoes("");
    pedirApi(`/tatuagens?etapa=${encodeURIComponent(etapa)}`)
      .then((projetos) => Promise.all(projetos.map((projeto) => pedirApi(`/tatuagens/${projeto.id}/passos`).then((passos) => passos
        .filter((passo) => passo.tipo === tipoAgendamento && (passo.situacao || "agendada") === "agendada")
        .map((passo) => ({ ...passo, tatuagem: projeto }))))))
      .then((listas) => { if (consultaAtiva) definirSessoes(listas.flat().sort((a, b) => `${a.data} ${a.horario}`.localeCompare(`${b.data} ${b.horario}`))); })
      .catch((erroApi) => { if (consultaAtiva) definirErroSessoes(erroApi.message); })
      .finally(() => { if (consultaAtiva) definirCarregandoSessoes(false); });
    return () => { consultaAtiva = false; };
  }, [etapa, atualizacao]);

  function atualizarSessao(passo, situacao, mensagem = "") {
    definirSessaoEmAtualizacao(passo.id);
    definirErroCancelamento("");
    pedirApi(`/tatuagens/${passo.tatuagem_id}/passos/${passo.id}/situacao`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ situacao, ...(situacao === "cancelada" ? { observacao: mensagem.trim() } : {}) }),
    }).then(() => {
      if (situacao === "cancelada") {
        definirSessaoParaCancelar(null);
        definirMensagemCancelamento("");
      }
      aoAtualizar();
      if (situacao === "realizada") definirEtapa("aguardando retoque");
    })
      .catch((erroApi) => {
        if (situacao === "cancelada") definirErroCancelamento(erroApi.message);
        else definirErroSessoes(erroApi.message);
      })
      .finally(() => definirSessaoEmAtualizacao(null));
  }

  return (
    <section id="projetos" className="painel-agenda">
      <div className="cabecalho-agenda">
        <div><span className="sobretitulo">VISÃO DO ESTÚDIO</span><h2>{titulo}</h2><p>Acompanhe cada história, do traço ao retoque.</p></div>
        <div className="filtros-etapa" role="group" aria-label="Filtrar tatuagens por etapa">
          {filtros.map((filtro) => <button key={filtro.valor} className={etapa === filtro.valor ? "filtro-ativo" : ""} onClick={() => definirEtapa(filtro.valor)}>{filtro.nome}</button>)}
        </div>
      </div>
      {carregando && <p className="estado">Carregando agenda…</p>}
      {erro && <p className="aviso aviso-erro" role="alert">{erro}</p>}
      {etapa === "em sessões" || etapa === "aguardando retoque" ? <>
        {carregandoSessoes && <p className="estado">Carregando agendamentos…</p>}
        {erroSessoes && <p className="aviso aviso-erro" role="alert">{erroSessoes}</p>}
        {!carregandoSessoes && !erroSessoes && sessoes.length === 0 && <p className="estado estado-vazio">{etapa === "em sessões" ? "Não há sessões agendadas." : "Não há retoques agendados."}</p>}
        {!carregandoSessoes && !erroSessoes && sessoes.length > 0 && agruparPorProximidade(sessoes).map((grupo) => <section className="grupo-agendamentos" key={grupo.nome}>
          <header className="cabecalho-grupo-agendamentos"><h3>{grupo.nome}</h3><span>{grupo.agendamentos.length}</span></header>
          <div className="grade-tatuagens grade-agenda">
          {grupo.agendamentos.map((sessao) => <article key={sessao.id} className="cartao-tatuagem cartao-agenda cartao-sessao">
            <div className="cartao-agenda-topo"><span className="cartao-inicial">{sessao.tatuagem.ideia.slice(0, 2).toUpperCase()}</span><span className="numero-cartao">{tipoAgendamento === "sessao" ? "SESSÃO" : "RETOQUE"} · {String(sessao.id).padStart(3, "0")}</span></div>
            <strong>{sessao.tatuagem.ideia}</strong>
            <span>{sessao.tatuagem.local_corpo} · {sessao.tatuagem.tamanho}</span>
            <p className="detalhe-sessao-agendada">{sessao.data.split("-").reverse().join("/")} · {sessao.horario?.slice(0, 5)} · {sessao.duracao_horas || 2} {(sessao.duracao_horas || 2) === 1 ? "hora" : "horas"}</p>
            <div className="acoes-sessao">
              {tipoAgendamento === "sessao" ? <>
                <button className="botao botao-ember" disabled={sessaoEmAtualizacao !== null} onClick={() => atualizarSessao(sessao, "realizada")}>{sessaoEmAtualizacao === sessao.id ? "Salvando…" : "Confirmar realizada"}</button>
                {sessaoParaCancelar === sessao.id
                  ? <FormularioCancelamentoSessao
                    id={`agenda-${sessao.id}`}
                    mensagem={mensagemCancelamento}
                    aoAlterarMensagem={definirMensagemCancelamento}
                    erro={erroCancelamento}
                    salvando={sessaoEmAtualizacao === sessao.id}
                    aoConfirmar={() => atualizarSessao(sessao, "cancelada", mensagemCancelamento)}
                    aoFechar={() => { definirSessaoParaCancelar(null); definirMensagemCancelamento(""); definirErroCancelamento(""); }}
                  />
                  : <button className="botao botao-claro" type="button" disabled={sessaoEmAtualizacao !== null} onClick={() => { definirSessaoParaCancelar(sessao.id); definirMensagemCancelamento(""); definirErroCancelamento(""); }}>Desmarcar sessão</button>}
              </> : <button className="botao botao-ember" onClick={() => aoAbrirFicha(sessao.tatuagem)}>Abrir ficha do retoque</button>}
            </div>
          </article>)}
          </div>
        </section>)}
      </> : <>
      {!carregando && !erro && tatuagens.length === 0 && <p className="estado estado-vazio">{etapa === "preparacao" ? "Não há projetos em preparação." : "Não há tatuagens nesta etapa."}</p>}
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
      </>}
    </section>
  );
}

// Mostra todos os projetos agrupados por etapa, separado da agenda filtrável.
function TelaProjetos({ atualizacao, aoAbrirFicha }) {
  const [tatuagens, definirTatuagens] = useState([]);
  const [carregando, definirCarregando] = useState(true);
  const [erro, definirErro] = useState("");
  const etapas = [
    { valor: "pedida", titulo: "Pedidos recebidos" },
    { valor: "aguardando aprovação", titulo: "Aguardando cliente" },
    { valor: "ajustes no desenho", titulo: "Ajustes no desenho" },
    { valor: "desenho aprovado", titulo: "Desenho aprovado" },
    { valor: "em sessões", titulo: "Sessões" },
    { valor: "aguardando retoque", titulo: "Aguardando retoque" },
    { valor: "finalizada", titulo: "Finalizados" },
  ];

  useEffect(() => {
    definirCarregando(true);
    definirErro("");
    pedirApi("/tatuagens")
      .then(definirTatuagens)
      .catch((erroApi) => definirErro(erroApi.message))
      .finally(() => definirCarregando(false));
  }, [atualizacao]);

  return (
    <section className="painel-projetos">
      <header className="cabecalho-projetos-estudio">
        <span className="sobretitulo">VISÃO DO ESTÚDIO</span>
        <h2>Todos os projetos.</h2>
        <p>Organizados por etapa, do pedido à finalização.</p>
      </header>
      {carregando && <p className="estado">Carregando projetos…</p>}
      {erro && <p className="aviso aviso-erro" role="alert">{erro}</p>}
      {!carregando && !erro && tatuagens.length === 0 && <p className="estado estado-vazio">Ainda não há projetos cadastrados. Os novos pedidos aparecerão aqui.</p>}
      {!carregando && !erro && tatuagens.length > 0 && <div className="quadro-projetos">
        {etapas.map((etapa) => {
          const itens = tatuagens.filter((tatuagem) => tatuagem.etapa === etapa.valor);
          return (
            <section className="coluna-projetos" key={etapa.valor}>
              <header><h3>{etapa.titulo}</h3><span>{String(itens.length).padStart(2, "0")}</span></header>
              {itens.length === 0 && <p className="estado-coluna">Nenhum projeto</p>}
              {itens.map((tatuagem) => (
                <article className="cartao-projeto" key={tatuagem.id}>
                  <span className="numero-cartao">PROJETO · {String(tatuagem.id).padStart(3, "0")}</span>
                  <h4>{tatuagem.ideia}</h4>
                  <p>{tatuagem.local_corpo} · {tatuagem.tamanho}</p>
                  <button className="botao botao-claro" onClick={() => aoAbrirFicha(tatuagem)}>Abrir ficha <span aria-hidden="true">↗</span></button>
                </article>
              ))}
            </section>
          );
        })}
      </div>}
    </section>
  );
}

// Resume os projetos do estúdio e encaminha os atalhos para as telas correspondentes.
function TelaVisaoGeral({ atualizacao, aoVerAgenda, aoAbrirFicha, aoRegistrarPasso, aoAtualizar }) {
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
        <article><strong>{String(emSessoes.length).padStart(2, "0")}</strong><h2>Sessões</h2><p>Projetos com sessões agendadas</p></article>
        <article><strong>{String(tatuagens.length).padStart(2, "0")}</strong><h2>Projetos ativos</h2><p>Pedidos registrados no estúdio</p></article>
      </section>
      <TelaAgenda atualizacao={atualizacao} aoAtualizar={aoAtualizar} aoAbrirFicha={aoAbrirFicha} />
    </>
  );
}

// Exibe o pedido concluído e consulta os passos para a equipe revisar o que foi feito.
function TelaPedidoFinalizado({ tatuagem, aoVoltar, nomeRetorno }) {
  const [passos, definirPassos] = useState([]);
  const [carregando, definirCarregando] = useState(true);
  const [erro, definirErro] = useState("");

  useEffect(() => {
    pedirApi(`/tatuagens/${tatuagem.id}/passos`)
      .then(definirPassos)
      .catch((erroApi) => definirErro(erroApi.message))
      .finally(() => definirCarregando(false));
  }, [tatuagem.id]);

  const desenhoEnviado = [...passos].reverse().find((passo) => passo.tipo === "desenho_enviado" && passo.imagem);

  return (
    <section className="ficha-finalizada">
      <button className="voltar" type="button" onClick={aoVoltar}>← Voltar para {nomeRetorno}</button>
      <header className="ficha-finalizada-cabecalho">
        <span className="sobretitulo">PROJETO CONCLUÍDO · {String(tatuagem.id).padStart(3, "0")}</span>
        <h2>{tatuagem.ideia}</h2>
        <p>{tatuagem.local_corpo} · {tatuagem.tamanho}</p>
        <span className="selo-etapa"><i />Pedido realizado</span>
      </header>
      <div className="ficha-finalizada-conteudo">
        <figure className="ficha-finalizada-imagem">
          <img src={desenhoEnviado?.imagem || "/imagens/mao-rosa.png"} alt={desenhoEnviado ? "Desenho enviado pelo tatuador" : "Desenho de referência de uma mão esquelética segurando uma rosa"} />
          <figcaption>{desenhoEnviado ? "Desenho do projeto" : "Referência de tatuagem"}</figcaption>
        </figure>
        <section className="ficha-finalizada-historico" aria-labelledby="titulo-historico-finalizado">
          <span className="sobretitulo">HISTÓRICO DO PROJETO</span>
          <h3 id="titulo-historico-finalizado">O que foi feito</h3>
          {carregando && <p className="estado">Carregando histórico…</p>}
          {erro && <p className="aviso aviso-erro" role="alert">{erro}</p>}
          {!carregando && !erro && passos.length === 0 && <p className="estado">Nenhum passo registrado.</p>}
          {!carregando && !erro && passos.map((passo) => (
            <article className="passo-finalizado" key={passo.id}>
              <strong>{TIPOS_DE_PASSO.find((tipo) => tipo.valor === passo.tipo)?.nome || passo.tipo}</strong>
              <span>{passo.data}</span>
              <p>{passo.horario ? `${passo.horario.slice(0, 5)} · ` : ""}{passo.observacao}</p>
            </article>
          ))}
        </section>
      </div>
    </section>
  );
}

// Registra a aprovação do desenho, uma sessão ou um retoque na ficha escolhida.
function TelaFicha({ tatuagem, aoVoltar, aoSalvar, nomeRetorno = "agenda" }) {
  const enviarDesenho = tatuagem.etapa === "pedida" || tatuagem.etapa === "ajustes no desenho";
  const etapaPermiteSessao = tatuagem.etapa === "desenho aprovado" || tatuagem.etapa === "em sessões";
  const tiposPermitidos = enviarDesenho
    ? TIPOS_DE_PASSO.filter((opcao) => opcao.valor === "desenho_enviado")
    : tatuagem.etapa === "desenho aprovado"
      ? TIPOS_DE_PASSO.filter((opcao) => opcao.valor === "sessao")
      : tatuagem.etapa === "em sessões"
        ? TIPOS_DE_PASSO.filter((opcao) => opcao.valor === "sessao")
        : tatuagem.etapa === "aguardando retoque"
          ? TIPOS_DE_PASSO.filter((opcao) => opcao.valor === "retoque")
          : [];
  const [tipo, definirTipo] = useState(tiposPermitidos[0]?.valor || "");
  const [imagem, definirImagem] = useState("");
  const [nomeImagem, definirNomeImagem] = useState("");
  const [arrastandoImagem, definirArrastandoImagem] = useState(false);
  const [data, definirData] = useState(dataInicialDaSessao);
  const [duracaoHoras, definirDuracaoHoras] = useState("2");
  const [horariosDisponiveis, definirHorariosDisponiveis] = useState([]);
  const [horario, definirHorario] = useState("");
  const [carregandoHorarios, definirCarregandoHorarios] = useState(false);
  const [erroHorarios, definirErroHorarios] = useState("");
  const [sessaoAgendada, definirSessaoAgendada] = useState(null);
  const [carregandoSessao, definirCarregandoSessao] = useState(etapaPermiteSessao);
  const [erroConsultaSessao, definirErroConsultaSessao] = useState("");
  const [abrirCancelamento, definirAbrirCancelamento] = useState(false);
  const [mensagemCancelamento, definirMensagemCancelamento] = useState("");
  const [erroCancelamento, definirErroCancelamento] = useState("");
  const [cancelandoSessao, definirCancelandoSessao] = useState(false);
  const [passoRetoque, definirPassoRetoque] = useState(null);
  const [carregandoPassoRetoque, definirCarregandoPassoRetoque] = useState(tatuagem.etapa === "aguardando retoque");
  const [observacao, definirObservacao] = useState("");
  const [erro, definirErro] = useState("");
  const [salvando, definirSalvando] = useState(false);
  const [observacaoAjuste, definirObservacaoAjuste] = useState("");
  const [imagemReferencia, definirImagemReferencia] = useState("");
  const [imagemDesenhoAprovado, definirImagemDesenhoAprovado] = useState("");
  const [carregandoReferencia, definirCarregandoReferencia] = useState(true);
  const [erroReferencia, definirErroReferencia] = useState("");
  const duracaoValida = Number.isInteger(Number(duracaoHoras)) && Number(duracaoHoras) >= 1 && Number(duracaoHoras) <= DURACAO_MAXIMA_HORAS;

  // Busca a referência enviada pela cliente ao abrir a ficha individual do pedido.
  useEffect(() => {
    pedirApi(`/tatuagens/${tatuagem.id}`)
      .then((dados) => definirImagemReferencia(dados.imagem_referencia || ""))
      .catch((erroApi) => definirErroReferencia(erroApi.message))
      .finally(() => definirCarregandoReferencia(false));
  }, [tatuagem.id]);

  // Consulta se o projeto já possui uma sessão reservada antes de oferecer outro agendamento.
  useEffect(() => {
    if (!etapaPermiteSessao) {
      definirSessaoAgendada(null);
      definirCarregandoSessao(false);
      definirErroConsultaSessao("");
      return;
    }

    let consultaAtiva = true;
    definirCarregandoSessao(true);
    definirErroConsultaSessao("");
    pedirApi(`/tatuagens/${tatuagem.id}/passos`)
      .then((passos) => {
        if (!consultaAtiva) return;
        const reserva = [...passos].reverse().find((passo) => passo.tipo === "sessao" && (passo.situacao || "agendada") === "agendada");
        definirSessaoAgendada(reserva || null);
      })
      .catch((erroApi) => { if (consultaAtiva) definirErroConsultaSessao(erroApi.message); })
      .finally(() => { if (consultaAtiva) definirCarregandoSessao(false); });

    return () => { consultaAtiva = false; };
  }, [tatuagem.id, tatuagem.etapa, etapaPermiteSessao]);

  // Localiza a reserva automática para permitir ajustar o retoque antes de confirmá-lo.
  useEffect(() => {
    if (tatuagem.etapa !== "aguardando retoque") {
      definirPassoRetoque(null);
      definirCarregandoPassoRetoque(false);
      return;
    }

    let consultaAtiva = true;
    definirCarregandoPassoRetoque(true);
    pedirApi(`/tatuagens/${tatuagem.id}/passos`)
      .then((passos) => {
        const reserva = [...passos].reverse().find((passo) => passo.tipo === "retoque_combinado" && (passo.situacao || "agendada") === "agendada");
        if (!reserva) throw new Error("Não encontrei um retoque agendado para este projeto.");
        if (consultaAtiva) {
          definirPassoRetoque(reserva);
          definirData(reserva.data);
          definirDuracaoHoras(String(reserva.duracao_horas || 2));
          definirHorario(reserva.horario?.slice(0, 5) || "");
        }
      })
      .catch((erroApi) => { if (consultaAtiva) definirErroHorarios(erroApi.message); })
      .finally(() => { if (consultaAtiva) definirCarregandoPassoRetoque(false); });

    return () => { consultaAtiva = false; };
  }, [tatuagem.id, tatuagem.etapa]);

  // Mostra o desenho enviado pelo tatuador enquanto a primeira sessão é agendada.
  useEffect(() => {
    if (tatuagem.etapa !== "desenho aprovado") return;
    pedirApi(`/tatuagens/${tatuagem.id}/passos`)
      .then((passos) => {
        const desenho = [...passos].reverse().find((passo) => passo.tipo === "desenho_enviado" && passo.imagem);
        definirImagemDesenhoAprovado(desenho?.imagem || "");
      })
      .catch((erroApi) => definirErroReferencia(erroApi.message));
  }, [tatuagem.id, tatuagem.etapa]);

  // Consulta a justificativa da cliente quando o tatuador precisa revisar o desenho.
  useEffect(() => {
    if (tatuagem.etapa === "ajustes no desenho") {
      pedirApi(`/tatuagens/${tatuagem.id}/passos`)
        .then((passos) => {
          const recusa = [...passos].reverse().find((passo) => passo.tipo === "desenho_reprovado");
          definirObservacaoAjuste(recusa?.observacao || "A cliente pediu ajustes no desenho.");
        })
        .catch((erroApi) => definirObservacaoAjuste(erroApi.message));
    }
  }, [tatuagem.id, tatuagem.etapa]);

  // Busca horários livres sempre que a data de uma sessão for escolhida.
  useEffect(() => {
    const ajustandoRetoque = tipo === "retoque" && tatuagem.etapa === "aguardando retoque";
    if ((tipo !== "sessao" && !ajustandoRetoque) || !data || !duracaoValida || (ajustandoRetoque && !passoRetoque)) {
      definirHorariosDisponiveis([]);
      definirCarregandoHorarios(false);
      definirErroHorarios("");
      if (!ajustandoRetoque) definirHorario("");
      return;
    }

    let consultaAtiva = true;
    definirCarregandoHorarios(true);
    definirErroHorarios("");
    definirHorariosDisponiveis([]);
    const parametroIgnorar = ajustandoRetoque ? `&ignorar_passo_id=${passoRetoque.id}` : "";
    pedirApi(`/tatuagens/horarios-disponiveis?data=${data}&duracao_horas=${duracaoHoras}${parametroIgnorar}`)
      .then((horarios) => {
        if (consultaAtiva) {
          definirHorariosDisponiveis(horarios);
          definirHorario((atual) => horarios.includes(atual) ? atual : horarios[0] || "");
        }
      })
      .catch((erroApi) => {
        if (consultaAtiva) definirErroHorarios(erroApi.message);
      })
      .finally(() => {
        if (consultaAtiva) definirCarregandoHorarios(false);
      });

    return () => {
      consultaAtiva = false;
    };
  }, [tipo, data, duracaoHoras, duracaoValida, passoRetoque?.id, tatuagem.etapa]);

  // Lê a imagem selecionada ou solta na área para anexá-la ao passo do desenho.
  function carregarDesenho(arquivo) {
    if (!arquivo) return;
    if (!arquivo.type.startsWith("image/")) {
      definirErro("Escolha um arquivo de imagem para enviar o desenho.");
      return;
    }
    if (arquivo.size > TAMANHO_MAXIMO_IMAGEM_BYTES) {
      definirErro("A imagem deve ter no máximo 5 MB.");
      return;
    }
    definirErro("");
    const leitor = new FileReader();
    leitor.onload = () => {
      definirImagem(leitor.result);
      definirNomeImagem(arquivo.name);
    };
    leitor.onerror = () => definirErro("Não foi possível ler essa imagem. Escolha o arquivo novamente.");
    leitor.readAsDataURL(arquivo);
  }

  // Recebe a imagem escolhida no seletor de arquivos.
  function selecionarDesenho(evento) {
    carregarDesenho(evento.target.files?.[0]);
  }

  // Permite soltar uma imagem diretamente na área de upload.
  function soltarDesenho(evento) {
    evento.preventDefault();
    definirArrastandoImagem(false);
    carregarDesenho(evento.dataTransfer.files?.[0]);
  }

  // Envia o novo passo e deixa a mensagem de recusa visível sem perder os dados.
  function enviarPasso(evento) {
    evento.preventDefault();
    definirErro("");
    if (enviarDesenho && !imagem) {
      definirErro("Selecione a imagem do desenho antes de enviar para a cliente.");
      return;
    }
    if (tipo === "retoque" && (!passoRetoque || !horario || carregandoHorarios)) {
      definirErro("Escolha um horário livre para a duração do retoque.");
      return;
    }
    definirSalvando(true);
    const atualizarReservaRetoque = tipo === "retoque"
      ? pedirApi(`/tatuagens/${tatuagem.id}/passos/${passoRetoque.id}/agendamento`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ duracao_horas: Number(duracaoHoras), horario }),
      })
      : Promise.resolve();
    atualizarReservaRetoque.then(() => pedirApi(`/tatuagens/${tatuagem.id}/passos`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tipo,
          data: tipo === "sessao" ? data : new Date().toISOString().slice(0, 10),
          horario: tipo === "sessao" ? horario : null,
          ...(tipo === "sessao" || tipo === "retoque" ? {
            duracao_horas: Number(duracaoHoras),
          } : {}),
          observacao: tipo === "sessao"
            ? `Sessão agendada por ${duracaoHoras} ${Number(duracaoHoras) === 1 ? "hora" : "horas"}.`
            : tatuagem.etapa === "aguardando retoque"
              ? `Retoque realizado por ${duracaoHoras} ${Number(duracaoHoras) === 1 ? "hora" : "horas"}.`
              : observacao,
          imagem: enviarDesenho ? imagem : null,
        }),
      }))
      .then(() => aoSalvar())
      .catch((erroApi) => definirErro(erroApi.message))
      .finally(() => {
        definirSalvando(false);
      });
  }

  // Desmarca a sessão e registra a mensagem que a cliente verá no histórico do pedido.
  function desmarcarSessao() {
    if (!sessaoAgendada || !mensagemCancelamento.trim()) {
      definirErroCancelamento("Escreva uma mensagem explicando o motivo do cancelamento.");
      return;
    }
    definirErroCancelamento("");
    definirCancelandoSessao(true);
    pedirApi(`/tatuagens/${tatuagem.id}/passos/${sessaoAgendada.id}/situacao`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ situacao: "cancelada", observacao: mensagemCancelamento.trim() }),
    })
      .then(() => aoSalvar())
      .catch((erroApi) => definirErroCancelamento(erroApi.message))
      .finally(() => definirCancelandoSessao(false));
  }

  const exibirFormulario = !etapaPermiteSessao || (!carregandoSessao && !erroConsultaSessao && !sessaoAgendada);

  return (
    <section className="painel-formulario">
      <button className="voltar" onClick={aoVoltar}>← Voltar para {nomeRetorno}</button>
      <div className="titulo-secao"><span className="sobretitulo">FICHA · {String(tatuagem.id).padStart(2, "0")}</span><h2>{tatuagem.etapa === "pedida" ? "Pedido recebido." : enviarDesenho ? "Revisar desenho." : tatuagem.etapa === "desenho aprovado" ? "Desenho Aprovado" : tatuagem.etapa === "aguardando retoque" ? "Retoque" : "Registrar um passo."}</h2><p>{nomeDaEtapa(tatuagem.etapa)}</p></div>
      {tatuagem.etapa === "desenho aprovado" && imagemDesenhoAprovado && <figure className="referencia-cliente previa-desenho-aprovado">
        <figcaption>Prévia do desenho aprovado</figcaption>
        <img src={imagemDesenhoAprovado} alt="Desenho aprovado pela cliente" />
      </figure>}
      {enviarDesenho && <section className="detalhes-pedido" aria-label="Pedido enviado pela cliente">
        <span className="sobretitulo">PEDIDO DA CLIENTE</span>
        <h3>{tatuagem.ideia}</h3>
        <dl>
          <div><dt>Local do corpo</dt><dd>{tatuagem.local_corpo}</dd></div>
          <div><dt>Tamanho aproximado</dt><dd>{tatuagem.tamanho}</dd></div>
        </dl>
        {tatuagem.etapa === "ajustes no desenho" && <p className="observacao-ajuste"><strong>O que a cliente pediu:</strong> {observacaoAjuste || "Carregando observação…"}</p>}
      </section>}
      {tatuagem.etapa !== "desenho aprovado" && imagemReferencia && <figure className="referencia-cliente">
        <figcaption>Imagem de referência enviada pela cliente</figcaption>
        <img src={imagemReferencia} alt="Referência de tatuagem enviada pela cliente" />
      </figure>}
      {erroReferencia && <p className="aviso aviso-erro" role="alert">{erroReferencia}</p>}
      {tatuagem.etapa !== "desenho aprovado" && !carregandoReferencia && !erroReferencia && !imagemReferencia && enviarDesenho && <p className="sem-referencia">A cliente não enviou uma imagem de referência.</p>}
      {etapaPermiteSessao && carregandoSessao && <p className="estado">Conferindo se já existe uma sessão marcada…</p>}
      {etapaPermiteSessao && erroConsultaSessao && <p className="aviso aviso-erro" role="alert">{erroConsultaSessao}</p>}
      {sessaoAgendada && <section className="bloco-sessao-agendada" aria-label="Sessão já marcada">
        <div><span className="sobretitulo">SESSÃO AGENDADA</span><h3>Este projeto já tem um horário reservado.</h3></div>
        <p>{formatarDataAgendamento(sessaoAgendada.data)} · {sessaoAgendada.horario?.slice(0, 5)} · {sessaoAgendada.duracao_horas || 2} {(sessaoAgendada.duracao_horas || 2) === 1 ? "hora" : "horas"}</p>
        {!abrirCancelamento
          ? <button className="botao botao-claro" type="button" disabled={cancelandoSessao} onClick={() => { definirAbrirCancelamento(true); definirMensagemCancelamento(""); definirErroCancelamento(""); }}>Desmarcar sessão</button>
          : <FormularioCancelamentoSessao
            id={`ficha-${sessaoAgendada.id}`}
            mensagem={mensagemCancelamento}
            aoAlterarMensagem={definirMensagemCancelamento}
            erro={erroCancelamento}
            salvando={cancelandoSessao}
            aoConfirmar={desmarcarSessao}
            aoFechar={() => { definirAbrirCancelamento(false); definirMensagemCancelamento(""); definirErroCancelamento(""); }}
          />}
      </section>}
      {exibirFormulario && <form onSubmit={enviarPasso} className="formulario">
        {enviarDesenho ? <>
          <label htmlFor="imagem-desenho">Desenho feito para a cliente</label>
          <div className={`area-upload ${arrastandoImagem ? "area-upload-ativa" : ""} ${imagem ? "area-upload-com-imagem" : ""}`} onDragOver={(evento) => { evento.preventDefault(); definirArrastandoImagem(true); }} onDragLeave={() => definirArrastandoImagem(false)} onDrop={soltarDesenho}>
            <input id="imagem-desenho" className="entrada-imagem-oculta" type="file" accept="image/*" onChange={selecionarDesenho} />
            <label className="conteudo-upload" htmlFor="imagem-desenho">
              {imagem ? <img className="previa-desenho" src={imagem} alt="Prévia do desenho selecionado" /> : <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M12 16V4m0 0L8 8m4-4 4 4" /><path d="M5 14v4a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-4" /></svg>}
              <strong>{imagem ? nomeImagem : "Arraste e solte o desenho para enviá-lo."}</strong>
              <span>{imagem ? "Imagem carregada · clique ou solte outra para substituir" : <>Ou <u>escolha uma imagem</u>. Formatos aceitos: PNG, JPG e outros formatos de imagem, até 5 MB.</>}</span>
            </label>
          </div>
        </> : tatuagem.etapa === "desenho aprovado" ? null : <>
          <label htmlFor="tipo-passo">O que foi feito?</label>
          <select id="tipo-passo" value={tipo} onChange={(evento) => definirTipo(evento.target.value)}>{tiposPermitidos.map((opcao) => <option key={opcao.valor} value={opcao.valor}>{opcao.nome}</option>)}</select>
        </>}
        {tipo === "sessao" && <>
          <label htmlFor="duracao-sessao">Duração da sessão (horas)</label>
          <input id="duracao-sessao" type="number" min="1" max={DURACAO_MAXIMA_HORAS} step="1" value={duracaoHoras} onChange={(evento) => definirDuracaoHoras(evento.target.value)} required />
          {duracaoHoras && !duracaoValida && <p className="aviso aviso-erro" role="alert">Informe uma duração inteira entre 1 e {DURACAO_MAXIMA_HORAS} horas.</p>}
          <label htmlFor="data-passo">Data da sessão</label>
          <input id="data-passo" type="date" min={hojeComoDataISO()} value={data} onChange={(evento) => definirData(evento.target.value)} required />
          <label htmlFor="horario-sessao">Horários disponíveis para {duracaoHoras || "a duração escolhida"} {Number(duracaoHoras) === 1 ? "hora" : "horas"}</label>
          <select id="horario-sessao" value={horario} onChange={(evento) => definirHorario(evento.target.value)} disabled={!duracaoValida || carregandoHorarios || horariosDisponiveis.length === 0} required>
            {carregandoHorarios && <option value="">Buscando horários…</option>}
            {!carregandoHorarios && horariosDisponiveis.length === 0 && <option value="">{mensagemSemHorarios(data)}</option>}
            {horariosDisponiveis.map((opcao) => <option key={opcao} value={opcao}>{opcao}</option>)}
          </select>
          {erroHorarios && <p className="aviso aviso-erro" role="alert">{erroHorarios}</p>}
        </>}
        {tipo === "retoque" && tatuagem.etapa === "aguardando retoque" && <>
          <label htmlFor="duracao-retoque">Duração do retoque (horas)</label>
          <input id="duracao-retoque" type="number" min="1" max={DURACAO_MAXIMA_HORAS} step="1" value={duracaoHoras} onChange={(evento) => definirDuracaoHoras(evento.target.value)} required />
          {duracaoHoras && !duracaoValida && <p className="aviso aviso-erro" role="alert">Informe uma duração inteira entre 1 e {DURACAO_MAXIMA_HORAS} horas.</p>}
          <p className="estado">Data prevista: {formatarDataAgendamento(data)}</p>
          <label htmlFor="horario-retoque">Horários que comportam essa duração</label>
          <select id="horario-retoque" value={horario} onChange={(evento) => definirHorario(evento.target.value)} disabled={!passoRetoque || !duracaoValida || carregandoPassoRetoque || carregandoHorarios || horariosDisponiveis.length === 0} required>
            {carregandoPassoRetoque || carregandoHorarios ? <option value="">Buscando horários…</option> : null}
            {!carregandoPassoRetoque && !carregandoHorarios && horariosDisponiveis.length === 0 && <option value="">{mensagemSemHorarios(data)}</option>}
            {horariosDisponiveis.map((opcao) => <option key={opcao} value={opcao}>{opcao}</option>)}
          </select>
          {erroHorarios && <p className="aviso aviso-erro" role="alert">{erroHorarios}</p>}
        </>}
        {tipo !== "sessao" && tatuagem.etapa !== "aguardando retoque" && <>
          <label htmlFor="observacao">Observação</label>
          <textarea id="observacao" value={observacao} onChange={(evento) => definirObservacao(evento.target.value)} required placeholder="Uma nota para o histórico da tatuagem" />
        </>}
        {erro && <p className="aviso aviso-erro" role="alert">{erro}</p>}
        <button className="botao botao-escuro" disabled={salvando || tipo === "sessao" && (!duracaoValida || !horario || carregandoHorarios) || tipo === "retoque" && (!duracaoValida || !passoRetoque || !horario || carregandoPassoRetoque || carregandoHorarios)}>{salvando ? "Enviando…" : tatuagem.etapa === "aguardando retoque" ? "Confirmar retoque realizado" : tipo === "sessao" ? "Marcar sessão para a cliente" : enviarDesenho ? "Enviar desenho para a cliente" : "Salvar passo"}<span aria-hidden="true">↗</span></button>
      </form>}
    </section>
  );
}

function TelaLogin({ aoEntrar }) {
  const [modoCadastro, definirModoCadastro] = useState(false);
  const [username, definirUsername] = useState("bruna");
  const [password, definirPassword] = useState("bruna123");
  const [nome, definirNome] = useState("");
  const [email, definirEmail] = useState("");
  const [senhaCadastro, definirSenhaCadastro] = useState("");
  const [confirmarSenha, definirConfirmarSenha] = useState("");
  const [senhaVisivel, definirSenhaVisivel] = useState(false);
  const [carregando, definirCarregando] = useState(false);
  const [erro, definirErro] = useState("");

  async function abrirSessao(identificador, senha) {
    const dadosToken = await pedirApi("/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ username: identificador, password: senha }),
    });
    localStorage.setItem("tinta_negra_token", dadosToken.access_token);
    const usuarioAtual = await pedirApi("/me");
    localStorage.setItem("tinta_negra_usuario", JSON.stringify(usuarioAtual));
    aoEntrar(usuarioAtual);
  }

  async function entrar(evento) {
    evento.preventDefault();
    definirErro("");
    definirCarregando(true);

    try {
      await abrirSessao(username, password);
    } catch (erroApi) {
      localStorage.removeItem("tinta_negra_token");
      localStorage.removeItem("tinta_negra_usuario");
      definirErro(erroApi.message || "Não foi possível entrar.");
    } finally {
      definirCarregando(false);
    }
  }

  async function cadastrar(evento) {
    evento.preventDefault();
    definirErro("");
    if (senhaCadastro !== confirmarSenha) {
      definirErro("As senhas não coincidem.");
      return;
    }

    definirCarregando(true);
    try {
      await pedirApi("/usuarios", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nome, email, senha: senhaCadastro }),
      });
      await abrirSessao(email, senhaCadastro);
    } catch (erroApi) {
      localStorage.removeItem("tinta_negra_token");
      localStorage.removeItem("tinta_negra_usuario");
      definirErro(erroApi.message || "Não foi possível criar sua conta.");
    } finally {
      definirCarregando(false);
    }
  }

  function alternarModoCadastro() {
    definirErro("");
    definirModoCadastro((modoAtual) => !modoAtual);
  }

  return (
    <section className="painel-formulario" style={{ maxWidth: 420, margin: "80px auto" }}>
      <div className="titulo-secao">
        <span className="sobretitulo">{modoCadastro ? "NOVA CONTA" : "ACESSO"}</span>
        <h2>{modoCadastro ? "Crie sua conta." : "Entrar no estúdio."}</h2>
        <p>{modoCadastro ? "Cadastre-se como cliente para acompanhar seus pedidos e sessões." : "Faça login para acessar a sua área de trabalho no sistema."}</p>
      </div>
      <form onSubmit={modoCadastro ? cadastrar : entrar} className="formulario">
        {modoCadastro ? <>
          <label htmlFor="nome-cadastro">Nome</label>
          <input id="nome-cadastro" autoComplete="name" value={nome} onChange={(evento) => definirNome(evento.target.value)} minLength="2" maxLength="100" required placeholder="Seu nome completo" />

          <label htmlFor="email-cadastro">E-mail</label>
          <input id="email-cadastro" type="email" autoComplete="email" value={email} onChange={(evento) => definirEmail(evento.target.value)} maxLength="254" required placeholder="voce@exemplo.com" />
        </> : <>
          <label htmlFor="username">Usuário ou e-mail</label>
          <input id="username" autoComplete="username" value={username} onChange={(evento) => definirUsername(evento.target.value)} placeholder="Seu usuário ou e-mail" required />
        </>}

        <label htmlFor="password">Senha{modoCadastro ? " (mínimo de 8 caracteres)" : ""}</label>
        <div className="campo-senha">
          <input id="password" type={senhaVisivel ? "text" : "password"} autoComplete={modoCadastro ? "new-password" : "current-password"} value={modoCadastro ? senhaCadastro : password} onChange={(evento) => (modoCadastro ? definirSenhaCadastro(evento.target.value) : definirPassword(evento.target.value))} minLength={modoCadastro ? "8" : undefined} maxLength={modoCadastro ? "128" : undefined} placeholder={modoCadastro ? "Crie uma senha" : "Digite sua senha"} required />
          <button
            className="botao-visualizar-senha"
            type="button"
            aria-label={senhaVisivel ? "Ocultar senha" : "Mostrar senha"}
            aria-controls="password"
            aria-pressed={senhaVisivel}
            onClick={() => definirSenhaVisivel((visivel) => !visivel)}
          >
            <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
              {senhaVisivel ? (
                <>
                  <path d="M3 3l18 18" />
                  <path d="M10.6 10.6a2 2 0 0 0 2.8 2.8" />
                  <path d="M9.9 5.2A10.8 10.8 0 0 1 12 5c5.5 0 9 7 9 7a15.5 15.5 0 0 1-3.1 3.9" />
                  <path d="M6.2 6.2C3.9 7.7 3 12 3 12s3.5 7 9 7a9.8 9.8 0 0 0 3.1-.5" />
                </>
              ) : (
                <>
                  <path d="M2.5 12s3.4-7 9.5-7 9.5 7 9.5 7-3.4 7-9.5 7-9.5-7-9.5-7Z" />
                  <circle cx="12" cy="12" r="3" />
                </>
              )}
            </svg>
          </button>
        </div>

        {modoCadastro ? <>
          <label htmlFor="confirmar-senha">Confirme sua senha</label>
          <input id="confirmar-senha" type={senhaVisivel ? "text" : "password"} autoComplete="new-password" value={confirmarSenha} onChange={(evento) => definirConfirmarSenha(evento.target.value)} minLength="8" maxLength="128" required placeholder="Digite a senha novamente" />
        </> : <small className="ajuda-campo">Demonstração: Bruna / bruna123 ou Vitor / vitor123</small>}

        {erro && <p className="aviso aviso-erro" role="alert">{erro}</p>}

        <button className="botao botao-escuro" disabled={carregando}>
          {carregando ? (modoCadastro ? "Criando conta…" : "Entrando…") : modoCadastro ? "Criar conta" : "Entrar"}<span aria-hidden="true">↗</span>
        </button>
        <p className="alternar-autenticacao">
          {modoCadastro ? "Já tem uma conta?" : "Ainda não tem conta?"}{" "}
          <button type="button" onClick={alternarModoCadastro} disabled={carregando}>{modoCadastro ? "Entrar" : "Cadastre-se"}</button>
        </p>
      </form>
    </section>
  );
}

// Apresenta as quatro telas da cartilha e troca os caminhos conforme o perfil escolhido.
export default function Aplicativo() {
  const [usuario, definirUsuario] = useState(null);
  const [verificandoSessao, definirVerificandoSessao] = useState(true);
  const [erroSessao, definirErroSessao] = useState("");
  const [tentativaValidacao, definirTentativaValidacao] = useState(0);
  const [tela, definirTela] = useState("visao-geral");
  const [telaAnteriorFicha, definirTelaAnteriorFicha] = useState("agenda");
  const [ficha, definirFicha] = useState(null);
  const [projetoCliente, definirProjetoCliente] = useState(null);
  const [atualizacao, definirAtualizacao] = useState(0);

  // Abre a tela inicial correspondente ao grupo da conta autenticada.
  function iniciarSessao(usuarioAtual) {
    definirFicha(null);
    definirProjetoCliente(null);
    definirTela(usuarioAtual.tipo === "cliente" ? "minhas" : "visao-geral");
    definirUsuario(usuarioAtual);
  }

  // Restaura a sessão somente depois de confirmar a identidade com a API.
  useEffect(() => {
    let consultaAtiva = true;

    function encerrarSessaoExpirada() {
      if (!consultaAtiva) return;
      definirUsuario(null);
      definirFicha(null);
      definirProjetoCliente(null);
      definirTela("visao-geral");
      definirErroSessao("");
      definirVerificandoSessao(false);
    }

    window.addEventListener("tinta-negra-sessao-expirada", encerrarSessaoExpirada);
    if (!localStorage.getItem("tinta_negra_token")) {
      localStorage.removeItem("tinta_negra_usuario");
      definirUsuario(null);
      definirVerificandoSessao(false);
      return () => {
        consultaAtiva = false;
        window.removeEventListener("tinta-negra-sessao-expirada", encerrarSessaoExpirada);
      };
    }

    definirVerificandoSessao(true);
    definirErroSessao("");
    pedirApi("/me")
      .then((usuarioAtual) => {
        if (!consultaAtiva) return;
        localStorage.setItem("tinta_negra_usuario", JSON.stringify(usuarioAtual));
        iniciarSessao(usuarioAtual);
      })
      .catch((erroApi) => {
        if (!consultaAtiva) return;
        definirUsuario(null);
        if (erroApi.status !== 401) {
          definirErroSessao("Não foi possível validar sua sessão. Confira a conexão com o estúdio e tente novamente.");
        }
      })
      .finally(() => {
        if (consultaAtiva) definirVerificandoSessao(false);
      });

    return () => {
      consultaAtiva = false;
      window.removeEventListener("tinta-negra-sessao-expirada", encerrarSessaoExpirada);
    };
  }, [tentativaValidacao]);

  if (verificandoSessao) {
    return <section className="painel-formulario" style={{ maxWidth: 420, margin: "80px auto" }}><p className="estado">Validando sua sessão…</p></section>;
  }

  if (erroSessao) {
    return <section className="painel-formulario" style={{ maxWidth: 420, margin: "80px auto" }}>
      <p className="aviso aviso-erro" role="alert">{erroSessao}</p>
      <button className="botao botao-escuro" type="button" onClick={() => definirTentativaValidacao((valor) => valor + 1)}>Tentar novamente</button>
      <button className="botao botao-claro" type="button" onClick={() => { localStorage.removeItem("tinta_negra_token"); localStorage.removeItem("tinta_negra_usuario"); definirErroSessao(""); }}>Voltar ao login</button>
    </section>;
  }

  if (!usuario) {
    return <TelaLogin aoEntrar={iniciarSessao} />;
  }

  const perfil = { nome: usuario.nome, tipo: usuario.tipo, clienteId: usuario.tipo === "cliente" ? usuario.id : null };

  // Alterna entre a lista da cliente e a tela independente de histórico do projeto.
  function abrirMinhasTatuagens() {
    definirProjetoCliente(null);
    definirTela("minhas");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function abrirHistoricoCliente(tatuagem) {
    definirProjetoCliente(tatuagem);
    definirTela("historico-cliente");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function abrirPedidoCliente() {
    definirProjetoCliente(null);
    definirTela("pedir");
  }

  function sair() {
    localStorage.removeItem("tinta_negra_token");
    localStorage.removeItem("tinta_negra_usuario");
    definirUsuario(null);
    definirFicha(null);
    definirProjetoCliente(null);
    definirTela("visao-geral");
  }

  function abrirAgenda() {
    definirFicha(null);
    definirTela("agenda");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function abrirProjetos() {
    definirFicha(null);
    definirTela("projetos");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function abrirVisaoGeral() {
    definirFicha(null);
    definirTela("visao-geral");
    window.scrollTo({ top: 0, behavior: "smooth" });
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

  // Atualiza a lista da cliente e volta à tela inicial depois que o pedido foi recebido.
  function concluirPedido() {
    definirAtualizacao((valor) => valor + 1);
    definirProjetoCliente(null);
    definirTela("minhas");
  }

  return (
    <div className={`aplicativo modo-${perfil.tipo}`}>
      <header className="barra-superior">
        <a className="marca" href="#inicio" onClick={perfil.tipo === "cliente" ? abrirMinhasTatuagens : abrirAgenda} aria-label="Tinta Negra Tattoo Studio">
          <span className="marca-simbolo" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round"><path d="M14.5 4.5 19 9 9 19H4.5v-4.5l10-10Z" /><path d="m12 7 5 5M4.5 19 3 21l2-1" /></svg></span>
          <span className="marca-texto"><strong>Tinta Negra</strong><small>Tattoo Studio</small></span>
        </a>
        <nav className="navegacao" aria-label="Navegação principal">
          {perfil.tipo === "tatuador" && <>
            <button className={tela === "visao-geral" ? "ativo" : "nav-inicio"} onClick={abrirVisaoGeral}><span className="icone-grade" aria-hidden="true">▦</span> Visão geral</button>
            <button className={tela === "agenda" || tela === "ficha" && telaAnteriorFicha === "agenda" ? "ativo" : "nav-agenda"} onClick={abrirAgenda}><span className="icone-grade" aria-hidden="true">▤</span> Agenda</button>
            <button className={tela === "projetos" || tela === "ficha" && telaAnteriorFicha === "projetos" ? "ativo" : "nav-projetos"} onClick={abrirProjetos}><span className="icone-grade" aria-hidden="true">☷</span> Projetos</button>
            <div className="selo-estudio"><span>DESDE 2018</span></div>
          </>}
        </nav>
        <div className="seletor-perfil">
          <span className="avatar-perfil" aria-hidden="true">{perfil.tipo === "cliente" ? "BM" : "VS"}</span>
          <span className="dados-perfil">
            <span>{perfil.tipo === "cliente" ? `Olá, ${perfil.nome}` : perfil.nome}</span>
            <small>{perfil.tipo === "cliente" ? "Cliente" : "Tatuador"}</small>
          </span>
          <button className="botao botao-ember" type="button" onClick={sair}>Sair</button>
        </div>
      </header>
      <main id="inicio" className="conteudo-principal">
        {tela === "minhas" && <section className="banner-cliente">
          <img className="banner-ornamento" src="/imagens/arabesco.png" alt="" />
          <div className="banner-conteudo"><span className="sobretitulo">SUA JORNADA NA PELE</span><h1>Histórias que ficam.</h1><p>Acompanhe cada traço, cada sessão e tudo o que vem depois.</p><button className="botao botao-ember" onClick={abrirPedidoCliente}><span aria-hidden="true">＋</span> Pedir tatuagem</button></div>
        </section>}
        {tela === "visao-geral" && <TelaVisaoGeral atualizacao={atualizacao} aoVerAgenda={abrirAgenda} aoAbrirFicha={abrirFicha} aoRegistrarPasso={registrarProximoPasso} aoAtualizar={() => definirAtualizacao((valor) => valor + 1)} />}
        <div className="coluna-conteudo">
          {tela === "pedir" && <TelaPedir perfil={perfil} aoVoltar={abrirMinhasTatuagens} aoCriar={concluirPedido} />}
          {tela === "minhas" && <TelaMinhasTatuagens key={atualizacao} perfil={perfil} aoAbrirHistorico={abrirHistoricoCliente} />}
          {tela === "historico-cliente" && projetoCliente && <TelaHistoricoCliente key={projetoCliente.id} perfil={perfil} tatuagem={projetoCliente} aoVoltar={abrirMinhasTatuagens} />}
          {tela === "agenda" && <TelaAgenda atualizacao={atualizacao} aoAtualizar={() => definirAtualizacao((valor) => valor + 1)} aoAbrirFicha={abrirFicha} />}
          {tela === "projetos" && <TelaProjetos atualizacao={atualizacao} aoAbrirFicha={abrirFicha} />}
          {tela === "ficha" && ficha && (ficha.etapa === "finalizada"
            ? <TelaPedidoFinalizado tatuagem={ficha} nomeRetorno={telaAnteriorFicha === "projetos" ? "projetos" : telaAnteriorFicha === "visao-geral" ? "visão geral" : "agenda"} aoVoltar={() => definirTela(telaAnteriorFicha)} />
            : <TelaFicha key={ficha.id} tatuagem={ficha} nomeRetorno={telaAnteriorFicha === "projetos" ? "projetos" : telaAnteriorFicha === "visao-geral" ? "visão geral" : "agenda"} aoVoltar={() => definirTela(telaAnteriorFicha)} aoSalvar={salvarPasso} />)}
        </div>
      </main>
      {perfil.tipo === "cliente" && <nav className="navegacao-mobile" aria-label="Navegação da cliente">
        <button className={tela === "minhas" || tela === "historico-cliente" ? "ativo" : ""} onClick={abrirMinhasTatuagens}>☷ <span>Minhas tatuagens</span></button>
        <button className={tela === "pedir" ? "ativo" : ""} onClick={abrirPedidoCliente}>＋ <span>Novo pedido</span></button>
      </nav>}
      <footer className="rodape"><span>UM PASSO DE CADA VEZ.</span><span>TINTA NEGRA · TATTOO STUDIO</span></footer>
    </div>
  );
}
