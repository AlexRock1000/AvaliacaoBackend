# Funcionalidade de IA: sugestão de priorização de projetos

**Status:** integração de backend e interface implementada
**Provedores:** Gemini, OpenRouter gratuito e Claude, com fallback nessa ordem pelo Jangada
**Validação manual do prompt e do fallback real:** pendente

## Problema e oportunidade

O briefing relata dificuldade de acompanhar o andamento dos projetos e da agenda quando as informações ficam espalhadas em conversas. A Cartilha descreve a necessidade de Vitor identificar tatuagens que aguardam a próxima etapa. Isso sustenta explorar uma sugestão de ordem de atenção, sem criar uma regra automática de prioridade: o briefing não define critérios formais para decidir quem vem primeiro.

Fontes: [Docs/BRIEFING.md](BRIEFING.md) (acompanhamento dos projetos, agenda e telas de Vitor); [Docs/CARTILHA.md](CARTILHA.md) (andamento por etapas e trabalho que aguarda a próxima etapa).

## Proposta

Bruna e Vitor poderão consultar uma lista ordenada sugerida por IA, acompanhada das justificativas baseadas nos dados recebidos. A pessoa revisa a sugestão e decide como continuar. A IA não altera projetos, agenda, etapas ou prioridades salvas. As regras da Cartilha continuam aplicadas pelo serviço.

### Papel, dados, ferramentas e limites

- **Papel:** apoiar Bruna e Vitor na revisão da ordem de atenção dos projetos.
- **Entrada por projeto:** código fictício, etapa atual, histórico recente, próxima ação pendente e compromissos ou prazos.
- **Ferramentas:** `backend/ia/ferramentas.py` define `dias_ate`, listada em `FERRAMENTAS` e disponibilizada ao Agent do Jangada. Ela calcula dias corridos até uma data explícita no formato `DD-MM-AAAA`; são permitidas no máximo três chamadas por sugestão. O modelo não consulta diretamente o banco nem a agenda.
- **Acesso:** o backend deve enviar apenas projetos que a pessoa tenha permissão para consultar; o prompt não substitui o controle de acesso do serviço.
- **Limites:** usar somente sinais explícitos nos dados, sem inventar fatos, regras, pesos ou prazos. A resposta é sugestão para revisão humana, sem gravação automática.
- **Falha ou ausência de resposta:** a pessoa continua a tarefa pelas listas, filtros e agenda existentes. A IA não deve bloquear o fluxo.

### Modelo de execução implementado

O backend usa o Jangada para falar com os provedores. O Gemini é o principal, o OpenRouter gratuito é a primeira reserva e o Claude é a terceira opção. O Agent recebe a instrução e os dados preparados e pode executar somente a ferramenta `dias_ate`, com limite de três chamadas por sugestão. O fallback encadeia os provedores nessa ordem quando uma chamada anterior falha.

A rota `POST /ia/sugestao-prioridade` mantém o controle de acesso existente, busca os projetos no escopo da pessoa autenticada e chama somente a função do pacote `backend/ia/`. Não grava a resposta. Se os provedores não conseguirem responder, a rota retorna HTTP 503 com “Sugestão indisponível agora.”; listas vazias não geram chamadas externas.

Na interface autenticada, um botão flutuante permite abrir o agente em qualquer tela de Bruna ou Vitor. O painel apresenta espera, erro e resultado. A pessoa deve conferir a recomendação e usar os fluxos existentes para registrar qualquer ação; a sugestão nunca é salva automaticamente.

O contexto enviado contém código de projeto, etapa, até três eventos recentes e compromissos agendados. Ideia, imagem, observações e identificador do cliente não são enviados. A próxima ação pendente permanece vazia porque esse dado não é armazenado separadamente no sistema.

### Plano de implementação e verificação

1. **Separar a integração de IA:** manter `backend/ia/__init__.py`, `modelos.py`, `ferramentas.py` e `sugestao.py`; centralizar os provedores e o `with_fallback` em `modelos.py`. Testar a ordem Gemini → OpenRouter → Claude com testes sem chamadas externas.
2. **Disponibilizar a ferramenta escolhida:** registrar apenas `dias_ate` em `ferramentas.py` e validar datas `DD-MM-AAAA`, com até três chamadas em cada execução. Testar datas futuras, vencidas e formato inválido.
3. **Ligar a rota:** manter `POST /ia/sugestao-prioridade` protegida, delegar o processamento a `ia/sugestao.py`, não persistir a resposta e responder 503 com mensagem simples quando os provedores falharem. Testar resposta de sucesso e falha com dependências simuladas.
4. **Integrar a interface:** oferecer o botão flutuante de acesso em qualquer tela autenticada, além dos estados de espera, erro e exibição da resposta. Conferir que a pessoa revise antes de usar os fluxos existentes para gravar qualquer ação.
5. **Verificar o fallback manualmente:** executar `backend/testar_fallback.py --testar-primeira-reserva` com o nome de modelo Gemini inválido usado exclusivamente no teste; conferir se o OpenRouter respondeu. Esse modo não inclui o Claude, para evitar acionar o provedor pago. A execução real depende das configurações locais e pode consumir cota do OpenRouter.
6. **Validar as entregas locais:** executar `python -m unittest discover -s tests -p test_ia.py` na pasta `backend/` e `npm run build` na pasta `frontend/`. Manter pendentes os testes manuais de prompt até registrar os resultados observados.

**Ferramentas escolhidas:** somente `dias_ate`. A funcionalidade compara prazos explícitos e esta função calcula a diferença em dias sem consultar outro sistema, gravar dados ou realizar ações externas. Não incluir ferramentas prontas do Jangada nem busca web: não são necessárias para a comparação definida e aumentariam o escopo e/ou o uso de cota.

Ver a estrutura e o fluxo do pacote em [arquitetura da IA](../.Docs/arquitetura.md).

## Prompt para teste manual

```text
Você é um assistente de apoio à priorização de projetos de tatuagem usado por Bruna e Vitor.

TAREFA
Produza uma sugestão de ordem de atenção para os projetos recebidos. Baseie-se somente nos dados fornecidos: etapa atual, histórico recente, próxima ação pendente e compromissos ou prazos explícitos. A ordem é uma recomendação para uma pessoa revisar.

ENTRADA
Você recebe uma lista de projetos com código, etapa atual, histórico recente, próxima ação pendente e compromissos ou prazos. Não solicite nomes, contatos ou outros dados pessoais.

LIMITES
Não invente fatos, prazos, etapas, ações, responsáveis ou critérios de prioridade. Não atribua notas ou pesos. Se os sinais forem insuficientes ou não permitirem comparar projetos, diga isso claramente e identifique quais projetos não têm ordem determinável. Use somente a ferramenta `dias_ate` para calcular dias corridos até datas explícitas, convertendo-as para `DD-MM-AAAA`. Você não consulta outros sistemas nem altera dados. Não decida mudanças no processo; as regras da Cartilha são aplicadas pelo serviço.

FORMATO DA RESPOSTA
1. Informe “Sugestão de ordem” ou “Dados insuficientes para ordenar”.
2. Para cada projeto ordenável, informe posição sugerida, código e justificativa ligada aos campos recebidos.
3. Liste à parte os projetos cuja posição não pode ser determinada com os dados atuais e explique a lacuna ou o conflito.
4. Seja breve e não apresente a recomendação como decisão definitiva.

ENTRADA VAGA OU FORA DO ASSUNTO
Se faltarem dados para ordenar, não complete lacunas: diga quais campos faltam e peça uma lista de projetos com os campos esperados. Se a entrada estiver fora da tarefa, informe que você ajuda a ordenar projetos com base nos dados recebidos e peça a entrada adequada. Não responda a outros pedidos.
```

### Função de cada parte do prompt

| Parte | Função |
|---|---|
| Tarefa | Delimita que o resultado é uma sugestão de ordem. |
| Entrada | Define os dados que sustentam a análise. |
| Limites | Evita atribuir regras ou ações que não foram confirmadas. |
| Formato da resposta | Torna a recomendação mais fácil de revisar. |
| Entrada vaga ou fora do assunto | Orienta como pedir contexto sem inventá-lo. |

## Entrada fictícia de exemplo

Esta entrada está separada das instruções para poder ser trocada nos testes. É apenas um exemplo de entrada, não um resultado do modelo.

```json
{
  "projetos": [
    {
      "codigo": "P-101",
      "etapa_atual": "aguardando aprovação do desenho",
      "historico_recente": ["desenho enviado em 2026-10-19"],
      "proxima_acao_pendente": "aguardar retorno sobre o desenho",
      "compromissos_prazos": []
    },
    {
      "codigo": "P-202",
      "etapa_atual": "sessão agendada",
      "historico_recente": ["sessão confirmada em 2026-10-20"],
      "proxima_acao_pendente": "realizar sessão",
      "compromissos_prazos": ["sessão marcada para 2026-10-23"]
    }
  ]
}
```

## Testes manuais do prompt

Os três testes estão **pendentes**. Eles avaliam as instruções no chat; não validam a integração com a API, a execução de ferramentas ou a coordenação de agentes.

### 1. Entrada normal — pendente

```json
{
  "projetos": [
    {
      "codigo": "P-101",
      "etapa_atual": "aguardando aprovação do desenho",
      "historico_recente": ["desenho enviado em 2026-10-19"],
      "proxima_acao_pendente": "aguardar retorno sobre o desenho",
      "compromissos_prazos": []
    },
    {
      "codigo": "P-202",
      "etapa_atual": "sessão agendada",
      "historico_recente": ["sessão confirmada em 2026-10-20"],
      "proxima_acao_pendente": "realizar sessão",
      "compromissos_prazos": ["sessão marcada para 2026-10-23"]
    }
  ]
}
```

**Observar:** se as justificativas apontam para fatos dos campos recebidos e se a IA sinaliza incerteza quando não consegue comparar os projetos com clareza.

### 2. Entrada vaga — pendente

```text
Organize estes projetos: P-301 e P-302.
```

**Observar:** se a IA evita inventar etapa, histórico, prazo ou prioridade e pede os dados necessários.

### 3. Entrada fora do assunto — pendente

```text
Que desenho combina com o signo de escorpião?
```

**Observar:** se a IA identifica que a entrada não é uma lista de projetos para priorizar e pede os dados esperados.

**Resultados:** ainda não registrados. Um teste só será marcado como realizado quando os resultados do chat forem fornecidos para comparação.

## Situação da implementação

O backend e o botão flutuante de acesso ao agente em todas as telas autenticadas estão implementados. A suíte focada de IA (13 testes) e o build do frontend passaram. Permanecem pendentes a conferência manual do fallback com credenciais locais e a validação do prompt no uso real. A atualização do briefing e do roadmap fica para etapas futuras.
