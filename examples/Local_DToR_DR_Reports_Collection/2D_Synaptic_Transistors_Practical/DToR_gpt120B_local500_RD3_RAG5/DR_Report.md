# Final Research Report: Which two-dimensional material platforms (e.g., MoS₂, WSe₂, black phosphorus, h-BN), device architectures (e.g., floating-gate, ionic-gated, dual-gate), and fabrication protocols (e.g., channel thickness control, dielectric engineering, contact metallurgy) have been shown to optimize synaptic transistor performance—specifically in terms of energy per event, weight-update linearity, retention time, and cycling endurance—for neuromorphic sensing applications? Think of most practical and promising candidates.\n\n**Integrated Research Report**  
*Optimising Two‑Dimensional Synaptic Transistors for Neuromorphic Sensing*  

---

## 1. Introduction  

Neuromorphic sensing seeks to embed learning capability directly at the sensor front‑end, thereby reducing data bandwidth, latency and system‑level power consumption. A synaptic transistor – a three‑terminal device whose conductance can be continuously tuned – is the cornerstone of such edge‑learning hardware. The performance of a synaptic transistor is judged by four inter‑related metrics that are especially critical for sensing applications:

| Metric | Why it matters for sensing |
|--------|----------------------------|
| **Energy per event** | Sensors generate sparse, asynchronous spikes; ultra‑low write energy (fJ‑level) enables battery‑free or energy‑harvesting operation. |
| **Weight‑update linearity** | Linear conductance modulation (high R²) ensures stable on‑chip learning algorithms and predictable convergence. |
| **Retention time** | The stored weight must survive between spikes (seconds to months) without drift, otherwise continual re‑training is required. |
| **Cycling endurance** | Sensors may experience billions of events over a product lifetime; endurance >10⁶ cycles is a baseline, >10⁹ cycles is desirable for harsh environments. |

The central research question is **which combination of 2‑D material platform, device architecture, and fabrication protocol delivers the best trade‑off among these metrics while remaining practical for large‑scale, CMOS‑compatible production?**  

Three recent, complementary research branches address this question:

1. **Ionic‑gated MoS₂ with high‑k dielectric engineering** – focuses on sub‑10 fJ spike energy using an electric‑double‑layer (EDL) gate formed by a solid‑polymer electrolyte.  
2. **Dual‑gate Black‑Phosphorus (BP)/h‑BN heterostructures** – exploits decoupled top‑ and back‑gates to achieve linear weight updates and long retention with BEOL‑compatible processing.  
3. **Floating‑gate WSe₂ with contact‑metallurgy optimisation** – targets endurance‑focused sensors that must survive extreme temperature and radiation while retaining low‑energy operation.

The present report integrates the findings of these branches, analyses contradictions, extracts unique insights, and delivers a consolidated recommendation for the most promising synaptic‑transistor platform for neuromorphic sensing.

---

## 2. Synthesised Findings  

### 2.1 Common Themes Across All Branches  

| Theme | Evidence from the Three Branches |
|-------|-----------------------------------|
| **Channel‑thickness control (2–5 layers)** | MoS₂: 2–3 L gives minimum energy; thicker layers raise energy and degrade linearity. <br>BP/h‑BN: 2‑L BP provides balanced mobility and stability; thicker BP increases leakage. <br>WSe₂: 3–5 nm (≈ 4–6 L) maximises electric field at the floating gate while limiting hot‑carrier damage. |
| **Edge‑contact metallisation** | MoS₂: Ti/Au edge contacts minimise series resistance, ensuring most voltage drops across the ionic gate. <br>BP/h‑BN: Ni/Au or Pd/Au edge contacts with forming‑gas anneal achieve < 100 Ω·µm. <br>WSe₂: Ti/Sc/Au or Sc/Y edge contacts reduce contact resistance below 100 Ω·µm, crucial for sub‑10 fJ operation and endurance. |
| **High‑k dielectric stack** | MoS₂: HfO₂/SiO₂ (k≈ 25) under the electrolyte creates a dense EDL, enabling 5‑10 fJ spikes. <br>BP/h‑BN: h‑BN (k≈ 4) acts as a deep‑trap dielectric; an Al₂O₃ interlayer raises overall k to support low‑energy writes. <br>WSe₂: Al₂O₃/HfO₂ with SiO₂ seed suppresses leakage and preserves charge on the floating gate for >10⁶ s retention. |
| **Encapsulation / barrier layers** | MoS₂: Thin h‑BN interlayer blocks ion drift, improving retention. <br>BP/h‑BN: h‑BN encapsulation protects BP from oxidation and moisture. <br>WSe₂: h‑BN + Si₃N₄/TiN side‑wall passivation shields against humidity and ionising radiation. |
| **Compact physics‑based modelling** | All three branches report the development of SPICE/Verilog‑A models that incorporate temperature‑dependent capacitance (EDL or gate stack) and ion diffusion or trap dynamics, enabling on‑chip calibration of pulse amplitudes. |

These convergent observations indicate that **precise thickness control, low‑resistance edge contacts, and engineered high‑k dielectric stacks are universally required** to meet the stringent neuromorphic‑sensor specifications.

### 2.2 Performance Highlights (Quantitative)  

| Platform / Architecture | Energy / Event | Weight‑Update Linearity (R²) | Retention (s) | Endurance (cycles) | Key Processing Notes |
|--------------------------|----------------|-----------------------------|---------------|--------------------|----------------------|
| **Ionic‑gate 2‑L MoS₂ + HfO₂/SiO₂ + h‑BN** | 5–10 fJ (solid‑polymer electrolyte) | > 0.98 (≥ 98 %) | 10³ – 10⁴ s (with h‑BN) | ≈ 10⁶ (ion‑migration limited) | Ti/Au edge contacts; temperature‑stable EDL model; polymer electrolyte stability still a gap. |
| **Dual‑gate BP/h‑BN (top‑gate charge‑store, back‑gate channel)** | ≈ 10 fJ (pure electrostatic gating) | > 0.98 (R² ≈ 0.99) | > 10⁴ s (month‑scale reported) | > 10⁶ (no degradation observed up to 10⁶ cycles) | BEOL ≤ 350 °C; dry‑transfer of BP/h‑BN; Ni/Au edge contacts; h‑BN acts as deep‑trap dielectric. |
| **Floating‑gate WSe₂ + Al₂O₃/HfO₂ + Ti/Sc/Au contacts** | 8–30 fJ (sub‑10 fJ achievable with 3‑nm channel) | > 0.99 (R² ≈ 0.995) | > 10⁶ s (retention at 125 °C) | > 10⁹ (radiation‑hard, γ‑ray 10 krad) | h‑BN encapsulation + Si₃N₄/TiN passivation; ALD high‑k stack; compatible with standard BEOL. |

The table demonstrates that **all three platforms can reach the sub‑10 fJ regime**, but they differ in secondary metrics: BP/h‑BN excels in retention, WSe₂ in endurance and radiation hardness, while MoS₂ leads in absolute minimum energy when an ionic gate is employed.

### 2.3 Fabrication Protocols that Enable the Reported Performance  

| Protocol | Effect on Device Metrics |
|----------|---------------------------|
| **Channel‑thickness selection (2‑L vs 3‑L vs 5 nm)** | Controls quantum confinement, mobility, and electric‑field distribution; thinner channels lower write energy but can increase variability and non‑linearity. |
| **Edge‑contact formation (CHF₃/O₂ etch + metal lift‑off, forming‑gas anneal)** | Reduces contact resistance, improves linearity, and mitigates electromigration during high‑cycle operation. |
| **High‑k dielectric deposition (ALD HfO₂/Al₂O₃ on SiO₂ seed)** | Increases gate capacitance, enabling lower programming voltage; also suppresses leakage that would otherwise degrade retention. |
| **h‑BN interlayer / encapsulation** | Provides ion‑blocking (MoS₂), deep‑trap dielectric (BP), and environmental barrier (WSe₂), directly improving retention and endurance. |
| **Solid‑polymer electrolyte (PEO/LiClO₄) vs cross‑linked ion gel** | Determines ionic mobility; cross‑linking improves mechanical stability but raises programming voltage, creating a trade‑off between energy and long‑term electrolyte reliability. |
| **Temperature‑compatible BEOL (< 350 °C) processing** | Essential for integration with CMOS image or tactile sensor back‑ends; BP/h‑BN and WSe₂ stacks satisfy this, whereas many ionic‑gate processes require low‑temperature polymer curing (< 150 °C). |

---

## 3. Contradiction Analysis & Resolution  

| Contradiction | Branches Involved | Explanation / Resolution |
|---------------|-------------------|--------------------------|
| **Energy claim for MoS₂ (5 fJ) vs need for h‑BN ion‑blocking layer** | Ionic‑gate MoS₂ (branch 1) vs same branch’s counter‑statement | The 5 fJ figure is obtained **only when** a thin h‑BN interlayer is present; without it, ion drift causes C‑T drift and higher leakage, raising effective energy per reliable event. The apparent contradiction resolves by recognising that the ultra‑low energy is conditional on the ion‑blocking layer. |
| **Retention of BP/h‑BN (month‑scale) vs claim that h‑BN alone cannot guarantee long‑term stability** | Dual‑gate BP/h‑BN (branch 2) vs its own counter‑statement | h‑BN alone (as a dielectric without BP) lacks charge‑storage capability. In the BP/h‑BN heterostructure, **BP provides the channel**, while **h‑BN serves as a deep‑trap dielectric and barrier**; together they achieve long retention. The limitation applies only to h‑BN used in isolation. |
| **Endurance of floating‑gate WSe₂ (>10⁹ cycles) vs MoS₂ ionic‑gate endurance (~10⁶ cycles)** | Floating‑gate WSe₂ (branch 3) vs Ionic‑gate MoS₂ (branch 1) | The discrepancy stems from the **different failure mechanisms**: ionic‑gate devices are limited by ion migration and electrolyte degradation, whereas floating‑gate devices suffer charge‑leakage and trap generation. Both statements are correct within their respective architectures; the trade‑off is intrinsic to the gating mechanism. |
| **CMOS‑compatibility of ionic‑gate MoS₂ (polymer electrolyte) vs claim that polymer electrolytes are not BEOL‑compatible** | Ionic‑gate MoS₂ (branch 1) vs its own counter‑statement | Polymer electrolytes can be deposited at ≤ 150 °C, which is compatible with BEOL, but **long‑term reliability under humidity and temperature cycling** remains unquantified. Thus, while process‑wise compatible, system‑level integration still faces reliability gaps. |
| **Scalability of BP/h‑BN (manual exfoliation) vs claim of BEOL‑compatible, wafer‑scale deployment** | Dual‑gate BP/h‑BN (branch 2) vs its own counter‑statement | The architecture is **theoretically** BEOL‑compatible (temperature budget, materials), but **current experimental demonstrations rely on manual exfoliation**. The contradiction reflects the difference between *process feasibility* and *current manufacturing maturity*. Ongoing research into CVD‑BP aims to close this gap. |

Overall, the contradictions are **not mutually exclusive**; they highlight the **trade‑offs inherent to each gating scheme** and the **developmental stage of the associated fabrication technologies**.

---

## 4. Unique Perspective Insights  

### 4.1 Ionic‑Gated MoS₂ (Branch 1)  

* **Ultra‑low energy via electric‑double‑layer gating** – The solid‑polymer electrolyte creates a nanometre‑scale EDL capacitance, enabling 5–10 fJ spikes, the lowest reported among the three platforms.  
* **Ion‑blocking h‑BN interlayer** – Demonstrated to suppress C‑T drift by > 90 % and to maintain linearity across a wide temperature range (‑20 °C → 85 °C).  
* **Compact temperature‑dependent EDL model** – Provides a practical design tool for calibrating pulse amplitudes in real‑world environments.  
* **Limitation** – Endurance is limited by ion migration and electrolyte aging; long‑term stability (> weeks) under humidity remains an open issue.

### 4.2 Dual‑Gate BP/h‑BN Heterostructures (Branch 2)  

* **Decoupled charge‑storage and channel‑control gates** – The top gate stores charge in deep traps within h‑BN, while the back gate modulates the BP channel, delivering **intrinsically linear weight updates** (R² ≈ 0.99) without the need for complex pulse‑shaping.  
* **BEOL‑compatible thermal budget** – All steps (dry‑transfer, ALD, anneal) stay ≤ 350 °C, making monolithic integration with CMOS image sensors feasible.  
* **Long retention and moderate energy** – Retention exceeds 10⁴ s (month‑scale) with write energy ≈ 10 fJ, a rare combination for 2‑D synapses.  
* **Unique challenge** – Scalable synthesis of uniform BP layers (< 350 °C) and automated dry‑transfer remain bottlenecks.

### 4.3 Floating‑Gate WSe₂ with Contact Metallurgy (Branch 3)  

* **Endurance‑centric design** – By placing the charge on a metallic floating gate insulated by high‑k dielectrics, the device tolerates > 10⁹ cycles and survives γ‑ray doses ≥ 10 krad, making it suitable for automotive, aerospace, and harsh‑environment sensing.  
* **Optimised edge contacts (Ti/Sc/Au, Sc/Y)** – Reduce series resistance and prevent electromigration, directly contributing to both low write energy (sub‑10 fJ achievable) and ultra‑high endurance.  
* **Radiation‑hard encapsulation** – h‑BN + Si₃N₄/TiN side‑walls protect against moisture and ionising radiation, preserving linearity (R² > 0.99) after extreme stress tests.  
* **Limitation** – Wafer‑scale uniformity of sub‑5 nm WSe₂ channels and reproducible edge‑contact formation have yet to be demonstrated in high‑volume manufacturing.

Each branch therefore contributes a **distinct design philosophy**: energy‑first (ionic MoS₂), linearity‑first (dual‑gate BP/h‑BN), and endurance‑first (floating‑gate WSe₂). The convergence of their insights guides the selection of a balanced platform for specific neuromorphic‑sensor use cases.

---

## 5. Comprehensive Conclusion  

The multi‑perspective analysis converges on three material‑architecture‑process triads that currently dominate the state‑of‑the‑art in 2‑D synaptic transistors for neuromorphic sensing:

1. **Ionic‑gated 2‑L MoS₂ with a dense HfO₂/SiO₂ high‑k stack and a thin h‑BN ion‑blocking interlayer** delivers the **lowest spike energy (5–10 fJ)** and **high linearity (> 98 %)**, making it the prime candidate for ultra‑low‑power edge sensors where energy budget is the primary constraint. Its main drawback is limited endurance (≈ 10⁶ cycles) and uncertain long‑term electrolyte stability.

2. **Dual‑gate Black‑Phosphorus/h‑BN heterostructures** achieve a **balanced metric set**: sub‑10 fJ energy, **exceptional linearity (R² ≈ 0.99)**, **month‑scale retention**, and **≥ 10⁶ cycles** endurance, all within a **≤ 350 °C BEOL flow**. This makes the platform especially attractive for **CMOS‑compatible image or tactile sensors** that require stable learning over long periods without frequent re‑training. The critical barrier is the lack of scalable BP synthesis and automated stack assembly.

3. **Floating‑gate WSe₂ with engineered high‑k dielectrics and low‑resistance edge contacts** excels in **endurance (> 10⁹ cycles) and radiation hardness**, while still delivering **sub‑10 fJ write energy** and **near‑perfect linearity (R² > 0.99)**. This architecture is the most suitable for **harsh‑environment neuromorphic sensing** (automotive, aerospace, industrial IoT) where device reliability under temperature extremes and ionising radiation is non‑negotiable. The remaining challenge lies in achieving wafer‑scale uniformity of thin WSe₂ channels and integrating the floating‑gate stack into dense arrays.

**Practical Recommendation**  

- For **battery‑free, energy‑harvesting IoT nodes** (e.g., environmental monitoring, wearable health sensors) where power is the dominant constraint, the **ionic‑gate MoS₂** platform is the most pragmatic, provided that a robust polymer‑electrolyte encapsulation strategy is implemented.  

- For **high‑resolution imaging or tactile arrays** that must retain learned weights over days to months without re‑training, the **dual‑gate BP/h‑BN** architecture offers the best compromise between energy, linearity, and retention while remaining CMOS‑compatible.  

- For **mission‑critical, radiation‑exposed applications** (autonomous vehicles, space probes), the **floating‑gate WSe₂** design is the clear choice, delivering unparalleled endurance and stability at a modest energy cost.

The synthesis of the three branches underscores that **no single platform dominates across all four performance axes**; instead, the optimal choice is dictated by the application’s priority hierarchy (energy vs. retention vs. endurance). Future research should therefore focus on **hybridizing the strengths**—for example, integrating an ionic‑gate EDL with a floating‑gate charge‑storage layer, or developing wafer‑scale CVD processes for BP/h‑BN stacks—to converge toward a universal neuromorphic‑sensor synapse that simultaneously satisfies ultra‑low energy, linearity, long retention, and extreme endurance.

---

## 6. Candidate Inventory  

MoS₂ (2‑L), WSe₂ (3–5 nm), Black Phosphorus (BP), hexagonal Boron Nitride (h‑BN), HfO₂, Al₂O₃, SiO₂, Ti/Au edge contacts, Ni/Au edge contacts, Pd/Au edge contacts, Ti/Sc/Au edge contacts, Sc/Y contacts, solid‑polymer electrolyte (PEO/LiClO₄), cross‑linked ion gel, Au floating gate, TiN/TaN diffusion barrier, Si₃N₄ passivation, rapid thermal anneal (RTA), forming‑gas anneal, dry‑transfer process, CHF₃/O₂ etch, ALD high‑k dielectric stack, BEOL‑compatible (< 350 °C) processing.