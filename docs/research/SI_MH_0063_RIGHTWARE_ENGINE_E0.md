# SI-MH-0063 — RIGHTWARE proprietary Intelligence Engine: R&D mandate and E0

**Date:** 2026-11-18 Africa/Maputo. **Classification:** EXPLICIT STRATEGIC DIRECTION + EXPERIMENTAL RESEARCH CODE. **CI of this SHA PENDING.**

Verified baseline develop@25ed1695b5daafc14c182aad288304398fda81e5: [Actions 44114227352](https://github.com/rightware-corporations/rightware-shared-intelligence/actions/runs/44114227352) SUCCESS 237/237 tests, G01 LIVE GitHub native restore and Mem0/Ollama E2E, D01-D05/D12 restricted G04 lab approved. G04 A1 real OIDC and A2 RLS still unimplemented.

The operator explicitly requires a RIGHTWARE-designed intelligence engine and real data science, rather than relying only on reverse engineering and 3rd-party vendors. This commits an [R0 strategic thesis](RIGHTWARE_INTELLIGENCE_ENGINE_STRATEGY_R0.md) and [R0 falsifiable scientific protocol](RIGHTWARE_INTELLIGENCE_ENGINE_RESEARCH_PROTOCOL_R0.md) using ongoing sealed independent comparative research. No LLM foundation training or commercial product launch is implied.

New research-only `backend/rightware_si/experimental_engine_e0.py` provides reproducible BM25 baseline + trusted synthetic scope/temporal filtering + authority/conflict/abstention separation; generates evidence candidates, never truth or final answers. `tests/test_rightware_engine_e0.py`: 22 new pure offline tests including PT accents, temporal validity, scope leakage, unverified-only abstention and authoritative conflict even past top-k. Total 259 expected CI, NOT YET VERIFIED.

The **novel own trained model does not exist yet**: E0 uses publicly known BM25 and hand-coded reference safety rules. E1/E2 will use independently collected ground-truth and trainable ranking/calibration and measure improvement, with held-out splits, paired bootstrap/ablation, risk coverage, and frozen oracle non-leakage. SI-RD A0-GLOBAL-02 sealed 82-source/56-query benchmark cannot be trained/tuned against. No vendor selected, no benchmark results extrapolated, no Mem0/Hindsight vendor code changed.

No API/DB/migrations/G04 identity config/production/JARVIS/PULSE/main changes, no private data, no user identity or authorization decision, no reviewer/DONE. Existing 28 real G04 negative oracles NOT_IMPLEMENTED.

NEXT: inspect CI for 259/expected and no regressions. Keep G04-A1/A2 security architecture parallel; prepare separate training labels/feature schema and non-leaky dataset, then preregister E1.
