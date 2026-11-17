# SI-MH-0061 — G04-A0: aprovação limitada + prova de autorização sintética

**2026-11-17 Africa/Maputo. BASE** develop@61a5d18a17c5fddb60373bf4e664cc89a1dc8ac4, SI-MH-0060. [Actions 43610801921](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/43610801921) SUCCESS, 216/216 testes, 8 migrações, G01 GitHub LIVE/restore e Mem0/Ollama PASS.

**Decisão:** [G04-A0 R1](G04_A0_OPERATOR_DECISION_R1.md) é aprovação limitada e documentada de D01–D05/D12 para um protótipo interno inteiramente sintético. D02 e D03 aprovam normas, NÃO escolhem fornecedores. D12 aprova requisito, NÃO alterou branch protection. D06–D11 pendentes.

**Código isolado:** backend/rightware_si/g04_a0_synthetic_policy.py é uma simulação in-memory de autorizações por resource/org/project e principal mapeado a issuer+subject, expirações, permissão/propósito e fail closed. O construtor exige LAB, flag RW_SI_ENABLE_G04_A0_SYNTHETIC_LAB=1 e DSN local rw_test, mas nunca conecta à BD. Todas as claims são NÃO VERIFICADAS e qualquer utilizador Python poderia fabricá-las. Este código não deve ser usado em endpoints nem alegado como autorização real.

**Testes:** 21 novos testes puros em tests/test_g04_a0_synthetic_lab.py, incluindo organizações B/C fictícias, mudanças de tenant, grants e memberships revogados, issuer/aud, HUMAN/SERVICE, private class, flag e DB guard. Resultado esperado: 237 testes, **CI PENDENTE**. Os 28 oráculos G04-R0 ainda são NOT_IMPLEMENTED (DB_REAL/EDI etc), não contam como executados.

**Não alterado:** migrações 0001–0008, HTTP/MCP, G01, R1C, Mem0, OIDC de verdade, fontes privadas, ambientes externos, main, JARVIS/PULSE, vendor/mem0 e investigação SI-MH-0060. Não existe autorização de produto para clientes, revisão ou DONE.

**Próximo:** validar CI deste SHA e registar evidência num novo checkpoint. Depois escolher IdP e workload provider em projeto G04-A1, desenhar schema membership/ACL/RLS no G04-A2 apenas com aprovação técnica separada.
