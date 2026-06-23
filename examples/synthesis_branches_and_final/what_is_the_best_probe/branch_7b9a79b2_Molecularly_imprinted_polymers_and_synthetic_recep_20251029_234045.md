# Branch Synthesis: Molecularly imprinted polymers and synthetic receptors for PFAS on FETs\n## Branch ID: 7b9a79b2b65bc200\n## Depth: 3\n\nA. Consolidated Insights
- Molecularly imprinted polymers (MIPs) and related synthetic receptors mounted on FETs are the most supported PFAS probes for water sensing in this perspective, with strong rationale for both broad screening and potential speciation via sensor arrays. Evidence points to broad PFAS affinity, near-gate binding advantages, and compatibility with gate-level transduction.
- Real-water performance targets cited across iterations include ng/L to sub-ng/L sensitivity and crucial benchmarks around PFAS6 (sum limit ≈ 20 ng/L) and LC-MS LOQs (~0.2 ng/L). These targets drive design choices such as thin, well-controlled MIP layers placed near the gate and high-surface-area FET channels to maximize signal amid Debye screening.
- Debye screening is consistently identified as the central challenge for electrochemical/readout PFAS-FETs in aqueous matrices. Proposed mitigations include near-surface binding, ultrathin MIP coatings, high-frequency transduction, surface passivation, and, in practice, sample conditioning to reduce ionic strength.
- Iterations converge on two practical modes: (i) a broad-screen PFAS-FET array where one gate uses a broad PFAS-imprinting strategy and other gates use targeted MIPs for PFOA/PFOS or additional PFAS; (ii) targeted imprinting (PFOS or GenX) to enable speciation with dedicated gates. This dual-pathway approach balances coverage and discrimination.
- GenX and PFOS/PFOA trajectories are complementary: PFOS-imprinted MIPs appear most mature for real-water PFOS signal, with sub-nanomolar/low-nanomolar demonstrations in non-FET contexts; GenX-imprinted MIPs show strong real-water performance on microelectrodes and offer a viable route to GenX PFETs, though direct real-water GenX PFET data are still lacking.
- Regeneration and durability remain underreported for PFAS-FET systems. While eight regeneration cycles are reported for some non-FET MIPs, device-level demonstrations of mild, on-device regeneration for MIP-FETs are absent, representing a critical path and risk factor for field deployment.
- Real-water validation, matrix effects, and cross-PFAS selectivity require standardized benchmarking. Cross-modal insights from ECL/optical and impedimetric MIPs provide design guidance, but PFET-specific quantitative metrics (LOD, LOQ, dynamic range, selectivity across PFAS families) on real water are still to be robustly established.

B. Divergent Claims (statement vs. counter-statement)
- Claim A: PFOS-imprinted MIP on PFETs is the best starting probe because sub-nanomolar LOD/LOQ have been demonstrated for PFOS-imprinted MIPs in real water, and gate-level transduction is readily achievable with near-gate binding.
  - Counter: There is no direct, fully published PFOS-imprinted PFET demonstration in real water with quantitative metrics; GenX-imprinted MIPs have shown sub-nanomolar performance on non-FET platforms and offer a strong route to PFET integration, so broad PFAS coverage may require multiple targeted MIPs or arrays rather than a single PFOS-imprint PFET.
- Claim B: Debye screening mitigation strategies (e.g., near-surface binding, ultrathin MIPs, high-frequency transduction) render MIP-FET PFAS sensing feasible down to ng/L or sub-ng/L in real water.
  - Counter: Debye screening remains a central, unresolved obstacle for fully quantitative PFAS-FET sensing in real water; concrete, device-level demonstrations combining ultrathin PFAS-MIPs with gate transduction and real-water LODs/LOQs are not yet published, so the claim is forward-looking rather than established.

C. Notable Gaps
- Direct PFOS- and GenX-targeted PFET demonstrations in real water with fully reported LOD/LOQ, dynamic range, and cross-PFAS selectivity.
- Device-level regeneration protocols for MIP-FETs (mild, on-device desorption) validated across 8+ cycles with quantified performance retention and baseline stability.
- Standardized, cross-lab benchmarking data for mult PFAS panels on PFETs, including matrix effects (different water types), isomer discrimination, and reproducibility across sensor devices.

D. Confidence
- Confidence: Medium
  - Rationale: There is a coherent, convergent rationale supporting MIPs (including PFOS- and GenX-targeted) as the best-projected PFAS probes for FETs, and substantial cross-modal evidence supports the underlying chemistry and transduction concepts. However, direct, fully validated PFOS/GenX PFET demonstrations in real water with multi-PFAS imprinting and documented 8+ regeneration cycles are still lacking, keeping the overall conclusion as promising but not yet fully proven.

E. Notable Candidates (distinct materials/probes/techniques surfaced in this branch)
- PFOS-imprinted MIP
- GenX-imprinted MIP
- Broad-spectrum PFAS-imprinted MIP
- Aptamer-informed MIP (apta-MIP)
- Extended-gate MOSFETs (EG-MOSFETs / extended-gate FET architectures)
- Graphene-based FETs
- CNT-based FETs (carbon nanotube)
- Silicon nanowire (SiNW) FETs
- Near-gate binding strategies
- High-frequency transduction approaches
- Surface passivation strategies
- Multisite PFAS sensor arrays / gate-by-gate multiplexing
- Real-water validation platforms (e.g., Amherst/Mass. water context)
- Cross-modal PFAS sensing references (ECL, optical fibers, impedimetric MIPs) for design guidance and calibration strategies

Confidence assessment: Medium