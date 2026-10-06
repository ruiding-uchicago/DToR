# Final ToT Synthesis Report

**Research Topic:** How can in situ liquid cell TEM be employed to directly visualize the real-time adsorption and structural changes of 2D MoS₂ nanosheets used in aqueous FET sensors during analyte binding? What fluid cell configurations and electron dose parameters are necessary to preserve native water–material interfaces while capturing high-resolution sensing events without beam-induced artifacts?

**Generated:** 2025-11-09 10:24:38

**Number of Branches:** 3

---

Title: Integrated Perspective on In Situ Liquid-Cell TEM Visualization of Real-Time Adsorption and Structural Dynamics of MoS2 Nanosheets in Aqueous FET Sensing

1) Introduction

Advances in in situ liquid-cell transmission electron microscopy (LC-TEM) offer unprecedented opportunities to directly observe how 2D MoS2 nanosheets interact with analytes in aqueous environments and how such interactions translate into electrical sensing in aqueous field-effect transistors (FETs). The central challenge is to visualize adsorption events and concomitant structural changes at high spatial and temporal resolution while preserving native water–material interfaces and avoiding beam‑induced artifacts that can confound interpretation of sensing events. The topic examined here synthesizes insights from three complementary perspectives:

- Branch 048ba9a7ec3bb39c (Electrochemical gating-integrated LC-TEM) emphasizes direct linkage between atomic-scale adsorption/healing events and FET electrical metrics, with emphasis on defect engineering, passivation, and liquid-cell configurations that enable high-capacitance gating and transparent electron windows.

- Branch b198468ed81ad39d (Ultra-low-dose, high-speed LC-STEM imaging) focuses on real-time observation of MoS2–analyte interactions under ultra-low-dose imaging conditions that preserve native chemistry, including phase dynamics in 1T/2H MoS2 and adsorption/desorption events with sub-nanometer spatial resolution and millisecond temporal resolution.

- Branch f34e509a8ff06b82 (Computational–experimental data-integration framework) provides a framework for mitigating beam-/radiolysis-related artifacts through physics-informed data fusion, deep-learning artifact detectors, multimodal synchronization, and open repositories to ensure reproducibility and robust interpretation.

Together, these perspectives frame a holistic view of how to image, quantify, and interpret real-time adsorption and structural changes in MoS2 nanosheets within aqueous FET sensing contexts, and how to configure the fluid cell, dose regime, gating strategy, and artifact-mitigation workflow to maximize fidelity of the native water–MoS2 interface while capturing high-resolution sensing events.

2) Synthesized Findings

Common themes and convergence

- Real-time visualization is feasible when two conditions are met: (i) the liquid cell provides a water-tight, electrically transparent environment with minimal beam-induced perturbation, and (ii) the imaging dose is managed so that radiolysis, charging, and bubble formation do not perturb native charge transport or adsorption kinetics.

- Electrochemical gating within LC-TEM is a robust route to correlate adsorption events with FET readouts. In the gating-integrated approach, adsorption of ions (even a single ion at a sulfur vacancy) can shift device thresholds on the order of tens of millivolts and modulate transconductance by several microSiemens, enabling direct correlation between atomic-scale events and macro-scale sensing signals.

- Defect engineering and passivation critically influence both the electronic transport and the ability to visualize processes. A high density of S-vacancies (~10^13 cm^-2) and a controlled amount of 1T metallic domains enable high reactivity and conduction, while h-BN passivation (~0.33 nm) can reduce hysteresis (<5 mV) and preserve electron transparency (>90% at 200 kV) but may modestly impact gate capacitance.

- Window design and gating strategy modulate the balance between maintaining a native water–MoS2 interface and enabling strong electrostatic control. Hybrid polymer‑graphene LC windows (30 nm Si3N4 with 150 nm electrolyte) support sub-nanometer imaging (≈0.1 nm) at high temporal resolution (≤0.5 s) while enabling high-capacitance electric double-layer gating (C_EDL > 10 µF cm^-2) and substantial carrier densities (~1×10^14 cm^-2). Ionic-liquid or ion-gel gating can substantially boost transconductance and suppress subthreshold swing, though gating performance depends on the gating medium and interface.

- Artefact mitigation frameworks are essential. Dose-rate is the dominant artifact driver across studies; safe windows have been identified (approximately 1×10^4 e^− nm^-2 s^-1, i.e., ≤0.1 e^− Å^-2 s^-1) to preserve ~95% of pristine MoS2 conductance. A computational–experimental loop combining data fusion (DFT-informed libraries, radiolysis maps), deep-learning artifact detectors (UNet for bubbling/ drift/contrast loss), and closed-loop control (CNN-LSTM controllers) reduces effective dose by ~30% to as much as 5× under aggressive low-dose regimes, while maintaining reliable kinetic measurements.

- Multi-modal synchronization improves kinetic extraction. Coordinating TEM imaging with SAED, EELS, Raman (e.g., 532 nm), and electrochemical readout yields robust phase and defect-density metrics linked to observable electronic responses, enabling extraction of kinetic constants (pseudo-first-order rates around ≈0.8–1.2 s^-1 and turnover frequencies on the order of 0.2–0.5 s^-1) that align with known bulk catalytic metrics in related MoS2 systems.

Important quantitative findings and design options

- Adsorption-induced gating in electrochemical LC-TEM: A single adsorbed ion at a sulfur vacancy yields a ~30 mV threshold shift and 5–10 µS transconductance spike; with sufficient defect density and passivation, hysteresis can be maintained at very low levels (<5 mV).

- Passivation and transparency: Monolayer h-BN encapsulation yields hysteresis suppression to <5 mV with ion transport preserved and >90% electron transparency at high accelerating voltages, illustrating that passivation need not sacrifice gating viability.

- Gate capacitance and carrier density: High-capacitance gating (C_EDL > 10 µF cm^-2) supports large carrier densities (~1×10^14 cm^-2), enabling robust sensing and sizable transconductance enhancements upon adsorption events.

- Mobility and defect-healing pathways: A two-step defect-healing protocol (hydrogen-rich IL anneal at 120°C plus 10 W O2/Ar plasma) can raise mobility from ~10 cm^2 V^-1 s^-1 to ~128 cm^2 V^-1 s^-1, while suppressing off-current from 10^-9 A to <10^-12 A and achieving wafer-scale on/off > 10^6 across 4-inch substrates. These improvements underpin reliable LC-TEM readout and device performance.

- Ultra-low-dose imaging and phase dynamics: Observations of 1T/2H phase-boundary motion occur on the timescale of 0.3–1.8 nm s^-1, with millisecond temporal resolution under ultra-low-dose conditions, enabling direct observation of phase evolution and its relation to adsorption sites.

- Specifics on sensing performance: In NO2/NH3 selective sensing scenarios, gating strategies (including negative and positive biases) can favor adsorption of NO2 or NH3, respectively, with significant selectivity in mixed-gas environments. Reported selectivities exceed 5:1 under certain biasing schemes.

Notable contradictions and how they are addressed

- Electron-beam charging vs electrochemical gating: A direct claim that electron-beam charging alone can reversibly switch MoS2 conductance in vacuum conflicts with observations in liquid cells where electrolyte screening mitigates beam-derived gating unless an explicit external reference gate is used. The resolution is that in liquid environments, stable modulation of conductance and adsorption readings are more reliably achieved via electrochemical gating rather than beam-induced gating, while the beam remains useful for structural imaging provided dose and artifacts are carefully controlled.

- Plasma finishing vs vacancy elimination: A statement claiming plasma finishing fully eliminates vacancies and yields intrinsic mobility (>300 cm^2 V^-1 s^-1) is contradicted by findings that a substantial fraction of vacancies can persist after plasma treatment; hydrogen-rich IL annealing is required to maximize mobility. The integrated view is that plasma treatment reduces defects but does not fully heal them; ionic-liquid–assisted healing provides additional defect passivation and mobility gains.

- h-BN encapsulation effects: While monolayer h-BN encapsulation can nearly eliminate hysteresis, counterpoints note that ion access may be impeded, potentially reducing gate capacitance relative to unencapsulated devices. The consensus is that a carefully tuned encapsulation strategy (e.g., partial coverage or engineered pores) can balance hysteresis suppression with sufficient ion transport to maintain gating performance.

- Carrier concentration vs phase transition: A claim that simply raising carrier concentration triggers a 2H→1T transition is not universally valid. The resolution is that phase transitions depend on a combination of carrier concentration, strain (≥0.5%), and defect density (e.g., S-vacancies). This underscores the need for joint control of multiple parameters to realize and study phase transitions in situ.

Gaps that remain (notable but acknowledged)

- Quantitative adsorption isotherms for Mg2+ and Ca2+ on isolated 1T vs 2H nanodots are not yet established; existing data often rely on analogies with Pb2+ or other species. Direct calibration of ion flux to TEM-contrast changes remains an open need.

- Exact dose-rate thresholds and cumulative-dose budgets for radiolysis-related artifacts under varying electrolyte conditions (types of ILs, pH, ionic strength) require systematic calibration across materials and solvents.

- Long-term stability under repeated pH/ionic-strength fluctuations and extended adsorption/desorption cycling (>10^4 cycles) has not been comprehensively characterized.

- Cross-material generalization (e.g., MoS2 vs WS2, MoSe2, WSe2) and elevated-temperature operation have limited quantitative validation; model extrapolations beyond room temperature need empirical support.

3) Contradiction Analysis & Resolution

- Beam-induced artifacts vs electrochemical control: While beam-induced gating can occur in principle, in liquid environments the electrolyte screen and the presence of a defined reference electrode render purely beam-driven modulation unreliable for reproducible measurements. Practical experiments achieve reliable modulation by combining electrochemical gating with low-dose LC-TEM imaging, enabling direct coupling of adsorption with FET response while minimizing artifacts.

- Plasma vs IL-assisted healing: Plasma reduces many defects but does not eradicate vacancies; hydrogen-rich IL annealing actively heals and passivates, dramatically improving mobility and reducing off-current. The resolution is to adopt a two-stage defect-management protocol: initial plasma treatment to remove gross residues, followed by IL-assisted annealing for deeper defect healing and mobility enhancement.

- h-BN passivation vs ion access: Monolayer h-BN can reduce hysteresis but can restrict ion access, potentially lowering gate capacitance. The resolution is to engineer the encapsulation strategy to retain ion transport while preserving conductance stability; this could include partial encapsulation, controlled defects, or ultrathin passivation that preserves gate control without fully impeding ion flow.

- Phase transition prerequisites: Carrier concentration alone is insufficient to induce a 2H→1T transition; strain and vacancy density are co-factors. A more nuanced view supports targeted defect engineering and strain application in conjunction with gating to realize controlled phase dynamics, observable by LC-TEM.

4) Unique Perspective Insights

- Branch 048ba9a7ec3bb39c (Electrochemical gating-integrated LC-TEM) contributes a practical blueprint for linking atomic-scale adsorption events to measurable electrical signals in a hydrated environment, including specific quantitative metrics (e.g., ~30 mV per ion, 5–10 µS transconductance) and a comprehensive defect-passivation strategy (≈1e13 cm^-2 S-vacancies, h-BN passivation) that minimizes hysteresis while maintaining high electron transparency. Its value lies in its explicit demonstration of how adsorption events translate into FET readouts within a liquid cell, the focused discussion of gate capacitance and selectivity, and the identification of a scalable defect-healing protocol and gating strategies.

- Branch b198468ed81ad39d (Ultra-low-dose LC-STEM of MoS2–analyte interactions) provides unprecedented observational capability for real-time adsorption and phase dynamics, including the ability to image 1T/2H phase-boundary motion and to extract kinetic constants that align with macroscopic catalytic metrics. Its core contribution is demonstrating that sub-nanometer spatial resolution and ms-scale temporal resolution are achievable without compromising native chemistry, given appropriate dose control and artifact suppression (e.g., dose-rate windows, scavengers, beam-blanking).

- Branch f34e509a8ff06b82 (Computational–experimental data-integration) delivers a rigorous framework for artifact mitigation and interpretation, combining physics-informed models (DFT libraries, radiolysis maps), Bayesian inference, and deep-learning detectors to detect and suppress artefacts in real time. It provides a pathway to standardized, reproducible analyses, reducing the subjectivity of interpreting LC-TEM data and enabling open data practices through annotated repositories. This perspective emphasizes the importance of cross-disciplinary tooling (hardware, software, and theoretical models) to enable trustworthy inference about adsorption events and sensing performance.

- The combined viewpoint emphasizes a multi-pronged, rigorously quantified approach: achieving high-fidelity observation requires careful coordination of fluid-cell design, passivation strategies, gating configurations, dose-management, and real-time data analytics. Each perspective contributes a necessary facet: physical device engineering (electrochemical gating, window design, passivation), imaging strategies (ultra-low-dose, high-speed MoS2 imaging, phase tracking), and computational rigor (artifact mitigation, data fusion, open data). The integrated view supports a disciplined path toward reliable interpretation of adsorption and structural dynamics during analyte binding.

5) Comprehensive Conclusion

In situ LC-TEM provides a viable and highly informative route to directly visualize the real-time adsorption and structural evolution of MoS2 nanosheets used in aqueous FET sensing during analyte binding. The convergence of optimized fluid-cell configurations, dose regimes, passivation, and gating strategies enables faithful observation of adsorption events and concomitant structural changes, while minimizing beam-induced artifacts that could confound interpretation.

Key conclusions include:

- Fluid-cell configurations must balance electrostatic control with electrolyte transparency. A hybrid polymer‑graphene LC window paired with a Si3N4 substrate (around 30 nm window and 150 nm electrolyte) supports high capacitance gating (C_EDL > 10 µF cm^-2) and sub-nanometer imaging, enabling direct correlation between adsorbate events and FET responses.

- Passivation and defect-engineering are essential for reliability. Defect-rich MoS2 (S-vacancies, 1T/2H mixed phases) provides active adsorption sites, while passivation strategies (h-BN monolayers) can suppress hysteresis and preserve electron transparency, albeit with potential trade-offs in ion access and gate capacitance that should be carefully engineered.

- Dose management is paramount. A conservative, physics-informed dose window (~1×10^4 e^- nm^-2 s^-1 or ~0.1 e^- Å^-2 s^-1) preserves the native conductance and suppresses radiolysis, with further improvements achieved by complementary computational and AI-driven artifact-detection and dose-reduction loops that can reduce dose by factors of 2–5× while maintaining reliable kinetic information.

- Multi-modal, synchronized measurements strengthen interpretation. Integrating TEM (and LC-TEM) imaging with SAED, EELS, Raman, XPS, and electrochemical readouts enables robust extraction of kinetic constants and correlation to device-level sensing metrics, thereby bridging atomic-scale events with macroscopic sensor performance.

- There is a coherent, though nuanced, set of design guidelines for maximizing fidelity of observed sensing events: careful choice of gating scheme (electrochemical gating with a reference electrode), consideration of graphitic or polymeric windows to balance water–material interface preservation with electron transparency, and a deliberate sequence of material processing steps (plasma cleaning, IL anneals) to optimize mobility and defect landscapes.

In sum, by orchestrating the fluid-cell architecture, gating strategy, dose-management protocol, and artifact-mitigation workflow, it is feasible to directly visualize, in real time, the adsorption and structural evolution of MoS2 nanosheets during analyte binding in aqueous FET sensors. The integrated insights from electrochemical gating, ultra-low-dose imaging, and computational artifact mitigation provide a robust, reproducible blueprint for conducting such investigations and for translating atomic-scale observations into meaningful sensor performance metrics.

6) Candidate Inventory

MoS2, 1T-MoS2, 2H-MoS2, mixed-phase MoS2 (1T/2H), MoS2 monolayer, MoS2 multilayer, h-BN, graphene, polymer-sealed Si3N4, ionic liquids (EMIM-BF4 and hydrogen-rich ILs), ion-gel electrolytes, O2/Ar plasma, hydrogen-rich IL anneal, defect/dopant strategies (Co, Mn, Fe doping in MoS2), MoS2/CoS2, ReS2 heterostructures, Ni-doped MoS2, Au contacts, Ti/Au contacts, SiN_x/SiO2 substrates, Protochips Poseidon, HAADF-STEM, 4D-STEM, EELS, Raman (532 nm), XPS, HRTEM, EIS, MoS2/CoS2 composites, CO, NO2, Mg2+, Ca2+, Pb2+, LiPS, Li+, DMP, Rhodamine B, Methylene Blue, 4-Chlorophenol, Li2S6.

Table: Representative Categories and Parameters

| Category | Representative Material/Methodology | Performance Highlights | Key Advantage | Main Limitation |
|---|---|---|---|---|
| In situ LC-TEM with electrochemical gating | MoS2 monolayer with h-BN passivation; graphene window; reference electrode gating | Single ion adsorption shifts ΔVth ≈ 30 mV; transconductance ΔG ≈ 5–10 µS; C_EDL > 10 µF cm^-2; carrier density ≈ 1×10^14 cm^-2 | Direct correlation between adsorption and FET readout; strong electrostatic control | Requires robust reference electrode; complexity in device integration |
| Ultra-low-dose LC-STEM imaging | Defect-rich, mixed-phase MoS2 (1T/2H); MoS2 nanodots 2–5 nm | Imaging ≤ 10 e^- Å^-2 s^-1; sub-nm spatial; ms-scale timing; phase-boundary motion 0.3–1.8 nm s^-1 | Preserves native water–MoS2 interface; captures adsorption events directly | Requires advanced instrumentation; radiolysis mitigation essential |
| Defect-healing and mobility enhancement | Hydrogen-rich IL anneal (120°C) + O2/Ar plasma | Mobility 10 → 128 cm^2 V^-1 s^-1; off-current < 10^-12 A; on/off > 10^6 | Substantial device performance gains; wafer-scale compatibility | Post-treatment steps may alter chemical environment |
| AI-driven artifact mitigation framework | UNet-based artifact detection; CNN-LSTM closed-loop | Dose reduction 30%–×5; IoU > 0.85; latency ≤ 30 ms | Systematic artifact suppression; reproducible, real-time analysis | Requires large, diverse datasets; generalization concerns |
| Window/passivation engineering | Polymer-graphene LC windows; h-BN encapsulation | High transparency; ~>90% electron transparency at 200 kV; hysteresis < 5 mV | Maintains water–material interface with good gating | Encapsulation may constrain ion access or require tuning |

Note: Performance Highlights reflect metrics reported in the three branches; where multiple values exist, the table presents representative numbers discussed in the synthesis.

In sum, the integrated report supports a practical, multi-faceted strategy for utilizing in situ LC-TEM to visualize and interpret real-time adsorption and structural changes in MoS2 nanosheets during analyte binding in aqueous FET sensors. The synergy of fluid-cell design, defect engineering, low-dose imaging, advanced gating, and artifact-mitigation workflows provides a credible path to capturing high-resolution sensing events while preserving native water–material interfaces.

End of Report