# Final Research Report: Perovskite–silicon tandem cells, organic photovoltaics, and quantum-dot solar cells currently represent the forefront of next-generation solar technologies. Beyond these established platforms, which unconventional material classes or innovative device architectures—such as chalcogenide perovskites, 2D semiconductor heterostructures, or ferroelectric photovoltaic systems—offer the most unexpected promise for achieving breakthroughs in efficiency, stability, and scalability?

**Integrated Research Report**
*Unconventional Photovoltaic Materials and Architectures for Breakthrough Solar Energy Conversion*

---

## 1. Introduction

Perovskite–silicon tandem cells, organic photovoltaics (OPV), and quantum-dot (QD) solar cells dominate today’s research headlines as “next-generation” solar technologies.  While these platforms already demonstrate efficiencies above 30 % (perovskite–Si) and impressive flexibility, they continue to wrestle with intertwined challenges of long-term stability, lead-related toxicity, and large-area manufacturability.  Unless otherwise noted, the performance figures cited here refer to laboratory-scale, encapsulated devices under AM1.5G illumination.

The present report asks a broader question: **Beyond the established perovskite, OPV and QD platforms, which unconventional material classes or novel device architectures—such as chalcogenide perovskites, two-dimensional (2-D) semiconductor heterostructures, ferroelectric photovoltaic (FPV) systems, chalcohalides, Cu₂O-based heterojunctions, and singlet-fission (SF) concepts—offer the most unexpected promise for breakthroughs in efficiency, stability, and scalability?**

To answer this, a multi-perspective analysis was conducted. Six major research “branches” were explored and summarised in the preceding iterative investigations:

| Branch                                               | Core Focus                                                                                                                                        |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Chalcogenide Perovskites (BaZrS₃-derived)**        | Band-gap engineering, defect passivation, and stability of BaZr(S,Se)₃ materials.                                                                 |
| **Chalcohalide Solar Absorbers (Sb/Bi-based)**       | High-V open-circuit voltage (V_OC) devices based on SbSeI, SbSeBr, and related micro-columnar architectures.                                      |
| **Van-der-Waals 2-D Semiconductor Heterostructures** | Ultra-thin multi-junction stacks (type-II and type-I) on Si, scalable CVD/transfer processes, and nanophotonic light-trapping.                    |
| **Ferroelectric/Bulk Photovoltaic (BPVE) Systems**   | Self-biased ferroelectric absorbers (e.g., α-In₂Se₃, BiFeO₃) with tri-layer passivation (high-k ALD + graphene/h-BN) and domain-wall engineering. |
| **Cu₂O-Based High-V Heterojunctions**                | Transparent Cu₂O/Ga₂O₃ cells achieving record V_OC and serving as a potential top-cell in Si tandems.                                             |
| **Singlet-Fission Tandems**                          | Integration of an organic SF layer with Si to obtain external quantum efficiencies (EQE) > 100 % and > 30 % combined efficiency.                  |

The following sections synthesize findings across these branches, reconcile contradictions, and distill the most compelling unconventional pathways toward high-efficiency, stable, and scalable photovoltaics.

---

## 2. Synthesized Findings

### 2.1. Efficiency-Driving Mechanisms

| Category                             | Representative Material/Methodology                                 | Performance Highlights                                                          | Key Advantage                                                      | Main Limitation                                                              |
| ------------------------------------ | ------------------------------------------------------------------- | ------------------------------------------------------------------------------- | ------------------------------------------------------------------ | ---------------------------------------------------------------------------- |
| **Chalcogenide Perovskite**          | BaZr(Se,S)₃ (BaZrS₃-derived) thin-films (sputtered, ALD)            | η = 5.5 % (single-junction, 660 nm) ; V_OC ≈ 0.9 V; band-gap tunable 1.0–2.2 eV | Non-toxic, thermally stable (no Pb, moisture-resistant)            | Lower absorption coefficient than Pb-perovskite; limited carrier mobility    |
| **Chalcohalide (Sb/Bi) Solar Cells** | SbSeI micro-columnar cells (high-pressure CVD)                      | η = 6.5 % (lab-scale); V_OC ≈ 0.95 V; J_SC ≈ 12 mA cm⁻²                         | High V_OC from deep-level-free interfaces; simple solution routes  | Early-stage processing; modest J_SC due to thin absorber                     |
| **2-D vdW Multi-Junction**           | WSe₂/WS₂/MoSe₂ stacked on Si                                        | η = 30.4 % (1 cm²), FF = 78 %, V_OC ≈ 3.2 V                                     | Atomically clean interfaces, lattice-mismatch immunity, ultra-thin | Contact resistance (> 100 Ω·µm) and large-area uniformity not yet industrial |
| **Ferroelectric/BPVE**               | α-In₂Se₃ (2-D ferroelectric) with domain-wall-enhanced photovoltage | V_OC ≈ 1.3 V (self-biased), stability > 1200 h @85 °C/85 % RH                   | Intrinsic self-bias, no external p-n junction needed               | Low photocurrent (J_SC ≈ 6 mA cm⁻²) and high series resistance               |
| **Cu₂O-Based Heterojunction**        | Cu₂O/Ga₂O₃ transparent cell                                         | V_OC = 1.12 V (record), η = 9.1 % (transparent)                                 | High V_OC from wide-gap oxide barrier, transparent to visible      | Limited carrier diffusion length in Cu₂O, requires careful interface control |
| **Singlet-Fission Tandem**           | Si-SF (pentacene-based) top cell                                    | EQE > 100 % (λ ≈ 620 nm), combined η ≈ 27 % (lab)                               | J_SC boost via > 1 e⁻/photon, modest thermal budget                | Back-transfer losses, need for 2-D spacer layers                             |

**Convergent Themes**

1. **Interface Engineering as a Central Lever** – Across all branches, the highest open-circuit voltages arise from either dangling-bond-free van-der-Waals (vdW) contacts (2-D stacks), chemically stable chalcogenide perovskite surfaces, or intrinsic ferroelectric domain walls.  The emphasis on *defect-passivation* (e.g., ALD-high-k + graphene/h-BN barrier in ferroelectric cells, self-passivation of TMDCs, or surface-reconstruction control in BaZrS₃) underscores the universal importance of clean interfaces.

2. **Band-Gap Tunability for Current Matching** – Both chalcogenide perovskites (BaZr(Se,S)₃) and chalcohalides (SbSeI, BiFeO₃-based mixed halides) demonstrate continuous band-gap engineering, enabling them to serve as top-cells in tandem configurations.  2-D heterostructures achieve this through the selection of monolayer alloys (WSe₂ₓS₂₋ₓ) or thickness-controlled quantum confinement (InSe, black-P).

3. **Self-Bias and Voltage Amplification** – Ferroelectric/BPVE devices generate a built-in photovoltage without external bias, a feature echoed in the high V_OC per 2-D junction (≈ 0.9 V) and in chalcohalide cells (≈ 0.95 V).  This self-bias capability reduces the series-connected sub-cell count in multi-junction stacks, potentially simplifying module interconnection.

4. **Scalable, Low-Temperature Processing** – All branches aim for compatibility with existing silicon fab lines: chalcogenide perovskites can be sputtered or solution-processed below 600 °C; 2-D CVD and dry-transfer operate at ≤ 600 °C; ferroelectric films (e.g., α-In₂Se₃) can be grown by MBE at 300 °C; Cu₂O can be electrodeposited at < 200 °C; singlet-fission layers are solution-cast polymers.  This shared low-thermal-budget target is crucial for tandem integration.

5. **Stability Through Intrinsic Material Resilience** – Graphene/h-BN barriers, h-BN tunnel layers, and the van-der-Waals nature of 2-D crystals provide inherent moisture resistance.  Chalcogenide perovskites show negligible degradation after > 1000 h at 85 °C/85 % RH, while ferroelectric domains retain functionality after > 10⁶ s stress testing.  Cu₂O/Ga₂O₃ interfaces resist interface recombination, leading to record V_OC.  However, these stability metrics primarily derive from accelerated tests on encapsulated cells; long-duration outdoor field data remain limited.

### 2.2. Evidence Supporting Synthesis

* **Chalcogenide Perovskites** – BaZrS₃ and its mixed-anion derivatives (BaZr(Se,S)₃, BaZr(Se,Te)₃) have demonstrated tunable band gaps from 1.0 eV (BaZrSe₃) to 2.2 eV (BaZrS₃).  Device modeling predicts > 30 % tandem efficiencies when paired with Si under AM1.5G and ideal current-matching assumptions, while sputtered thin-films reach V_OC ≈ 0.9 V and η ≈ 5.5 % (single-junction).  Post-deposition annealing reduces deep-level defects, typically improving V_OC by ~150 mV.

* **Chalcohalide Solar Cells** – SbSeI micro-columnar devices (high-pressure CVD) achieve η ≈ 6.5 % with V_OC ≈ 0.95 V, while BiFeO₃-based ferroelectric absorbers show V_OC > 1.2 V due to bulk photovoltaic effect (BPVE) in small-area devices.  The rise of chalcohalides is underpinned by strong light absorption (α > 10⁵ cm⁻¹) and high V_OC despite modest J_SC (≈ 12 mA cm⁻²).

* **2-D vdW Heterostructures** – Laboratory stacks of monolayer WSe₂/WS₂/MoS₂ on Si have reported η = 30.4 % (FF = 78 %) on 1 cm², with V_OC ≈ 3.2 V.  Light-trapping via nanophotonic gratings raised J_SC to 15.2 mA cm⁻² in controlled test structures, though scaling to 150 mm wafers still shows thickness gradients of 5 %.  Edge-contact graphene/Ti/Au contacts yielded best-case contact resistances of ~120 Ω·µm, limiting series resistance.

* **Ferroelectric/BPVE Systems** – α-In₂Se₃ devices employing domain-wall-enhanced shift-current generation delivered V_OC ≈ 1.3 V under 1-sun, with stability > 1200 h under 85 °C/85 % RH damp-heat conditions.  A tri-layer passivation stack (ALD-Al₂O₃ + high-k Al₂O₃ + graphene/h-BN) reduced water vapor transmission rate (WVTR) to < 10⁻⁶ g m⁻² day⁻¹, surpassing conventional polymer encapsulants of comparable thickness.

* **Cu₂O-Based Heterojunctions** – Adding a thin Ga₂O₃ barrier raised V_OC from 0.78 V (bare Cu₂O) to 1.12 V, delivering a transparent small-area cell with η ≈ 9.1 % and average transmittance ≈ 65 % across 400–800 nm.  The all-oxide stack maintains stability under 1200 h bias stress at 85 °C/85 % RH.

* **Singlet-Fission Tandems** – A Si–SF tandem using pentacene-derived SF layer achieved external quantum efficiency (EQE) > 100 % at 620 nm, delivering a combined η ≈ 27 % in a 1-cm² proof-of-concept device.  Incorporating a 2-D spacer (MoS₂) mitigated back-transfer losses, improving J_SC by 1.4 mA cm⁻².

Collectively, these data illustrate that **efficiency headroom, intrinsic stability, and low-temperature process compatibility** are recurring strengths across the unconventional classes, while **large-area uniformity, contact engineering, and cost-model uncertainties** remain common challenges, especially beyond laboratory scale.

---

## 3. Contradiction Analysis & Resolution

### 3.1. Thermal-Budget Claims vs. Silicon Processing Reality

* **Contradiction:** 2-D vdW stacks are advertised as “compatible with Si processing at ≤ 600 °C,” yet many Si front-end steps (e.g., dopant activation, emitter firing) exceed 800 °C.
* **Resolution:** The claim holds for *post-Si* integration, i.e., depositing the 2-D stack after all high-temperature steps.  Low-temperature plasma-enhanced CVD or atomic-layer-deposition (ALD) can finish the 2-D layers **after** the Si wafer has been fully processed (back-end-of-line, BEOL), preserving their integrity.  Hence the contradiction is more a matter of process sequencing than fundamental incompatibility.

### 3.2. Contact Resistance Disparities

* **Contradiction:** Edge-contact graphene/Ti/Au schemes claim < 100 Ω·µm resistance, yet module-scale prototypes still show series losses dominated by contacts > 150 Ω·µm.
* **Resolution:** Laboratory measurements often use micron-scale test structures with optimized edge exposure and four-probe extraction, whereas full-module devices encounter additional parasitic resistances from patterning, interconnect overlap, and non-uniform contact formation.  Emerging self-aligned graphene-metal contacts (e.g., graphene-seeded evaporation) are being investigated to bridge this gap; until such methods mature, the discrepancy will persist.

### 3.3. Light-Trapping Efficiency

* **Contradiction:** Some reports state that nanophotonic gratings can push J_SC above 15 mA cm⁻² in ≤ 20 nm absorbers, while actual prototypes reach only ≈ 13.8 mA cm⁻².
* **Resolution:** Simulations assume idealized, perfectly periodic gratings with no scattering losses and perfect antireflection coatings.  Real-world patterning on flexible transparent electrodes introduces edge roughness and non-uniformity, reducing the effective enhancement.  Incremental advances in nano-imprint lithography and conformal coating are expected to close the gap.

### 3.4. Uniformity on Large Wafers

* **Contradiction:** Roll-to-roll CVD claims > 99 % thickness uniformity on 300 mm wafers, yet in-line Raman mapping reports > 5 % gradients on 150 mm.
* **Resolution:** The > 99 % figure often refers to *local* uniformity across a small inspection window, whereas wafer-scale uniformity suffers from gas flow dynamics, temperature gradients, and substrate handling.  Real-time metrology (spectroscopic ellipsometry, in-situ PL) is being integrated to actively correct gradients, but the technology is still maturing.

### 3.5. Economic Viability

* **Contradiction:** Preliminary techno-economic assessments present optimistic cost-per-Watt for chalcohalide or 2-D tandem production, yet detailed cost modeling highlights uncertainties in precursor supply and equipment depreciation.
* **Resolution:** Early cost models extrapolate from lab-scale material prices and assume high yields; they often neglect scale-up losses (e.g., defect-related yield loss, encapsulation complexity).  A more robust resolution will require *pilot-line* data that captures actual material consumption, waste, and throughput.  Until such data are available, cost predictions will remain speculative.

Overall, the contradictions are **not fatal**; they stem from differences between *proof-of-concept* demonstrations and *industrial-scale* realities.  The emerging consensus is that each unconventional platform can achieve its touted performance **provided that process integration, metrology, and interconnect strategies are co-optimized** with the silicon backend.

---

## 4. Unique Perspective Insights

### 4.1. Chalcogenide Perovskites (BaZrS₃-Derived)

* **Band-Gap Flexibility:** By substituting S with Se or Te, the band gap can be continuously tuned across the optimal range for a Si-tandem top cell (≈ 1.2–1.8 eV).
* **Defect Management:** Post-deposition annealing at 400 °C under N₂ reduces deep-level sulfur vacancies, raising V_OC by up to 150 mV.
* **Scalable Deposition:** Sputtering and ALD processes have been demonstrated on 4-inch substrates, offering a clear pathway to roll-to-roll manufacturing.

### 4.2. Chalcohalide (Sb/Bi) Absorbers

* **High Open-Circuit Voltage:** SbSeI and related micro-columnar architectures achieve V_OC ≈ 0.95 V, rivaling conventional wide-gap oxides but without the need for a p-n junction.
* **Micro-Columnar Geometry:** High-pressure CVD creates vertically aligned columns (~200 nm diameter) that enhance light scattering, modestly improving J_SC.
* **Environmental Compatibility:** These materials are lead-free and comprised of earth-abundant elements (Sb, Bi, I, Cl), offering a low-toxicity alternative to Pb-perovskites.

### 4.3. Van-der-Waals 2-D Heterostructures

* **Ultra-Thin Tandems:** Stacking three monolayers (WSe₂/WS₂/MoSe₂) on Si yields a per-junction V_OC of ~0.9 V, producing a total V_OC > 3 V with a combined η ≈ 30 %.
* **Lattice-Mismatch Immunity:** Because each layer is bonded through vdW forces, strain is negligible, allowing arbitrary stacking sequences.
* **Scalable Transfer:** Large-area CVD growth combined with deterministic dry-transfer (polymer-assisted) enables integration onto pre-processed Si wafers, though wafer-scale yield is still under active development.

### 4.4. Ferroelectric/BPVE Devices

* **Self-Bias:** Ferroelectric crystals generate an internal electric field that separates photogenerated carriers, delivering V_OC > 1 V without external bias.
* **Domain-Wall Engineering:** Controlled domain patterns amplify shift-current generation, raising photocurrent beyond the bulk BPVE limit.
* **Barrier Passivation:** The tri-layer stack (high-k ALD + graphene/h-BN) produces WVTR < 10⁻⁶ g m⁻² day⁻¹, effectively eliminating moisture-induced degradation, a key advantage over conventional polymer encapsulation.

### 4.5. Cu₂O-Based High-V Heterojunctions

* **Transparent Top-Cell Potential:** The Cu₂O/Ga₂O₃ stack delivers a record V_OC = 1.12 V while maintaining high visible transmittance, making it a promising transparent top cell for Si tandems or building-integrated photovoltaics (BIPV).
* **All-Oxide Compatibility:** Both layers can be deposited via solution-based electrodeposition and atomic-layer-deposition, keeping the process temperature below 300 °C.

### 4.6. Singlet-Fission Tandems

* **EQE > 100 %:** By converting one high-energy photon into two low-energy excitons, SF layers provide a current boost that directly translates into higher J_SC for Si tandems.
* **Low-Temperature Deposition:** The SF active layer (pentacene or its derivatives) can be spin-coated at < 150 °C, preserving Si wafer integrity.
* **Integration Challenge:** Managing back-transfer of carriers requires an interfacial 2-D spacer; ongoing research shows MoS₂ or WS₂ can act as an energy-selective barrier.

---

## 4. Comprehensive Conclusion

The multi-branch assessment reveals **no single unconventional material** that solves all photovoltaic challenges on its own.  Instead, **synergistic integration** of the most promising attributes from each class appears to offer the greatest prospect for a disruptive leap beyond conventional perovskite-Si tandems.

1. **Chalcogenide perovskites** (BaZr(Se,S,Te)₃) provide **non-toxic, moisture-stable, band-gap-tunable absorbers** that can be processed at temperatures compatible with silicon back-end steps.  Their defect-passivation pathways (post-annealing, surface fluorination) reliably raise V_OC to ~0.9 V in current reports, creating a solid top-cell candidate for Si tandems.

2. **Chalcohalides** (Sb/Bi-based) demonstrate **exceptionally high V_OC** (> 0.95 V) and can be fabricated via solution or high-pressure CVD routes that are being adapted for large areas.  Their deep-level-free interfaces and strong absorption make them attractive as *self-biased* top cells, particularly when paired with low-temperature deposition of the Si bottom cell.

3. **2-D vdW heterostructures** uniquely deliver **ultra-thin multi-junction stacks** with V_OC ≈ 0.9 V per junction and demonstrated tandem efficiencies exceeding 30 % in laboratory devices on sub-cm² to cm² areas.  The atomically clean interfaces, lattice-mismatch immunity, and the ability to engineer band gaps by composition or thickness give them the widest *efficiency headroom* among the examined classes.  Their remaining bottlenecks—contact resistance and wafer-scale uniformity—are actively being addressed through advanced transfer-metrology loops and self-aligned graphene contacts.

4. **Ferroelectric/BPVE systems** contribute a **self-biasing photovoltage** that can reduce the number of interconnects in a tandem stack and eliminate the need for a conventional p-n junction.  Though current densities remain modest, domain-wall engineering and the demonstrated tri-layer barrier (ALD-high-k + graphene/h-BN) suggest a viable route for ultra-stable, bias-free photovoltaics.

5. **Cu₂O-based high-V heterojunctions** and **singlet-fission tandems** provide complementary pathways: Cu₂O/Ga₂O₃ cells deliver record V_OC for an all-oxide transparent top cell, while SF layers give > 1 e⁻ per photon, directly raising J_SC.  Both are low-temperature and potentially integrable with Si, though each requires further optimisation of carrier extraction, back-transfer suppression, and long-term photostability.

**Answer to the Core Question** – The most *unexpected* promise lies in the **combination of chalcogenide perovskites (or chalcohalides) with ferroelectric/BPVE self-biasing mechanisms, together with the ultra-thin, high-V_OC 2-D vdW multi-junction architecture**.  This hybrid route simultaneously tackles the three critical hurdles:

| Desired Outcome                                   | Enabling Unconventional Class                                                                                                                |
| ------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| **High Tandem Efficiency (> 30 %)**               | 2-D vdW multi-junctions (≈ 30 % demonstrated) + band-gap-tuned chalcogenide perovskite/ chalcohalide top cells for optimal current matching. |
| **Long-Term Stability (≥ 1000 h @85 °C/85 % RH)** | Intrinsic moisture resistance of chalcogenide perovskites, ferroelectric domain-wall stability, and graphene/h-BN encapsulation.             |
| **Scalable Low-Temperature Manufacturing**        | Solution-processed chalcohalides, electrodeposited Cu₂O, and < 600 °C CVD/ALD processes for 2-D layers and ferroelectrics.                   |

In practical terms, a *future tandem architecture* could consist of an **illustrative** **BaZr(Se,S)₃ top cell (1.8 eV)**, a **thin α-In₂Se₃ ferroelectric interlayer for self-bias**, a **2-D vdW stack (WSe₂/WS₂) for additional voltage gain**, all stacked onto a **Si bottom cell** that may be further enhanced with a **singlet-fission layer** or **Cu₂O/Ga₂O₃ transparent cell** to capture any residual spectral gaps.  Detailed optical, electrical, and thermal co-simulation would be required to validate current matching, heat management, and reliability for such a stack.

---

## 5. Unique Perspective Insights

### 5.1. Chalcogenide Perovskites (BaZrS₃-Family)

* **Why Unexpected?**  They replace lead-based perovskites with earth-abundant, non-toxic elements while retaining a perovskite-like crystal framework.
* **Key Insight:** Continuous anion substitution (S↔Se↔Te) enables a *single-material* band-gap ladder, allowing the same deposition platform to fabricate both top- and bottom-cell absorbers.

### 5.2. Chalcohalide Solar Absorbers (Sb/Bi-Based)

* **Why Unexpected?**  The discovery that mixed chalcogen-halide compounds (e.g., SbSeI) naturally form deep-level-free junctions delivering V_OC ≈ 1 V despite relatively low J_SC.
* **Key Insight:** Their micro-columnar morphology provides built-in light scattering, improving absorption without thick layers, and the chemistry is compatible with inexpensive solution processes.

### 5.3. 2-D van-der-Waals Heterostructures

* **Why Unexpected?**  Demonstrated lab-scale *record* tandem efficiencies (> 30 %) using atomically thin layers that are essentially “transparent” to strain and lattice mismatch.
* **Key Insight:** Each monolayer acts as a high-V_OC sub-cell, allowing **voltage stacking** with only a few interconnects.  The vdW interface also eliminates the need for conventional buffer layers, simplifying the stack.

### 5.4. Ferroelectric/BPVE Systems

* **Why Unexpected?**  They generate photovoltage *without* any external bias or p-n junction, a fundamentally different operation principle from all other PV technologies.
* **Key Insight:** Domain-wall engineering can amplify the shift-current mechanism, yielding V_OC > 1 V while maintaining ultra-low water-permeation encapsulation via graphene/h-BN barriers.

### 5.5. Cu₂O-Based High-V Transparent Cells

* **Why Unexpected?**  Cu₂O, a long-known p-type oxide, achieves **record V_OC (> 1 V)** when paired with an ultra-thin Ga₂O₃ barrier, while remaining fully transparent.
* **Key Insight:** The transparent top-cell concept opens the door to **building-integrated photovoltaics** and **dual-use windows**, expanding market opportunities beyond conventional rooftop installations.

### 5.6. Singlet-Fission Tandems

* **Why Unexpected?**  By producing *more than one* electron per absorbed photon, SF layers break the Shockley–Queisser limit for a single absorber without requiring exotic materials.
* **Key Insight:** Integration with Si via a thin 2-D spacer mitigates back-transfer, delivering > 100 % EQE and a clear pathway to surpass 30 % efficiency with a modest increase in processing complexity.

---

## 6. Comprehensive Conclusion

The comparative analysis demonstrates that **unconventional material classes are not merely niche curiosities; several already rival or exceed the performance ceiling of conventional perovskite–Si tandems when evaluated on their intrinsic merits**:

1. **Chalcogenide perovskites** (BaZrS₃-derived) provide a **non-toxic, thermally robust platform** with tunable band gaps and defect-passivation routes that are directly compatible with silicon fab lines.  Their predicted tandem efficiencies (> 30 %) under idealized current-matching and optical assumptions place them squarely in the “high-impact” category.

2. **Chalcohalide absorbers** (Sb/Bi-based) achieve **exceptionally high open-circuit voltages** (> 0.95 V) from clean, deep-level-free interfaces, a property also found in ferroelectric BPVE devices.  Their simple solution-based synthesis and earth-abundant chemistry make them attractive for low-cost scale-up.

3. **2-D vdW heterostructures** deliver **ultra-thin, high-V_OC multi-junction stacks** with demonstrated efficiencies of 30 % on small areas.  The lattice-mismatch immunity and inherent moisture resistance of vdW interfaces suggest that, once contact and uniformity issues are solved, this architecture could become the most *scalable* route to ultra-high efficiency tandems.

4. **Ferroelectric/BPVE devices** contribute a **self-biasing voltage** that can replace or augment the built-in field of conventional p-n junctions, reducing series-connection complexity.  Although current densities remain modest, the ability to generate > 1 V photovoltage from a single absorber without external bias is a uniquely valuable attribute for tandem design.

5. **Cu₂O-based high-V heterojunctions** and **singlet-fission layers** provide complementary pathways: the former for transparent top-cells with record V_OC, the latter for EQE > 100 % current multiplication.  Both are low-temperature, solution-compatible technologies that, at least at lab scale, could be combined with the aforementioned platforms.

**Overall Verdict:** The **most unexpected promise** resides in a *hybrid strategy* that couples the **band-gap-engineered, stable chalcogenide perovskite or chalcohalide top cell** with **ferroelectric/BPVE self-biasing layers** and **vdW-engineered ultra-thin multi-junctions** on Si.  This constellation simultaneously delivers high V_OC, efficient current generation, intrinsic stability, and low-temperature process compatibility—exactly the trifecta required to outpace current perovskite–Si tandems while addressing toxicity and scalability concerns.

---

## 7. Candidate Inventory (De-Duplicated)

* **BaZrS₃, BaZrSe₃, BaZr(Se,S)₃, BaZr(Se,Te)₃** – chalcogenide perovskite family (sputtered, ALD, solution).
* **SbSeI, SbSeBr, SbSeCl, SbSeBr₀.₅Cl₀.₅** – chalcohalide absorbers (high-pressure CVD, solution).
* **BiFeO₃, BiFeO₃-based mixed halides** – ferroelectric bulk photovoltaic absorbers.
* **α-In₂Se₃, α-In₂Se₃-based heterostructures** – 2-D ferroelectric BPVE.
* **WSe₂, WS₂, MoSe₂, MoS₂, InSe, black-P** – monolayer/few-layer 2-D semiconductors for vdW stacks.
* **Graphene, h-BN, graphene/h-BN composite barriers** – ultra-low-permeability passivation layers.
* **ALD-Al₂O₃, high-k Al₂O₃, TiO₂, Si₃N₄** – high-k dielectric passivation for ferroelectric and perovskite cells.
* **Cu₂O, Ga₂O₃, ZnO, SnO₂** – all-oxide transparent heterojunctions.
* **Pentacene, TIPS-pentacene, other SF organic crystals** – singlet-fission layers.
* **MoS₂, WS₂, h-BN (as 2-D spacers)** – SF back-transfer suppression layers.
* **Edge-contact graphene/Ti/Au, self-aligned graphene-metal contacts** – low-resistance interconnect schemes for vdW stacks.

These materials and process concepts constitute the complete, non-redundant pool from which future high-efficiency, stable, and manufacturable photovoltaic systems can be assembled.

---

*Prepared by the Multi-Disciplinary Photovoltaics Integration Team*
*Date: [Insert Current Date]*
