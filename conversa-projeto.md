# Histórico da conversa — Tinta Negra Tattoo Studio

**Data do registro:** 21/10/2026  
**Formato:** resumo cronológico para importar como contexto em outra conversa. As decisões e solicitações importantes foram preservadas; não é uma transcrição literal de cada mensagem.

## Contexto do projeto

O sistema atende duas personas: **Bruna**, cliente, e **Vitor**, tatuador. O fluxo acompanha pedidos de tatuagem, etapas do projeto, agenda, sessões e mensagens registradas no histórico.

## Solicitações e alterações discutidas

1. **Grupos e permissões:** foi solicitada uma funcionalidade em que cada persona corresponda a um grupo de usuários, com permissões de acesso às rotas. O código dessa funcionalidade deveria ser comentado e identificado.
2. **Execução local:** foram solicitados o início do backend e, depois, do frontend.
3. **Login:** foi pedido um controle para mostrar ou ocultar a senha.
4. **Direcionamento por persona:** após o login de Bruna, o sistema mostrava uma página semelhante à inicial do tatuador. O fluxo foi ajustado para levar a cliente à área de suas tatuagens e manter a visão geral para o tatuador.
5. **Sessões:** foi pedido que, após marcar uma sessão, não apareça outra opção para marcá-la novamente. O tatuador pode desmarcar a sessão e deve escrever uma mensagem explicando o cancelamento; a mensagem fica no histórico visível à cliente. Também foi incluída a proteção contra uma segunda sessão ativa para o mesmo projeto.
6. **Histórico da cliente:** foi pedido que selecionar o cartão de um projeto abra uma tela própria com o histórico de etapas e mensagens. A navegação foi separada no estado principal do app para que a tela de histórico não mantenha o banner ou a lista inicial visíveis. A cliente pode voltar à lista.
7. **Ajustes visuais da cliente:** o fundo da área da cliente ficou em tom escuro, os cartões de projeto foram clareados para destacá-los e as fontes de textos e controles foram ampliadas.

## Ideia de IA registrada

O usuário pediu uma análise do briefing para encontrar oportunidades de funcionalidades que dependam de IA, considerando Bruna e Vitor. A oportunidade escolhida foi apoiar a organização dos projetos e da agenda: Vitor tem dificuldade para acompanhar os pedidos, identificar em que etapa está cada processo e decidir quais projetos merecem atenção primeiro.

### Decisões confirmadas

- A funcionalidade deve servir tanto a Bruna quanto a Vitor.
- Provedor previsto: API do Claude.
- A resposta será uma lista ordenada de projetos, acompanhada de justificativas de apoio.
- Dados por projeto: código fictício, etapa atual, histórico recente, próxima ação pendente e compromissos ou prazos.
- A IA deve usar somente sinais explícitos nos dados; a ordem é sugestão para revisão humana.
- O backend envia os dados permitidos ao modelo. O modelo não recebe ferramentas, não consulta outros sistemas e não altera registros.
- As regras da Cartilha continuam sendo aplicadas pelo serviço. A revisão e a decisão final permanecem com uma pessoa.
- Para o escopo atual, uma chamada ao modelo é suficiente. Não há responsabilidades independentes ou ferramentas que justifiquem vários agentes.
- Se a IA falhar ou não responder, a pessoa continua o trabalho pelas listas, filtros e agenda existentes.

O registro detalhado, incluindo o prompt de teste manual e três entradas de teste pendentes, está em [`Docs/ia.md`](Docs/ia.md). Os testes avaliam as instruções no chat; não validam a integração pela API, ferramentas ou coordenação de agentes. Nenhum resultado foi marcado como realizado.

## Commits relevantes

- `09470b4` — `docs: registra proposta de priorização com IA`
- `3455243` — `feat: melhora login e gestão de sessões`
- `f398b16` — `feat: destaca histórico e interface da cliente`

## Estado conhecido ao gerar este arquivo

- O commit mais recente é `f398b16`.
- A árvore de trabalho estava limpa após esse commit.
- Os testes não foram executados para as alterações de interface descritas acima.
- A ideia de IA permanece planejada; a integração não foi implementada.

