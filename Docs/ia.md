# Funcionalidade de IA: sugestão de priorização de projetos

**Status:** planejada  
**Provedor previsto:** Claude via API  
**Validação manual do prompt:** pendente

## Problema e oportunidade

O briefing relata dificuldade de acompanhar o andamento dos projetos e da agenda quando as informações ficam espalhadas em conversas. A Cartilha descreve a necessidade de Vitor identificar tatuagens que aguardam a próxima etapa. Isso sustenta explorar uma sugestão de ordem de atenção, sem criar uma regra automática de prioridade: o briefing não define critérios formais para decidir quem vem primeiro.

Fontes: [Docs/BRIEFING.md](BRIEFING.md) (acompanhamento dos projetos, agenda e telas de Vitor); [Docs/CARTILHA.md](CARTILHA.md) (andamento por etapas e trabalho que aguarda a próxima etapa).

## Proposta

Bruna e Vitor poderão consultar uma lista ordenada sugerida por IA, acompanhada das justificativas baseadas nos dados recebidos. A pessoa revisa a sugestão e decide como continuar. A IA não altera projetos, agenda, etapas ou prioridades salvas. As regras da Cartilha continuam aplicadas pelo serviço.

### Papel, dados, ferramentas e limites

- **Papel:** apoiar Bruna e Vitor na revisão da ordem de atenção dos projetos.
- **Entrada por projeto:** código fictício, etapa atual, histórico recente, próxima ação pendente e compromissos ou prazos.
- **Ferramentas:** nenhuma ferramenta é exposta ao modelo. Na integração prevista, o backend enviará os dados à API do Claude; o modelo não consultará diretamente o banco nem a agenda.
- **Acesso:** o backend deve enviar apenas projetos que a pessoa tenha permissão para consultar; o prompt não substitui o controle de acesso do serviço.
- **Limites:** usar somente sinais explícitos nos dados, sem inventar fatos, regras, pesos ou prazos. A resposta é sugestão para revisão humana, sem gravação automática.
- **Falha ou ausência de resposta:** a pessoa continua a tarefa pelas listas, filtros e agenda existentes. A IA não deve bloquear o fluxo.

### Modelo de execução previsto

Uma única chamada ao Claude recebe a instrução abaixo e os dados enviados pelo backend. Isso atende ao escopo atual porque há uma tarefa e uma resposta para revisão humana. Não se propõem agentes com ferramentas nem vários agentes: não há, até aqui, fontes que o modelo precise consultar diretamente ou responsabilidades independentes que justifiquem dividir o trabalho.

## Prompt para teste manual

```text
Você é um assistente de apoio à priorização de projetos de tatuagem usado por Bruna e Vitor.

TAREFA
Produza uma sugestão de ordem de atenção para os projetos recebidos. Baseie-se somente nos dados fornecidos: etapa atual, histórico recente, próxima ação pendente e compromissos ou prazos explícitos. A ordem é uma recomendação para uma pessoa revisar.

ENTRADA
Você recebe uma lista de projetos com código, etapa atual, histórico recente, próxima ação pendente e compromissos ou prazos. Não solicite nomes, contatos ou outros dados pessoais.

LIMITES
Não invente fatos, prazos, etapas, ações, responsáveis ou critérios de prioridade. Não atribua notas ou pesos. Se os sinais forem insuficientes ou não permitirem comparar projetos, diga isso claramente e identifique quais projetos não têm ordem determinável. Você não tem ferramentas, não consulta outros sistemas e não altera dados. Não decida mudanças no processo; as regras da Cartilha são aplicadas pelo serviço.

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

## Pontos ainda não definidos

- ? A tela específica onde a lista será exibida.
- ? A forma de selecionar e montar os projetos que cada pessoa autorizada verá no payload.
- ? Os resultados dos três testes manuais.

## Fora do escopo desta etapa

Não houve alteração de código nem implementação da integração. A atualização do briefing e do roadmap fica para etapas futuras.
