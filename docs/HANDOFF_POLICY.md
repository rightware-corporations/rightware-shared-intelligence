# RIGHTWARE — Handoff & Engineering Continuity Policy

**Status:** DECISÃO OFICIAL DO OPERADOR, 2026-11-12. Aplicável ao RIGHTWARE Shared Intelligence; norma recomendada para outros projetos somente após adoção explícita.

## Regra inegociável
**Nenhum output técnico fica somente no chat.** Toda entrega, implementação, investigação com conclusão acionável, correção, auditoria, falha, resultado de teste ou checkpoint é registrada no GitHub antes de ser dada como concluída.

Dois documentos com funções diferentes:
- docs/HANDOFF_MASTER.md é o **livro cumulativo append-only**. Adicionar entradas; nunca apagar/reordenar/reinterpretar entradas históricas. Corrigir com adenda posterior. Git preserva versão anterior; branch protection/backup ainda precisam de configurar.
- docs/HANDOFF.md é a **fotografia operacional atual**: HEAD de desenvolvimento, teste comprovado, bloqueios, riscos, próximo comando/ação, compatibilidade, o que não está implementado. Pode ser atualizado a cada checkpoint, mas o histórico não se perde porque está no MASTER e no Git.
- docs/handoffs/ contém dossiers de recuperação e checkpoints detalhados quando necessário, vinculando evidência, diffs e relatórios externos. Não guardar logs que contenham segredos.

## Reforço oficial — output por output (SI-MH-0081, 2026-11-24)

**DECISÃO OFICIAL DO OPERADOR:** cada output relevante de trabalho do SIC, inclusive análise sem código, deve ter um registo durável, detalhado e verificável no GitHub. Aplica-se a qualquer agente ou ferramenta que trabalhe no projecto. Não depende do fim da conversa, da missão inteira ou de solicitação adicional do operador.

- Unidade de registo: cada entrega, conclusão técnica, decisão, mudança de plano, experiência, resultado, tentativa falhada ou bloqueio significativo. Progresso parcial que permita retomar trabalho também é um checkpoint; não esperar pelo fecho de uma fase longa. Mensagens de cortesia e progresso sem conteúdo novo não exigem commit.
- Antes de apresentar um output como concluído, publicar a evidência sanitizada e os dois handoffs no mesmo commit em develop, verificar que o HEAD remoto contém a entrega e fornecer ao operador o SHA, referências, estado de validação e próxima acção. CI ainda em execução = PENDING, não PASS; registar o resultado observado por adenda quando disponível, sem criar uma cadeia infinita de commits que apenas atestam o CI da adenda anterior.
- Cada registo deve permitir a outro agente reconstruir o trabalho sem o chat: contexto de entrada, objectivo, estado anterior/HEAD, opções consideradas e razão técnica da escolha, decisões versus hipóteses, passos efectivamente executados, comandos reproduzíveis sanitizados, artefactos/diffs, ambiente e resultados PASS/FAIL/SKIP/NOT_RUN, erros e tentativas, alterações e não-alterações, riscos, dependências e próxima acção exacta. Incluir rollback quando aplicável.
- Para trabalho longo, criar checkpoints intermédios a cada marco relevante e antes de mudar de sessão, quando possível. Se ocorrer interrupção, recuperar pelo HEAD remoto e último checkpoint, identificar trabalho local não publicado e não presumir que foi concluído. Não apagar trabalho desconhecido nem fazer reset destrutivo.
- Se GitHub estiver inacessível, preservar um handoff sanitizado local quando possível, declarar REGISTO PENDENTE e não declarar entrega concluída; reconciliar e publicar antes de prosseguir com trabalho dependente.
- O GitHub público não é arquivo de conversas privadas integrais, segredos, dados pessoais, anotações privadas, gold reservado ou material confidencial. Registar decisões e evidência técnica necessária em resumo sanitizado; usar referências ou compromissos públicos apenas quando não exponham informação protegida. Não publicar conteúdo de CUSTODY_ONLY ou .runtime.
- Em cada recuperação, ler HANDOFF_POLICY, HANDOFF, última entrada MASTER, dossier SIC e verificar HEAD/CI reais. O histórico MASTER é append-only; não reescrever falhas nem decisões antigas. Preservar develop/main e a política de release existente.

## Fluxo de trabalho obrigatório para cada output técnico
1. ANTES: consultar develop remoto, HANDOFF.md, última entrada HANDOFF_MASTER.md, PRs e CI reais; não assumir estado do chat.
2. DECIDIR: registrar âmbito, hipótese, decisão aprovada ou recomendação; identificar o que NÃO será alterado.
3. EXECUTAR: construir em develop; testar ou marcar expressamente PENDENTE/BLOQUEADO. Sem marcar sucesso antes dos logs.
4. REGISTAR NO MESMO COMMIT: código/config/docs resultantes + atualizar docs/HANDOFF.md + acrescentar uma entrada nova ao docs/HANDOFF_MASTER.md. Se houver fase apenas analítica relevante, registar também o resultado, mesmo sem código.
5. VERIFICAR: comparar HEAD remoto, observar CI, confirmar arquivos e não remoção de histórico; se CI sair depois do commit, acrescentar um novo checkpoint/adenda e commitar.
6. ENTREGAR: informar commit/branch, documentação, mudanças, resultados reais, falhas, bloqueios e próximo passo. Não depender da conversa para continuar.

## Contrato mínimo para cada entrada
- Timestamp e identificador imutável SI-MH-XXXX.
- Classificação: OFFICIAL DECISION / ACTIVE IMPLEMENTATION / STRATEGIC PROPOSAL / HYPOTHESIS / EXPERIMENT / RECOMMENDATION / VERIFIED / FAILED / BLOCKED.
- Problema, objetivo, escopo, código/arquivos alterados, dados/migrations, CI/testes com SHA, evidência de execução, decisões, limitações, segurança, próximos passos e responsável quando conhecido.
- Referências diretas a commits/PRs/issues/runs (não copiar logs enormes). Distinguir claramente FAKE, unidade, real PostgreSQL, real Mem0/Ollama, E2E e produção.
- Registar explicitamente o que NÃO foi feito, para evitar falsas inferências.

## Política Git
- Apenas duas BRANCHES DE TRABALHO futuras: develop e main. Não criar feat/*, docs/* ou branches transitórias para novos trabalhos. Isso não significa apagar referências históricas antes de um inventário.
- develop = integração e construção; main = versão aprovada. MAIN NÃO está pronta para produção; contém apenas README inicial.
- Não fazer merge de develop para main sem autorização expressa, testes verdes e decisão de release.
- Não realizar force-push/rebase destrutivo nos ramos oficiais. Preservar hashes de PRs antigos como referências históricas antes de os encerrar; comparar árvore e confirmar CI primeiro.
- GitHub branch protection / regras de revisão e cópias de segurança externas ainda não configuradas. Política escrita não é equivalente a proteção técnica.

## Dados sensíveis e disponibilidade
- Repositório público: jamais escrever tokens, chaves, dados pessoais, conversas privadas completas, dumps de BD ou credenciais de CI.
- Manter apenas evidências necessárias, redigidas/sanitizadas, refs a código e resumos úteis. Os detalhes confidenciais, se aprovados futuramente, vão a armazenamento privado com autorização.
- Git não assegura sozinho disponibilidade caso se perca acesso à organização GitHub: recomendamos posteriormente backups encriptados e espelho privado dos docs/commits, com testes de restauração.
- Se o GitHub estiver indisponível e não for possível gravar o checkpoint, a entrega deve ser marcada REGISTO PENDENTE, não concluída.

## Gates
- Workflow em develop deve verificar alterações simultâneas aos dois handoffs.
- Compromisso adicional: validação automática da política não substitui revisão humana do conteúdo do handoff.
- Qualquer dispensa exige DECISÃO explícita com justificativa num novo checkpoint, nunca exclusão silenciosa.

