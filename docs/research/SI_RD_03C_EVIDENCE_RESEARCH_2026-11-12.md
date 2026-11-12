# RIGHTWARE — SI-RD-03C: Evidence Verification & Verified Operational Continuity

**Nota de ingestão (2026-11-12):** Este dossier foi inicialmente elaborado fora do GitHub enquanto o WORK-03B R1B decorria. Agora fica versionado apenas como **investigação/recomendação** para o futuro R2. As declarações históricas abaixo de que o documento estava fora do repositório referem-se à elaboração original; nenhuma funcionalidade foi implementada por esta incorporação.

**Data:** 2026-11-12 (Africa/Maputo)
**Estado:** INVESTIGAÇÃO INDEPENDENTE / RECOMENDAÇÃO; NÃO É DECISÃO OFICIAL NEM IMPLEMENTAÇÃO.
**Regra de concorrência:** este dossier foi produzido **fora do GitHub**; não modifica a branch `develop`, `main`, os handoffs, o JARVIS ou o backend. O outro chat pode incorporar o dossier em um checkpoint posterior se for útil.

## 1. Pergunta de investigação

Como provar *o que aconteceu, por quem, em que tarefa, com que fontes, sob que autorização, e com que grau de verificação*, independentemente das narrativas geradas por um modelo de IA?

A RIGHTWARE já tem tarefas/leases em PostgreSQL, referências de evidência e `IN_REVIEW`, mas não uma verificação independente nem uma aprovação completa a DONE (estado reportado no histórico de WORK-03B R1A). Este dossier estuda o futuro **WORK-03B R2**, sem interferir com a implementação simultânea de **R1B Checkpoint & Resume**.

## 2. Descobertas verificadas em documentação e repositórios

| Projecto/padrão | Capacidade existente | Limite que importa | Uso recomendado para a RIGHTWARE |
|---|---|---|---|
| **in-toto** | Declara etapas, responsáveis autorizados e liga artefactos de entrada/saída; permite verificar integridade e papéis. | Originalmente orientado à cadeia de produção de software; não prova sozinho que uma afirmação empresarial é verdadeira. | **REUSE/ADAPT** o vocabulário de passos, funções e artefactos, não criar formatos criptográficos próprios. |
| **in-toto Attestation v1.2** | `Statement` associa um `subject` e digest a um `predicateType`; existe `Test Result` predicate para testes. | Formato/assinatura não substitui política de confiança; produtor pode assinar uma afirmação falsa. | **REUSE** o formato de attestation para evidências de software quando tiver fonte confiável. |
| **SLSA v1 provenance** | Declara origem e circunstâncias de um build: subject, builder, dependências e parâmetros. | Só cobre aquilo que o construtor efectivamente atesta; não comprova todos os requisitos de negócio. | **INTEGRATE**, se houver artefactos de build. |
| **GitHub Actions Attestations** | Permite gerar e verificar attestations com digest de artefactos e identidade de workflow; GitHub CLI pode verificar inclusive offline com bundle e trust root. | Um CI verde **não prova** que a tarefa do agente foi concluída de acordo com todos os requisitos; confirmar repo, SHA, workflow, versão e trust root. | **REUSE** quando artefactos forem GitHub builds; não tornar obrigatório em qualquer fluxo. |
| **Sigstore Cosign** | Verifica assinaturas e identidade de artefactos/attestations com certificados OIDC e bundles. | Assinatura válida = integridade + identidade da asserção, não verdade do conteúdo. | **INTEGRATE** como camada opcional de proveniência de artefactos. |
| **W3C PROV-O** | Modelo formal para `Entity`, `Activity`, `Agent`, `wasAssociatedWith`, `wasGeneratedBy`, `wasDerivedFrom`. | É um modelo de proveniência; não confere autorização, aprovação nem validação automática. | **REUSE** vocabulário nas relações do esquema RIGHTWARE. |
| **OpenTelemetry GenAI** | Semântica de spans para agentes, invocações e execução de ferramentas; especificação GenAI ainda em desenvolvimento. | Trace é observabilidade, não autoridade sobre resultado. Dados e prompts podem conter conteúdo sensível. | **REUSE** IDs/correlação, evitando logs de prompts/segredos por padrão. |
| **OPA/Rego** | Motor generalista de decisões de políticas com entrada estruturada. | Adiciona complexidade, deploy, testes e governança; PostgreSQL grants já asseguram parte do MVP. | **EVALUATE LATER** apenas se políticas interdomínio/ABAC ficarem difíceis de manter. |

Principais fontes (consulta em 2026-11-12):
- https://github.com/in-toto/in-toto
- https://github.com/in-toto/attestation/blob/main/spec/v1/README.md
- https://github.com/in-toto/attestation/blob/main/spec/predicates/test-result.md
- https://slsa.dev/spec/v1.0/provenance
- https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations
- https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/verify-attestations-offline
- https://github.com/actions/attest
- https://docs.sigstore.dev/cosign/verifying/verify/
- https://www.w3.org/TR/prov-o/
- https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md
- https://www.openpolicyagent.org/docs
- https://docs.github.com/en/rest/actions/workflow-runs
- https://docs.github.com/en/actions/reference/security/secure-use

**Licenciamento:** `actions/attest` (MIT), `sigstore/cosign` (Apache-2.0), `open-telemetry/semantic-conventions` (Apache-2.0), `open-policy-agent/opa` (Apache-2.0) conforme metadados consultados dos repositórios. `in-toto/in-toto` e `slsa-framework/slsa` devolvem `NOASSERTION` como metadado GitHub — verificar LICENSE e dependências específicas antes de copiar ou redistribuir. Não confundir especificações públicas com licença da implementação.

## 3. A arquitectura mínima que faz sentido testar em R2

```text
Agent A / Agent B (untrusted claims) -> RIGHTWARE authenticated REST/MCP
                                           |
             PostgreSQL authority + evidence reference + event log
                                           |
                         Verification worker (read-only)
                         |                     |
                   GitHub API          Signed attestation/digest
                         |                     |
                      exact check results / source receipts
                                           |
                 Verification (PASS / FAIL / INCONCLUSIVE)
                                           |
             Authorized independent human/policy reviewer
                                           |
                          ACCEPT -> Task DONE (R2)
```

O worker **não** recebe autorizações de aprovação de tarefa; apenas acrescenta resultados de verificação. Mesmo um `PASS` de um teste deve referir a **alegação exacta que foi verificada**. A aceitação final do resultado pertence a um actor/política de revisão distinto do executor.

**Modelo de confiança em 5 passos**:
1. `CLAIMED`: agente apresentou uma afirmação ou URL — **não verificada**.
2. `SOURCE_RESOLVED`: servidor independente obteve o registo externo num endpoint allowlisted (e.g. API GitHub), não confiou no texto/URL fornecido como prova.
3. `CHECKED_PASS | CHECKED_FAIL | INCONCLUSIVE`: verificador atesta o resultado **específico** (ex.: workflow concluiu `success` para exact SHA e workflow esperado).
4. `REVIEW_ACCEPTED | REVIEW_REJECTED`: actor autorizado confronta os critérios de aceitação com evidência; `PASS` isolado não significa aceitação.
5. `SUPERSEDED/REVOKED`: correção versionada, revogação de autorização ou evidência invalidada não pode ser escondida por memória derivada.

Não guardar segredo de token, prompt privado ou logs integrais como ``evidence``. O registo imutável deve usar metadados mínimos, hashes, links vinculados a IDs e políticas de retenção/eliminação coerentes. Um hash não significa que o conteúdo é verdadeiro; um PDF assinado também pode conter dados falsos.

## 4. Exemplo de verificação de CI (código ainda NÃO construído)

Um cliente afirma: 'CI PASS, tarefa terminada' e fornece URL. O verificador deve:

1. Obter o recurso por **GitHub REST API** com a credencial própria de leitura: `GET /repos/{owner}/{repo}/actions/runs/{run_id}`; NÃO efectuar `fetch` arbitrário do URL controlado pelo agente (evitar SSRF), redireccionamentos inesperados ou comandos indicados pelo texto do agente.
2. Conferir **ID estável de repository** esperado, `head_sha` completo, `workflow_id`/ficheiro esperado, `event`, `run_attempt`, `status=completed` e `conclusion=success`. O `head_sha` e o workflow devem referir-se à tarefa/critério exactos; CI de outro commit é FAIL.
3. Verificar que o workflow e o ambiente de execução integram a lista de fornecedores confiáveis; não aceitar `pull_request_target`/`workflow_run` com checkout inseguro de código não confiável como equivalentes a builds de confiança.
4. Se relevante, verificar o **artefacto** por digest e attestation assinado com o signer/issuer/repositório esperado. Consultas GitHub REST a um run não são, por si, uma attestation criptográfica.
5. Gravar resultado como **CHECKED_PASS para ‘run específico X concluiu SUCCESS’**, incluindo `checked_at`, `provider`, `repository_id`, `sha`, `run_id`, `attempt`, `workflow_id`, `verifier_identity`, `policy_version` e digest. Não atribuir automaticamente `DONE`.
6. Se API indisponível, permissão revogada ou fonte inacessível -> `INCONCLUSIVE`/falha fechada, sem inventar aprovação. Corrigir por novo evento, sem reescrever a observação anterior.

Nota importante das fontes: A documentação de GitHub admite verificação offline de attestations, mas alerta que apenas o nome do repo pode ser insuficiente depois de renomeações: comparar também **repository ID**. O `in-toto` descreve política monotónica: ausência de atestado requerido deve permanecer DENY, não virar ALLOW por falta de evidência.

## 5. O que é potencialmente proprietário (HIPÓTESE, NÃO comprovado)

O possível diferencial RIGHTWARE não é o formato de proveniência, nem a assinatura, nem o checkpoint. É um **motor de política de continuidade com provas vinculadas a tarefas de diferentes aplicações** que consiga:

- Reconstruir o estado autorizado no tempo sem depender da memória gerada por LLM;
- Rejeitar resultados não demonstrados, mas preservar claims e passos intermédios para revisão;
- Adaptar verificadores externos por domínio (GitHub, sistemas empresariais, plataformas municipais, fontes de automação);
- Distinguir claramente **‘fonte foi observada’, ‘resultado de teste foi válido’, ‘critério de negócio foi aceite’**;
- Aplicar o mesmo modelo na passagem entre agentes heterogéneos, de forma substituível e sem cloud obrigatória.

Isto requer benchmark de fiabilidade, esforço de operação e entrevistas com clientes; ainda não demonstra vantagem competitiva face a soluções existentes.

## 6. Testes de contrato propostos (fixture anexo)

Ficheiro sintético `RIGHTWARE_SI_RD_03C_EVIDENCE_CASES.jsonl`. Os 16 casos cobrem autenticidade de run, SHA/identidade/fluxo, comportamento fail-closed, separação de deveres, efeitos duplicados e reautorização. São **oráculos propostos**, não resultados executados contra um verificador real.

**Critério P0 para um futuro R2**: zero auto-aprovações por claims, zero vazamentos inter-projectos, zero uso de run de outro SHA como evidência, zero promoção a DONE sem actor/regras de revisão, e zero replay de side-effects externos no conjunto sintético. Não generalizar zero falhas de 16 testes a segurança de produção.

## 7. Decisões recomendadas, não aprovadas

1. **REUSE** W3C PROV como vocabulário, in-toto Statement/Test-Result para evidência de software e GitHub APIs oficiais para verificação concreta; não inventar formato de assinatura nem stack de observabilidade.
2. **BUILD** pequeno `VerificationPolicy + EvidenceVerifier` acoplado a PostgreSQL autorizado, com adaptadores externos read-only e verificação mínima independente.
3. **POSTPONE** OPA/Rego, transparência própria, bases de grafos e infra de attestations empresariais até existir um caso de uso que as justifique.
4. **PRESERVE** separação WORK-03B R1B vs R2: o outro chat continua checkpoints/resume; este dossier de investigação não altera o código concorrente.
5. **NEXT**: incorporar as conclusões após o próximo HEAD e HANDOFF válidos, discutir contratos R2 e só então implementar/verificar em laboratório.
