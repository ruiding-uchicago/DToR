# Final ToT Synthesis Report

**Research Topic:** Which two-dimensional material platforms (e.g., MoS₂, WSe₂, black phosphorus, h-BN), device architectures (e.g., floating-gate, ionic-gated, dual-gate), and fabrication protocols (e.g., channel thickness control, dielectric engineering, contact metallurgy) have been shown to optimize synaptic transistor performance—specifically in terms of energy per event, weight-update linearity, retention time, and cycling endurance—for neuromorphic sensing applications? Think of most practical and promising candidates.

**Generated:** 2025-11-09 10:24:43

**Number of Branches:** 3

---

Title: Toward Practical 2D Synaptic Transistors for Neuromorphic Sensing: A Multi-Perspective Synthesis on Materials, Architectures, and Fabrication Protocols

1) Introduction

Driven by the demand for energy-efficient, high-endurance neuromorphic systems, this report synthesizes findings from three expert perspectives on two-dimensional (2D) material platforms, device architectures, and fabrication protocols that optimize synaptic transistor performance for neuromorphic sensing. The central question asks which 2D material platforms (examples: MoS2, WSe2, black phosphorus, h-BN), device architectures (examples: floating-gate, ionic-gated, dual-gate), and fabrication protocols (examples: channel thickness control, dielectric engineering, contact metallurgy) have demonstrated meaningful improvements in energy per event, weight-update linearity, retention time, and cycling endurance. The three branches considered are:

- Branch 1c350f6c99ed3c84: Floating-gate and ferroelectric-gate 2D transistors for nonvolatile, high-endurance synaptic weights, including ferroelectric-tunable stacks, dielectric-engineering strategies, and scalable novel architectures.
- Branch 459255dc45c8ebc3: 2D heterostructure engineering and fabrication protocol optimization for robust synaptic transistors, focusing on sub-60 mV/decade switching, ultra-low-energy operation, contact-resistance minimization, defect-trap management, low-temperature ferroelectric integration, and wafer-scale fabrication.
- Branch f5022d76baf990ca: Ionic-gated 2D synaptic transistors with dual-gate control, emphasizing energy-efficient gating, high-capacitance electrolytes, and scalable dual-gate approaches.

The scope of the report encompasses: (i) representative material platforms and their corresponding device architectures that have shown the most practical performance gains; (ii) fabrication and integration protocols that enable BEOL compatibility and scalable manufacture; and (iii) an integrated view of performance benchmarks relevant to neuromorphic sensing, including energy per event, weight-update linearity, retention time, and cycling endurance. Throughout, the synthesis highlights concrete numbers reported in the branches and identifies the most promising candidates for practical neuromorphic sensing tasks.

2) Synthesized Findings: Cross-Branch Synthesis and Convergent Themes

A. High-endurance, nonvolatile synaptic weights via ferroelectric and floating-gate mechanisms
- Hybrid ferroelectric–floating‑gate stacks enable coarse ferroelectric switching (2–4 bits) with long endurance, and fine charge-trap tuning (up to 8 bits) to realize effective 10–12‑bit nonvolatile weights, with write voltages ≤ 2 V. This combination aims to provide both durable long-term storage and refined analog weight updates.
- Dielectric engineering, notably achieving high C_DE/C_FE ratios (≥ 15 in 2D FeFETs such as Hf0.5Zr0.5O2 and AlScN/HZO), is a central lever for suppressing dielectric-field-induced charge trapping, yielding endurance > 10^9 cycles and retention on the order of > 10 years, while enabling subthreshold behavior (sub-60 mV/dec).
- Ultra-thin 2D dielectrics (EOT < 0.15 nm via oxygen plasma treatment) enable programming voltages ≤ 1 V and femtojoule-level write energies (~18 fJ per pulse), which is highly attractive for on-chip learning and low-power operation.
- Radiation hardness is enhanced in part by the ferroelectric materials and the high C_DE/C_FE design, which can mitigate trap formation under ionizing radiation; experimental demonstrations show tolerance up to ~300 krad(Si) with limited V_TH shift, though some radiation aspects remain to be fully quantified.
- System-level demonstrations (e.g., MNIST-like tasks with 93.9% baseline accuracy, 97.7% MNIST with ferroelectric FG arrays, and CIFAR-10 with four-kilopixel FeFET crossbars) indicate that multi-level weight storage translates to practical inference performance, supporting the viability of such stacks for neuromorphic sensing.
- Scalable 3D/nested architectures (3D NAND–style ferroelectric cells, vertical barristor concepts) have been proposed to boost synapse density by >10× relative to planar designs, while preserving endurance and retention targets.

Key quantitative indicators:
- Endurance: >10^9 program/erase cycles in high‑C_DE/C_FE designs; sustained operation over many cycles with minimal V_TH drift.
- Retention: >10 years in robust ferroelectric stacks.
- Memory window: wide windows reported (e.g., up to tens of volts in some 2D‑ferroelectric combinations), with some stacks achieving memory windows on the order of several volts depending on geometry and materials.
- Energy per write: femtojoule-scale (≈18 fJ) per pulse for ultrathin dielectrics; sub-volt programming (< 1–2 V).
- Inference performance: multi-bit or multi-level weight storage correlating with practical classification benchmarks.

B. 2D heterostructure engineering enabling low-power, highly scalable synaptic transistors
- Sub-60 mV/dec subthreshold swing and ultralow spike energy (≈9–12 fJ) have been demonstrated using combinations such as WS2/SnS2 tunneling with ferroelectric HZO or graphene floating gates, and α-In2Se3–based stacks. This establishes a practical energy-efficiency floor for 2D synaptic devices.
- Contact engineering at the 2D‑layer level—via Sb edge contacts, Ti/Al interlayers, 1T′‑MoTe2 control, and graphene edge contacts—consistently yields very low contact resistivities (often ≤ 0.5 Ω·mm), which is critical for high-speed, multi-gate operation and for preserving linearity in weight updates.
- Defect-gradient and trap-density control (through plasma processing, vacancy engineering, and oxidized 2D dielectrics) creates a unified model that links shallow traps to durable retention while keeping energy per spike in the fJ range, supporting both short-term plasticity and long-term memory windows (~10^6 or higher).
- Low-temperature ferroelectric integration (ALAs/HZO) achieves sizable remnant polarization (2Pr ∼ 27–38 µC cm^-2) with endurance > 10^8 cycles and BEOL compatibility (≤ 150 °C), facilitating monolithic integration with conventional CMOS backends.
- Wafer-scale heterostructure fabrication (vdW epitaxy of WS2/SnS2 and related bilayers) demonstrates uniformity metrics across 4-inch wafers, with on/off variations ≤ 5% and leakage around 10^-14 A, enabling high-density synaptic arrays (claimed > 10^6 synapses per wafer in some scoping studies).
- A hybrid tunnel–ferroelectric–floating‑gate stack (TF‑G) can deliver a combined advantage: sub-60 mV/dec swings, memory windows ≥ 10^6, and spike energies < 10 fJ, presenting a potentially single-device solution for both analog weight storage and ultra-low-power neuromorphic inference.

Key quantitative indicators:
- Subthreshold swing: ≈ 45 mV/dec (reported in TF‑G and related stacks); occasional reports of sub-60 mV/dec across various 2D stacks.
- Spike energy: ≈ 9–12 fJ per event in certain hybrid stacks; ≤ 18 fJ per pulse in ultra-thin dielectric scenarios.
- Endurance: >10^8 cycles for low‑temperature ferroelectric integration; >10^9 cycles in some high-endurance FeFETs when paired with robust dielectric engineering.
- Contact resistance: often ≤ 2 Ω·mm (targeted values often < 0.5 Ω·mm on wafer-scale substrates).
- Memory window: ≥ 10^6 for TF‑G stacks; wider windows reported for other ferroelectric stacks (up to tens of volts in certain configurations).

C. Ionic-gated 2D synaptic transistors: energy-efficient gating with dual-gate control
- Dual-gate decoupled operation (ionic write, electronic read) demonstrates sub-volt operation (≤ 0.9 V) and ultra-low switching energy (femto- to picojoules). This architecture supports very many discrete conductance states with linear, symmetric weight updates (ΔG/G ≈ 1% per pulse; R^2 > 0.99), favorable for stable, scalable synaptic learning.
- High-capacitance electrolytes (ion-gels ≈ 1–5 µF cm^-2; solid-state NASICON/MOF electrolytes with ionic conductivities) enable high carrier density at the channel, achieving on/off ratios > 10^4 and subthreshold swings below 80 mV/dec.
- Contact engineering at 2D interfaces (graphene/2D‑semiconductor interfaces; TaOx/Al2O3 traps) supports high transconductance and tight leakage control, essential for kilohertz to low-megahertz operation in large arrays.
- Demonstrations of wafer-scale flexible devices (4-inch) and even inkjet-printed architectures indicate reasonable scalability and mechanical robustness (e.g., σ ≈ 3% threshold voltage spread, > 1 million bending cycles with modest performance drift).
- Thermal and BEOL compatibility: solid-state electrolytes such as NASICON, LiPON, MOF materials survive high-temperature processing better than liquid ion-gels, enabling monolithic integration with CMOS, with post-BEOL deposition potential (< 200 °C for several processes).
- Multifunctionality through ion sieving concepts (GO/2D‑MOF membranes) expands sensing-weighting capabilities without sacrificing high on/off ratios.

Key quantitative indicators:
- Operating voltage: ≤ 0.9 V for dual-gate operation.
- Switching energy: femto- to picojoule per event; reports of ≤ 8 nJ in some dual-gate configurations, with other demonstrations in the fJ/pJ range depending on architecture.
- Storage states: ≥ 10^4 distinct conductance states with linear updates reported in some devices.
- Endurance: data beyond 10^6 cycles are not uniformly reported; long-term endurance remains an area for further validation.
- On/off ratio: > 10^4; subthreshold swing < 80 mV/dec in several demonstrations.

3) Contradiction Analysis & Resolution

A. Contradictions across perspectives
- Endurance versus memory window: Branch 1c350f6c99ed3c84 emphasizes extremely high endurance (>10^9 cycles) with sizable memory windows, while certain opposing claims (e.g., “highest” memory window statements) highlight very large voltage windows (e.g., ≈ 27.8 V) that may be achieved under specific geometries or measurement conditions. Resolution: Endurance and memory window are both geometry- and material-dependent; 2D ferroelectric stacks with optimized C_DE/C_FE ratios achieve long endurance with manageable window sizes on standard write voltages, whereas some ferroelectric/FG stacks in nonstandard geometries can exhibit larger window magnitudes but at the risk of stricter control requirements or leakage paths.
- Energy per event versus stability across large arrays: Some claims present ultra-low write energies (fJ) at the element level, yet large-scale (multi-bit, multi-gate) arrays face realistic energy accounting that includes peripheral circuits and leakage. Resolution: Device-level metrics (fJ per event) are favorable, but system-level power budgets must account for driver circuitry, readout, and interconnects; the most practical path is combining ultra-low-energy single-device switching with energy-efficient peripheral design to preserve overall neuromorphic efficiency.
- Ionic gating speed versus stability: Ion-gel gating offers very low voltage operation and large capacitance, but some claims contrast with long-term endurance and high-temperature stability. Resolution: Solid-state electrolytes (NASICON, LiPON, MOF-based electrolytes) improve BEOL compatibility and environmental stability, while ion gels may still be advantageous for rapid prototyping; a balanced approach uses solid electrolytes for production while retaining gel-based experiments for near-term exploration.
- Wafer-scale uniformity versus large-diameter scalability: Demonstrations on 4-inch wafers (and flexible formats) show promising uniformity and low leakage, but scaling to 8–12 inch substrates remains unproven in the supplied material. Resolution: The demonstrated uniformity on 4-inch wafers is a solid proof-of-concept; further process development is needed to translate these results to larger substrates with consistent defect densities.

B. Why these contradictions persist
- The field combines cutting-edge materials (2D layers, heterostructures, ferroelectrics) with novel device architectures, each with a unique design latitude and measurement paradigm. Endurance, retention, and linearity are highly sensitive to stacking order, interface quality, defect landscapes, dielectrics, and measurement conditions (voltage, pulse shape, temperature, radiation). Branch-specific claims are frequently conditioned on specific stacks, geometries, or measurement protocols, which may not be directly comparable. The absence of standardized test protocols across groups further complicates direct comparisons.

C. Takeaway on resolution
- The apparent contradictions arise from context (device geometry, stack composition, measurement condition, and target metrics). A unified framework would benefit from: (i) standardized, cross‑checked metrics for endurance, retention, energy per event, and linearity; (ii) clear reporting of memory window versus programming conditions; and (iii) cross-validation across wafer sizes with consistent process control. Overall, the convergent trend is that ferroelectric/FG stacks and 2D heterostructure stacks, when paired with low-temperature BEOL-compatible processes and low-leakage contacts, can deliver a compelling combination of very low energy, good linearity, and enduring retention for neuromorphic sensing.

4) Unique Perspective Insights: Distinct Contributions of Each Branch

A. Branch 1c350f6c99ed3c84 — Floating-gate and ferroelectric-gate 2D transistors
- Core contribution: Demonstrates a synergistic combination of coarse ferroelectric switching and fine charge-trap tuning to achieve extremely high effective weight resolution (10–12 bits) with robust endurance and retention, while maintaining low write voltages. The emphasis on dielectric-engineering (high C_DE/C_FE ratios), ultrathin dielectrics with very small EOT, and energy-efficient write operation (∼fJ) stands out as a practical path toward ultra-low-power on-chip learning.
- Notable claims: Endurance >10^9 cycles; retention >10 years; energy per write in the femtojoule range; radiation hardness; potential for 3D integration and high-density synapse arrays. The branch also highlights divergent claims (memory windows, or “highest” windows) and acknowledges gaps in radiation-dose-rate data and large-scale multi-bit array validation, making a balanced, honest assessment of current limits.
- Value: Provides a credible, near-term route to high-endurance, multi-level synapses with robust retention and low-energy writes, anchored by well-defined ferroelectric/dielectric stacks and BEOL-compatible processing.

B. Branch 459255dc45c8ebc3 — 2D heterostructure engineering and fabrication protocol optimization
- Core contribution: Focuses on device physics and fabrication protocols to realize sub-60 mV/dec subthreshold characteristics, ultra-low spike energies, and wafer-scale manufacturability. Emphasizes defect-trap control, low-temperature ferroelectric integration, and wafer-scale heterostructure growth that yields high uniformity and low leakage.
- Notable claims: Subthreshold swing close to 45 mV/dec; spike energy down to the femtojoule range; contact resistivities in the sub-ohm·mm range; endurance in high-performance ferroelectric stacks; wafer-scale uniformity with leakage around 10^-14 A; 4-inch wafers; dense, scalable arrays (≥10^6 synapses per wafer in envisioned scenarios).
- Value: Bridges materials science with scalable fabrication, delivering a blueprint for industrially relevant, uniform, low-energy synaptic devices across wafer-scale substrates. The emphasis on contact engineering, defect management, and low-temperature BEOL compatibility offers a pragmatic, integration-focused perspective.

C. Branch f5022d76baf990ca — Ionic-gated 2D synaptic transistors and dual-gate control
- Core contribution: Provides a detailed account of energy-efficient dual-gate ionic gating with decoupled write/read, emphasizing very low operating voltages, linear multi-state updates, and solid-state electrolyte options that improve integration prospects.
- Notable claims: Dual-gate operation with ≤0.9 V; extremely low switching energy (fJ–nJ range); high conductance state counts and linearity (ΔG/G ≈ 1% per pulse; R^2 > 0.99); durable mechanical and flexible performance in wafer-scale devices; BEOL-friendly solid-state electrolytes (NASICON, LiPON, MOFs) that survive higher temperature processing than gels.
- Value: Provides a practical, energy-efficient orthogonal gating strategy for neuromorphic sensing, with a clear path toward monolithic integration via solid-state electrolytes and CMOS-compatible processing, while acknowledging gaps in ultra-long endurance data and full system-level power accounting.

5) Comprehensive Conclusion

- Practical candidates and their complementary strengths:
  - Ferroelectric/FG 2D stacks (e.g., α-In2Se3/h-BN/graphene hybrids and HZO-based FeFETs) offer the strongest combination of ultra-long endurance (>10^9 cycles), robust retention (>10 years), and low-voltage operation with multi-bit weight storage. They are supported by substantial evidence for energy-efficient writes (tens of fJ to a few tens of fJ per event) and scalable integration, including potential vertical/form factor expansion to increase synapse density.
  - 2D heterostructure engineering—a focus on sub-60 mV/dec switching, ultra-low write energy, excellent contact resistance, low-trap densities, and wafer-scale manufacturing—provides a powerful, manufacturable path to scalable, dense synaptic networks with good linearity and high on/off ratios. The combination of materials (WS2, SnS2, MoS2, WSe2) with low-temperature ferroelectric integration and robust dielectrics makes this branch particularly relevant for BEOL-friendly neuromorphic systems.
  - Ionic-gated dual-gate architectures deliver outstanding energy efficiency and multi-state linearity, enabling very low-voltage operation and high conductance-state counts. Solid-state electrolyte options improve thermal stability and integration prospects, making these devices attractive for monolithic integration with CMOS, while acknowledging the need for more data on ultra-long endurance and total system power.
- The most practical and promising candidates for neuromorphic sensing applications are those that combine ultra-low write energy, robust linearity and multi-state capability, long retention, and endurance above 10^8–10^9 cycles, with BEOL-compatible processing and scalable fabrication. The three branches converge on a common strategic direction: leverage 2D ferroelectric/FG or 2D heterostructure stacks to realize multi-level weights with extremely low energy, ensure long-term retention and high cycling endurance, and enable scalable fabrication through wafer-scale, low-temperature processing and robust contact engineering. Ionic gating provides a complementary, energy-efficient gating approach that can be integrated with 2D materials to enhance linearity and scaling, particularly when solid-state electrolytes enable CMOS-compatible BEOL integration.
- In short, the most promising practical platforms for neuromorphic sensing lie at the intersection of:
  - 2D ferroelectric/FG transistors with high C_DE/C_FE ratios, ultralow-voltage operation, extreme endurance, and long retention (ferroelectric FeFETs and related TF‑G stacks).
  - 2D heterostructure stacks that deliver sub-60 mV/decade switching, ultralow spike energies, and wafer-scale fabrication with low-resistance contacts.
  - Ionic-gated dual-gate devices that offer ultra-low energy and very linear, multi-state updates, with solid-state electrolytes enabling BEOL-compatible integration.
- Collectively, these insights sketch a path toward dense, energy-efficient, robust neuromorphic sensing platforms that can be manufactured at scale and integrated with conventional CMOS backends.

6) Candidate Inventory (De-duplicated)

α-In2Se3, h-BN, graphene, MoS2, WSe2, WS2, SnS2, MoTe2, Bi2Se3, InSe, α‑In2Se3/h-BN/graphene stack, Hf0.5Zr0.5O2 (HZO), AlScN, ZrO2, P(VDF‑TrFE), GO, 2D MOF HKUST-1, NASICON electrolyte, LiPON, TaOx, Al2O3, Sb edge contacts, 1T′‑MoTe2, TF‑G stack, vdW epitaxy, WS2/SnS2 bilayers, WSe2/SnS2 bilayers, Ti/Al interlayers, graphene edge contacts, Sb edge contacts, FeFET, ferroelectric tunnel junctions (FTJs), TaO_x, GO/2D‑MOF membranes, electrochemical gating (ion gels, alginate ion gel), dual-gate ionic gating (NASICON/ion-gel/MOF electrolytes), VO/MoS2 related heterostructures, VP‑MoS2, VB‑MoS2, Al2O3/HfO2 stacks, P(VDF‑TrFE) melting/crystallization routes, VC/graphene contacts, 3D vertical ferroelectric cells, and vertical barristor architectures.

Table: Representative Material/Methodology with Performance Highlights (selected examples)

| Category | Representative Material/Methodology | Performance Highlights | Key Advantage | Main Limitation |
|---|---|---|---|---|
| Ferroelectric/FG 2D FeFET | HZO-based FeFET with high C_DE/C_FE | Endurance > 10^9 cycles; Retention > 10 years; energy per write ≈ fJ range; sub-V programming (≤2 V) | Very high endurance, robust retention, low-energy writes | Voltage window variability with dielectric stack; radiation-dose-rate effects not fully characterized |
| Ferroelectric/FG 2D stack | α-In2Se3/h-BN/graphene FG with ferroelectric gating | Effective 10–12 bits; write energy ≈ 18 fJ per pulse; V_write ≤ 2 V; memory window up to tens of volts in some configurations | High multi-level weight resolution + low energy | Large-scale multi-bit array validation limited; radiation data limited |
| 2D tunnel + ferroelectric + FG | WS2/SnS2 tunnel + HZO ferroelectric + graphene FG (TF-G) | SS ≈ 45 mV/dec; memory window ≥ 10^6; spike energy < 10 fJ | Very low energy per spike; strong linearity and large memory window | Endurance and long-term device variability across large arrays require more data |
| Wafer-scale 2D heterostructures | WS2/SnS2 bilayers via vdW epitaxy; 4" wafers | On/off variation ≤ 5%; leakage ≈ 10^-14 A; potential >10^6 synapses per wafer | High uniformity, high-density integration | Scaling to larger wafers (8–12") and long-term manufacturing yield data | 
| Ionic-gated dual-gate | Ion-gel/solid-state electrolytes with dual-gate control | ≤0.9 V operation; switching energy fJ–nJ; ΔG/G ≈ 1% per pulse; R^2 > 0.99 | Ultra-low-voltage, large dynamic range, linear updates | Endurance data beyond 10^6 cycles; full system-level power budgets |

Notes:
- Performance highlights summarize the most robust metrics reported across the branches. Where a parameter is explicitly stated, it is quoted; otherwise “n/a” is used.
- The table is not exhaustive; it focuses on representative, practically relevant examples that illustrate the convergent trends across the three branches.

In closing, the multi-perspective synthesis points to a pragmatic path to neuromorphic sensing with 2D materials: exploit ferroelectric/FG and 2D heterostructure stacks for ultra-low-energy, high-endurance synapses, and leverage ionic gating with dual-gate control to complement and extend energy efficiency and linearity, all within BEOL-compatible fabrication frameworks and scalable wafer-scale manufacturing. The most promising near-term candidates couple ultralow write energy and sub-volt operation with endurance above 10^8–10^9 cycles, retention on the order of years, and scalable, low-temperature processing to enable dense synaptic networks integrated with conventional CMOS.

End of report.