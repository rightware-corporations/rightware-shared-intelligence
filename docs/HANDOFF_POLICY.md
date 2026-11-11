# RIGHTWARE — Handoff & Engineering Continuity Policy

**Status:** DECISÃO OFICIAL DO OPERADOR, 2026-11-12. Aplicável ao RIGHTWARE Shared Intelligence; norma recomendada para outros projetos somente após adoção explícita.

## Regra inegociável
**Nenhum output técnico fica somente no chat.** Toda entrega, implementação, investigação com conclusão acionável, correção, auditoria, falha, resultado de teste ou checkpoint é registrada no GitHub antes de ser dada como concluída.

Dois documentos com funções diferentes:
- docs/HANDOFF_MASTER.md é o **livro cumulativo append-only**. Adicionar entradas; nunca apagar/reordenar/reinterpretar entradas históricas. Corrigir com adenda posterior. Git preserva versão anterior; branch protection/backup ainda precisam de configurar.
- docs/HANDOFF.md é a **fotografia operacional atual**: HEAD de desenvolvimento, teste comprovado, bloqueios, riscos, próximo comando/ação, compatibilidade, o que não está implementado. Pode ser atualizado a cada checkpoint, mas o histórico não se perde porque está no MASTER e no Git.
- docs/handoffs/ contém dossiers de recuperação e checkpoints detalhados quando necessário, vinculando evidência, diffs e relatórios externos. Não guardar logs que contenham segredos.

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

