# Branch Synthesis: Floating-gate and ferroelectric-gate 2D transistors for nonvolatile, high-endurance synaptic weights\n## Branch ID: 1c350f6c99ed3c84\n## Depth: 3\n\n**A. Consolidated Insights (≈6 bullets)**  

- **Hybrid ferroelectric‑floating‑gate stacks (α‑In₂Se₃ / h‑BN / graphene)** can combine coarse ferroelectric switching (2–4 bits, ≥10⁹ cycles) with fine charge‑trap tuning (up to 8 bits, ≈10⁶ cycles) to realise **effective 10–12‑bit non‑volatile weights** while keeping the write voltage ≤ 2 V.  
- **High C_DE/C_FE ratios (≥ 15)** in 2‑D FeFETs (Hf₀.₅Zr₀.₅O₂, AlScN, HZO) suppress dielectric‑field‑induced charge trapping, delivering **>10⁹ P/E cycles**, **>10 years retention**, and **sub‑60 mV dec⁻¹ sub‑threshold swing**.  
- **Ultra‑thin 2‑D dielectrics (EOT < 0.15 nm, leakage < 2 × 10⁻⁵ A cm⁻²)** obtained by oxygen‑plasma treatment enable **≤1 V programming** and **femto‑joule‑level write energy (≈18 fJ per pulse)**, meeting the power budget of on‑chip learning.  
- **Radiation‑hardness** is achieved intrinsically by the ferroelectric material (HZO tolerates ≥ 300 krad(Si) with < 50 mV V_TH shift) and by the high C_DE/C_FE design that limits ionising‑radiation‑induced trap formation.  
- **System‑level demonstrations** (MNIST 93.9 % accuracy, 97.7 % MNIST with FG array, 90 %+ CIFAR‑10 on 4 k‑cell FeFET cross‑bars) confirm that multi‑level weight storage translates into practical inference performance.  
- **Scalable 3‑D NAND‑style ferroelectric cells** and **vertical barristor architectures** can increase synapse density > 10× over planar designs while preserving the >10⁹‑cycle endurance and >10‑year retention required for long‑lived neuromorphic processors.  

---

**B. Divergent Claims (statement ↔ counter‑statement)**  

- **Statement:** “Floating‑gate devices achieve 8‑bit (256‑level) resolution with ≈ 10⁶ cycle endurance.”  
  **Counter‑statement:** “Ferroelectric‑gate FeFETs provide >10⁹ cycles but are limited to ≤4 bits; thus the high‑precision claim is not universally true.”  

- **Statement:** “High C_DE/C_FE (≈ 15) eliminates depolarisation loss, guaranteeing >10⁹‑cycle endurance.”  
  **Counter‑statement:** “Increasing the blocking‑oxide thickness to boost C_DE/C_FE can reduce the memory window and accelerate retention loss, indicating a trade‑off rather than a universal solution.”  

- **Statement:** “Radiation‑hardness of HZO‑based FeFETs is demonstrated up to 300 krad(Si) with negligible V_TH shift.”  
  **Counter‑statement:** “Dose‑rate effects, displacement‑damage, and long‑term annealing after irradiation have not been quantified, leaving the radiation claim incomplete.”  

- **Statement:** “Recessed‑channel FeFETs achieve a 5.5 V memory window in Si‑based platforms, the highest reported for 2‑D ferroelectrics.”  
  **Counter‑statement:** “Other reports (α‑In₂Se₃ / h‑BN / graphene) show memory windows up to ≈ 27.8 V, suggesting that the ‘highest’ claim depends on device geometry and measurement conditions.”  

- **Statement:** “3‑D vertical ferroelectric cells can be fabricated with >10× density without sacrificing endurance.”  
  **Counter‑statement:** “Current experimental arrays are limited to 4 × 4 cells; large‑scale uniform multi‑bit operation has not yet been demonstrated, so the density claim remains speculative.”  

- **Statement:** “Optical programming of floating‑gate devices consumes only 12 pJ per spike, enabling ultra‑low‑power neuromorphic sensing.”  
  **Counter‑statement:** “Electrical write energy can be as low as 18 fJ per pulse; the optical route is orders of magnitude less efficient and lacks quantitative energy‑per‑bit comparison.”  

---

**C. Notable Gaps (≈3 bullets)**  

- **Quantitative C_DE/C_FE optimisation:** No systematic study reports the exact dielectric‑to‑ferroelectric capacitance ratio that simultaneously maximises endurance, memory window, and low‑voltage operation.  
- **Large‑scale multi‑bit array validation:** Demonstrations are confined to ≤4 × 4 cells; uniform 8‑bit (or higher) weight distribution across >10 × 10 cross‑bars has not been shown.  
- **Radiation‑dose‑rate and displacement‑damage data:** Only total ionising dose up to 300 krad(Si) is reported; effects of high‑dose‑rate environments and non‑ionising radiation on endurance and retention remain unexplored.  

---

**D. Confidence**  
**Medium** – the synthesis draws on multiple quantitative reports, but several critical parameters (e.g., exact C_DE/C_FE values, large‑scale array performance, comprehensive radiation testing) are still missing, limiting full certainty.  

---

**E. Notable Candidates (materials, probes, techniques)**  

α‑In₂Se₃, Hf₀.₅Zr₀.₅O₂ (HZO), AlScN, CuInP₂S₆, MoTe₂, P(VDF‑TrFE), graphene, h‑BN, 2‑D dielectrics (oxygen‑plasma‑treated), 3‑D NAND‑style ferroelectric pillars, vertical barristor structures, optical programming (400–800 nm pulses), TCAD Landau‑Khalatnikov modeling, Shockley‑Read‑Hall charge‑trap kinetics, photogating (bulk photovoltaic effect), dual‑gate asymmetric write/read architecture, recessed‑channel geometry, multi‑gate hetero‑synapse arrays, 2‑DSPC (solid‑phase crystallisation), ferroelectric tunnel junctions (FTJs).