# RIGHTWARE Intelligence Engine — Estratégia de tecnologia proprietária R0

**Data:** 2026-11-18 (Africa/Maputo). **Estado:** INTENÇÃO ESTRATÉGICA EXPLÍCITA DO OPERADOR; ARQUITETURA PROPOSTA; motor produtivo NÃO IMPLEMENTADO.

## 1. Princípio de propriedade tecnológica

O operador reiterou: RIGHTWARE deve desenvolver o **próprio motor de inteligência e ciência de dados**, não limitar-se à engenharia reversa, Mem0, Hindsight, Ollama, Qwen ou modelos alheios. Esta é uma orientação estratégica — **não** prova de propriedade intelectual exclusiva, de treino de LLM, de precisão demonstrada ou de decisão de produto comercial. A marca RIGHTWARE é a entidade tecnológica; JARVIS e PULSE são consumidores potenciais distintos, não sinónimos do motor.

**O que deverá pertencer à RIGHTWARE:** contratos e datasets próprios legalmente constituídos, modelos especializados treinados quando justificados, políticas de recuperação/atualização de memória, features e ranking, calibração de incerteza, auditoria de fontes, gestão de conflitos e temporalidade, decisão de responder/abster/negar, experimentação e avaliação quantitativa, versionamento e interfaces estáveis.

**O que pode ser substituível:** PostgreSQL e índice lexical, motor vetorial, Mem0/Hindsight, embeddings, modelos de linguagem base, GPU/CPU, API e serviços. Cada dependência tem de ser tratada como infraestrutura ou baseline, não como inteligência proprietária demonstrada.

## 2. Camadas propostas (motor em pesquisa, não lançamento)

1. **Trusted Identity and Scope Gate (G04):** autenticação HUMAN e SERVICE, tenant/project/resource e consentimento; produzir contexto de autorização derivado do servidor. G04-A0 tem apenas evaluator sintético; OIDC/RLS reais NÃO existem.
2. **Evidence Registry (Core atual):** PostgreSQL imutável para eventos/estados/evidências, fonte autorizada, validade, proveniência, ref/source_id; Mem0 é memória sem autoridade.
3. **Retrieval Layer:** lexical e semântica, pesquisa temporal, códigos exatos, filtro do âmbito **antes da recuperação**.
4. **RIGHTWARE Evidence Ranker:** algoritmo próprio a desenvolver, features interpretáveis lexical/semanticidade/autoridade/tempo/proveniência, trainable reranker e método de aprendizagem controlada; BM25 como comparação pública de referência.
5. **RIGHTWARE Knowledge State:** liga factos a fontes e intervalos temporais, reconhece substituições, contradições e graus de verificação.
6. **RIGHTWARE Confidence/Decision:** calibração e política de `EVIDENCE_CANDIDATE/ABSTAIN/CONFLICT/DENY` com custos de erro e evidência citável; nunca promover contexto Mem0 a prova.
7. **Model/Agent Adapter:** Qwen/Ollama ou outro LLM é um *realizador de linguagem* opcional, não o verificador; execução de ferramentas e aprovação de tarefas continuam separadas no JARVIS/PULSE.
8. **Experiment and Governance:** datasets blindados, treino/dev/test sem fuga, experimentos reprodutíveis, CI, relatórios de modelo e cartões de risco.

O termo "modelo RIGHTWARE" deve apontar inicialmente para a família de modelos de **recuperação, ranking, atualização de conhecimento e decisão evidencial**. Não confundir com um LLM fundacional já treinado.

## 3. Primeiro protótipo E0 entregue em pesquisa

`backend/rightware_si/experimental_engine_e0.py`: motor **offline**, sem DB, sem rede, sem modelo vendor, sem autenticação real; usa ranking lexical BM25 (algoritmo padrão, não IP exclusiva) + filtragem de organização/projeto sintéticos e validade temporal + restrição da autoridade e conflitos. Produz **candidatos de evidência, não respostas confirmadas**. `trusted_scope` é uma asserção simulada do caller, **não autenticação**. A autoridade dos documentos é também injetada por fixture confiável experimental. Não ligar a HTTP, MCP, Mem0, nem usar para decisões de clientes/produção.

`tests/test_rightware_engine_e0.py` contém 22 testes puros. Base SI-MH-0062 tinha 237 testes; esperado 259, mas novos testes devem ser validados em CI antes de PASS. Os 28 oráculos G04 continuam NOT_IMPLEMENTED.

## 4. O que é decisão oficial e o que ainda é hipótese

| Item | Classificação |
|---|---|
| RIGHTWARE pretende deter motor próprio de IA/ciência de dados | DIREÇÃO ESTRATÉGICA EXPLÍCITA |
| Shared Intelligence como núcleo de memória, contexto e continuidade verificável | ARQUITETURA EXISTENTE/EM EVOLUÇÃO; G01 LAB verificado |
| E0 lexical + autoridade/tempo como referência | EXPERIMENTO DE ENGENHARIA, não motor ML treinado |
| Modelos de ranking, estimativa de confiança e atualização temporal | HIPÓTESES DE I&D a validar por benchmark |
| Treinar LLM fundacional RIGHTWARE | NÃO APROVADO / sem necessidade demonstrada |
| Selecionar PostgreSQL Server/Mem0/Hindsight | COMPARAÇÃO INCONCLUSA, não decisão |
| Disponibilizar motor a JARVIS/PULSE ou clientes | NÃO AUTORIZADO até integração e segurança |
| Adotar datasets privados de utilizadores para treino | NÃO AUTORIZADO; consentimento/retenção abertos |

## 5. Moat/valor de produto a comprovar

A proposta de diferenciação não deve ser "também temos embeddings". Deve ser: **inteligência operacional verificável**, capaz de recuperar o contexto correto no tempo certo, atribuir autoridade real às fontes, identificar conflitos, manter continuidade entre sessões/agentes e recusar conclusões sem suporte. Vantagens competitivas só podem ser afirmadas após ganho consistente contra baselines abertos sob mesmas condições, custos controlados, segurança e generalização a dados novos.

**Regras de investigação:** INVESTIGAR → COMPARAR → VALIDAR → DIFERENCIAR → CONSTRUIR. Engenharia reversa serve para estudar interfaces/limites de componentes públicos compatível com licenças, nunca para copiar código proprietário ou suprimir autoria. Evidência de patenteabilidade ou exclusividade requer exame técnico/legal independente.

## 6. Ligação com G04 e produtos

G04-A1 identidade e G04-A2 isolamento não constituem o motor inteligente, mas são **pré-requisitos obrigatórios** para acesso privado/empresarial. O motor deve ser testado com corpora públicos/sintéticos e escopos fidedignos sem aceder a dados reais. JARVIS retém seu `_GuardedEngine`, permissões por ferramenta, `ToolOutcome` e `TaskTrace`; Shared fornece memória, checkpoints, evidência e conhecimento recuperável, **não** prova de execução do JARVIS. PULSE consome inteligência operacional sob permissões próprias. O acoplamento é por contratos, não por importar o PostgreSQL/Core completo em cada produto.

**Next:** protocolo científico R0 → E1 retrieval instrumentado no dataset público de desenvolvimento → E2 reranking treinável e calibração apenas depois de splits/pré-registo → comparação vendor no benchmark blindado sem vazar o oráculo → integração sob G04 aprovado.
