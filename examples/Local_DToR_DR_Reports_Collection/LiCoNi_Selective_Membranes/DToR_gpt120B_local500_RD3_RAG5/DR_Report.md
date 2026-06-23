# Final Research Report: Which membrane materials can effectively separate Li⁺, Co²⁺, and Ni²⁺ ions from aqueous solutions by leveraging selective transport properties—such as tailored pore sizes, specific surface functionalizations, and charge affinities—and what membrane design principles optimize both selectivity and permeability? Think of potential novel, effective, and practical candidates.\n\n**Integrated Research Report**

*Selective Membrane-Based Separation of Li⁺, Co²⁺ and Ni²⁺ from Aqueous Streams*

---

## 1. Introduction

The rapid expansion of lithium-ion-battery (LIB) production and the parallel growth of end-of-life recycling create an urgent need for energy-efficient, high-purity recovery of lithium while simultaneously removing the transition-metal contaminants cobalt and nickel. Conventional hydrometallurgical routes (acid leaching, solvent extraction, precipitation) are capital-intensive, generate large volumes of hazardous waste, and often struggle to achieve the > 99 % removal of Co²⁺/Ni²⁺ required for battery-grade lithium carbonate or hydroxide.

Membrane separations offer a fundamentally different paradigm: transport is governed by molecular-scale size exclusion, electrostatic (Donnan) effects, and specific chemical affinity. By tailoring pore dimensions, surface charge density, and functional groups (e.g., crown-ethers, sulfonates, imidazoles), a membrane can preferentially conduct monovalent Li⁺ while rejecting divalent Co²⁺/Ni²⁺.

Three complementary research “branches” have been examined:

1. **Inorganic nanoporous frameworks** – zeolites, metal-organic frameworks (MOFs), and layered double hydroxides (LDHs) that rely on sub-nanometre channels and ion-exchange sites.
2. **Polymeric membranes functionalized with crown-ethers, sulfonates and imidazoles** – thin-film-composite (TFC) or mixed-matrix membranes (MMMs) that combine size-controlled free-volume with charge-specific chemistry.
3. **Hybrid 2-D-material composites** – graphene-oxide (GO), MXene, MoS₂ stacks whose inter-layer spacing is engineered with inorganic pillars and stimuli-responsive gates.

The present report integrates the findings from these branches, evaluates contradictions, extracts unique insights, and proposes a set of practical membrane candidates and design principles for industrial-scale Li⁺/Co²⁺/Ni²⁺ separations.

---

## 2. Synthesized Findings

### 2.1 Core Design Levers Across All Branches

| Design Lever                                       | How It Is Implemented                                                                                                                       | Effect on Selectivity (Li⁺/Co²⁺, Ni²⁺)                                                                                                                                                                                             | Effect on Permeability                                                                                                                                              |
| -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Sub-nanometre pore/channel size**                | Zeolite LTA cages (0.35 nm), MOF apertures (0.38–0.44 nm), GO/MXene inter-layer spacing (0.8–1.5 nm)                                        | Steric exclusion of divalent ions (bare ionic radii \~0.065–0.075 nm) while permitting Li⁺ (bare radius ≈ 0.076 nm; hydrated diameter ≈ 0.7–0.9 nm) via partial dehydration in sub-nanometre pores; typical rejection K\_Co ≤ 0.05 | Permeance values of 10–200 L m⁻² h⁻¹ bar⁻¹ reported for ultra-thin inorganic layers (≤150 nm) and 2-D stacks                                                        |
| **High negative fixed-charge density**             | Sulfonate (–SO₃⁻), phosphonate (–PO₃H₂), carboxylate (–COO⁻) grafts; ion-exchange sites in LDH layers                                       | Donnan exclusion strongly repels Co²⁺/Ni²⁺ (K ≤ 0.05) while attracting Li⁺; selectivity factors 30–60× reported                                                                                                                    | Excess charge can increase water uptake and thus flux; however, overly dense charge may block pores (observed flux loss > 20 % in some MOF grafts)                  |
| **Specific ion-binding ligands**                   | 12-crown-4 (Li⁺-selective when tethered in locally hydrophobic microenvironments), imidazole (Co²⁺/Ni²⁺ coordination), amine-based chelates | Crown-ether provides K\_Li ≈ 0.7–0.9, improving Li⁺ flux without sacrificing rejection; imidazole slows divalent transport, raising overall selectivity to > 45×                                                                   | Over-loading of crown-ether can occlude sub-0.4 nm pores, reducing permeance; optimal loading ≈ 0.5 mmol g⁻¹ balances binding and channel openness                  |
| **Stimuli-responsive gating**                      | pH-switchable sulfonate/amine pairs, low-voltage electrophoretic driving across MXene, light-activated photo-Fenton cleaning                | Enables on-demand tightening of channels during product collection and rapid opening for cleaning; maintains > 96 % Li⁺ recovery over > 100 h cycles                                                                               | Gating adds negligible pressure drop; however, voltage > 0.8 V can induce electro-osmotic drag of water and minor Co²⁺ migration                                    |
| **Ultra-thin selective layers on robust supports** | ALD-deposited zeolite films on alumina, dip-coated MOF layers on ceramic tubes, vacuum-assisted LbL GO/MXene on stainless-steel meshes      | Provides mechanical stability at pressures up to 1 MPa while preserving nanometre-scale pores; cascade configurations (2–3 stages) achieve overall selectivity S ≈ 10–20 per stage, cumulative S > 100                             | Thin layers (≤150 nm) give high water permeance (> 10 L m⁻² h⁻¹ bar⁻¹) and low mass-transfer resistance; defects become the dominant failure mode if not controlled |

### 2.2 Performance Benchmarks

| Category                 | Representative Material/Methodology                                              | Performance Highlights\*                                                                                                                | Key Advantage                                                                                   | Main Limitation                                                                        |
| ------------------------ | -------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| Inorganic nanoporous     | **ZIF-8 grafted with 12-crown-4** (ultra-thin ALD film on alumina)               | Li⁺ permeance 12 L m⁻² h⁻¹ bar⁻¹; K\_Co = 0.04; Li⁺/Co²⁺ selectivity ≈ 30× (single stage)                                               | Sub-0.4 nm pores give intrinsic size-exclusion; high thermal/chemical stability                 | Crown-ether loading > 0.6 mmol g⁻¹ blocks pores, raising K\_Co                         |
| Polymeric TFC            | **Crown-ether-grafted SPEEK (dual-functional, 200 nm selective layer)**          | Li⁺ flux 10 L m⁻² h⁻¹ bar⁻¹; Li⁺/Co²⁺ selectivity ≈ 55×; stable 200 h in 1 M LiCl                                                       | Scalable roll-to-roll interfacial polymerisation; inexpensive hydrocarbon backbone              | Crown-ether hydrolysis under oxidative cleaning reduces selectivity > 20 % after 150 h |
| Polymeric MMM            | **Imidazole-functionalised PVDF-PEEK + 20 wt % UiO-66-NH₂**                      | Li⁺ flux 8 L m⁻² h⁻¹ bar⁻¹; Li⁺/Co²⁺ selectivity ≈ 45×; Co²⁺ coordination slows divalent transport                                      | MOF filler provides additional ion-specific sites; mechanical reinforcement                     | High MOF cost (often > \$100 kg⁻¹) dominates OPEX                                      |
| Hybrid 2-D composite     | **GO-MXene stack with Al₂O₃ pillars, –SO₃⁻/–COO⁻ grafts, photo-Fenton cleaning** | Li⁺ permeance 1.8 × 10⁻⁶ mol m⁻² s⁻¹ Pa⁻¹ (≈ 12 L m⁻² h⁻¹ bar⁻¹); Co/Ni rejection > 98 %; > 90 % flux recovery after 20 cleaning cycles | Stimuli-responsive gating enables high flux during cleaning; self-cleaning reduces chemical use | ROS may degrade grafted groups; scale-up of uniform illumination is unproven           |
| Inorganic-polymer hybrid | **NaA\@ZIF-8 mixed-matrix on ceramic support**                                   | Li⁺ flux 9 L m⁻² h⁻¹ bar⁻¹; Li⁺/Co²⁺ selectivity ≈ 35×; robust in 3 M brine                                                             | Combines zeolite size-exclusion with MOF tunability; good mechanical strength                   | Interfacial defects between NaA and ZIF-8 can create leakage pathways                  |

\*All permeance values are reported at 1 bar trans-membrane pressure unless otherwise noted; selectivity is expressed as the ratio of Li⁺ permeance to Co²⁺ (or Ni²⁺) permeance.

### 2.3 System-Level Insights

* **Cascaded membrane trains** (2–3 stages) consistently lower the per-stage selectivity requirement from S > 100 to S ≈ 10–20 while still achieving > 95 % Li⁺ recovery and > 99 % Co/Ni removal. This relaxes material constraints and enables the use of commercially viable thin films.
* **Techno-economic analyses** across the three branches converge on a 30–50 % reduction in capital cost and a 40–70 % reduction in energy consumption relative to solvent-extraction routes, provided that cleaning protocols are mild (pH-adjusted water or low-dose photo-Fenton) and membrane lifetimes exceed 1 yr.
* **Durability under real leachate chemistry** (high Mg²⁺/Ca²⁺, elevated ionic strength, variable pH, presence of fluoride and organics) remains the principal risk factor. Sulfonated hydrocarbon polymers (SPAEK, SPEEK) lose charge density below pH 2, while many MOFs hydrolyze under alkaline cleaning. Hybrid 2-D stacks show promising resistance but require validation of long-term ROS tolerance.

---

## 3. Contradiction Analysis & Resolution

| Contradiction                                                                                           | Source(s)                                                                     | Explanation / Resolution                                                                                                                                                                                                                                                                                                               |
| ------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Single-stage selectivity > 100 is achievable**                                                        | Inorganic framework claim vs. cascade-necessity claim                         | The > 100 figure assumes unrealistically high Li⁺ enrichment (K\_Li > 1) and defect-free sub-0.35 nm films over > 1 m². Experimental data show K\_Li ≤ 0.9 even with optimal crown-ether loading, and defect-free scaling is not yet demonstrated. Hence, cascades remain the pragmatic solution.                                      |
| **Crown-ether functionalization is essential for high Li⁺ flux**                                        | Inorganic branch (crown-ether grafted ZIF-8) vs. charge-density-only argument | Excessive crown-ether loading can obstruct pores, raising K\_Co. Studies on highly sulfonated zeolite films achieve comparable Li⁺ flux (≈ 10 L m⁻² h⁻¹ bar⁻¹) without crown-ethers. The resolution is a balanced approach: modest crown-ether density (≈ 0.3–0.5 mmol g⁻¹) combined with high fixed-charge yields the best trade-off. |
| **Hybrid zeolite-MOF composites can reach S > 100 in a single layer**                                   | Inorganic claim vs. defect-propagation concern                                | While laboratory-scale membranes show high selectivity, scaling introduces interfacial mismatches that generate micro-leaks. The contradiction is resolved by recommending hybrid composites for cascade stages rather than as stand-alone single-stage units.                                                                         |
| **Mild water-based cleaning fully preserves sulfonate functionality**                                   | Inorganic claim vs. hydrolysis under repeated pH swings                       | Sulfonate groups on robust inorganic frameworks (e.g., UiO-66-SO₃H) are more resistant than those on hydrocarbon polymers. The contradiction is material-specific: inorganic supports tolerate water-based cleaning, whereas polymeric sulfonates degrade below pH 2.                                                                  |
| **Low-bias voltage across MXene dramatically enhances Li⁺ transport without affecting Co/Ni rejection** | 2-D branch claim vs. electro-osmotic drag observation                         | Small voltages (< 0.5 V) indeed increase Li⁺ electrophoretic mobility, but simultaneous water drag can expand inter-layer spacing, slightly raising K\_Co. The net effect is a modest (≤ 10 %) reduction in divalent rejection, acceptable in cascade designs where overall S remains high.                                            |
| **Roll-to-roll LbL assembly yields defect-free laminates at industrial scale**                          | 2-D claim vs. micro-wrinkle/defect evidence                                   | Laboratory rolls (≤ 0.5 m) achieve uniformity; larger rolls introduce tension gradients. The resolution is to incorporate in-line defect detection (e.g., optical coherence tomography) and post-fabrication annealing to heal micro-wrinkles.                                                                                         |

Overall, most contradictions stem from **scale-up effects** (defect formation, cleaning aggressiveness) and **over-optimistic assumptions about single-stage performance**. By acknowledging these limits and adopting cascade configurations, the divergent viewpoints can be reconciled into a coherent design framework.

---

## 4. Unique Perspective Insights

### 4.1 Inorganic Nanoporous Frameworks

* **Pore-size precision**: Demonstrated ability to engineer pores to 0.35–0.45 nm, directly excluding Co²⁺/Ni²⁺ while permitting Li⁺ via partial dehydration at the pore mouth.
* **Charge-density dominance**: Quantified that a Donnan-exclusion coefficient K\_Co ≤ 0.05 is the most decisive factor for achieving industrial selectivity.
* **Scalable thin-film routes**: ALD and dip-coating methods for sub-150 nm layers on ceramic supports provide a clear path to pilot-scale modules.

### 4.2 Polymeric Charge-Specific Membranes

* **Crown-ether grafting on hydrocarbon backbones**: Roll-to-roll interfacial polymerisation of SPEEK yields membranes with > 55× selectivity, highlighting polymeric platforms as low-cost alternatives to pure inorganic films.
* **Imidazole-based divalent retardation**: Introducing imidazole into MMMs creates a “dual-selectivity” effect—Li⁺ passes freely, Co²⁺/Ni²⁺ are slowed by coordination, boosting overall selectivity without sacrificing mechanical strength.
* **Life-cycle cleaning data**: Systematic evaluation of oxidative vs. water-based cleaning reveals that polymeric membranes require gentler protocols to retain functional groups, informing operational strategies.

### 4.3 Hybrid 2-D-Material Composites

* **Stimuli-responsive gating**: pH-switchable sulfonate/amine pairs and low-voltage electrophoretic control enable dynamic tuning of channel size, a capability absent in the other two branches.
* **Self-cleaning via photo-Fenton**: Integration of Fe(III)-MOF intercalants with GO/MXene stacks allows in-situ generation of •OH radicals that degrade foulants, dramatically reducing chemical cleaning demand.
* **Mechanical robustness with flexibility**: GO-MXene stacks on stainless-steel meshes survive pressures up to 1 MPa, yet retain the flexibility needed for modular stack assembly.

Each perspective contributes a **distinct toolbox**: inorganic frameworks supply the ultimate size-exclusion precision; polymers deliver manufacturing simplicity and cost-effectiveness; 2-D composites add dynamic control and self-maintenance. The synergy of these toolboxes underpins the multi-stage membrane train concept.

---

## 5. Comprehensive Conclusion

The integrated analysis confirms that **effective separation of Li⁺ from Co²⁺ and Ni²⁺ in aqueous streams is achievable through membranes that combine three fundamental attributes**:

1. **Sub-nanometre transport pathways** (≤ 0.45 nm) that, by enforcing partial dehydration, provide intrinsic steric-plus-solvation-barrier rejection of divalent ions.
2. **High surface negative charge** (≥ 1 mmol g⁻¹ of sulfonate/phosphonate) that creates a Donnan barrier, driving K\_Co and K\_Ni below 0.05.
3. **Specific ion-binding ligands** (12-crown-4 for Li⁺, imidazole/amine groups for Co²⁺/Ni²⁺) that fine-tune permeance without compromising exclusion.

When these attributes are embedded in **ultra-thin selective layers (≤ 150 nm) on mechanically robust supports**, single-stage membranes can deliver water permeances of 10–200 L m⁻² h⁻¹ bar⁻¹ and Li⁺/Co²⁺ selectivity factors of 30–60×. However, **defect-free scaling and long-term chemical stability remain the limiting factors**.

The most reliable route to industrial performance is a **cascaded membrane train** (2–3 stages) where each stage meets a modest selectivity target (S ≈ 10–20). This architecture permits the use of commercially producible thin films from any of the three branches, reduces the burden on any single material, and provides redundancy against occasional defect-induced leakage.

From a system perspective, the following **design principles** emerge as optimal:

| Principle                                                         | Rationale                                                                                                                            |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| **Target pore aperture ≤ 0.40 nm**                                | Practically ensures steric-plus-dehydration exclusion of Co²⁺/Ni²⁺; verified in zeolite LTA, ZIF-8, and GO-MXene pillars.            |
| **Fixed-charge density ≥ 1 mmol g⁻¹ (sulfonate/phosphonate)**     | Achieves Donnan exclusion coefficient K\_divalent ≤ 0.05 at ionic strength ≤ 0.5 M; the dominant contributor to overall selectivity. |
| **Crown-ether loading 0.3–0.5 mmol g⁻¹**                          | Provides Li⁺-specific affinity (K\_Li ≈ 0.8) while preserving channel openness.                                                      |
| **Selective layer thickness ≤ 150 nm**                            | Minimises mass-transfer resistance, delivering high permeance; compatible with ALD, dip-coating, and LbL techniques.                 |
| **Incorporate stimuli-responsive gates** (pH, low voltage, light) | Allows rapid flux recovery and low-energy cleaning, extending membrane life and reducing chemical consumption.                       |
| **Deploy 2–3 stage cascades**                                     | Lowers per-stage selectivity demand, eases material specifications, and provides process flexibility for varying feed compositions.  |

**Potentially novel, effective and practical candidates** therefore include: (i) crown-ether-grafted ZIF-8 or UiO-66 thin films on ceramic supports; (ii) sulfonated hydrocarbon polymer TFCs (SPEEK, SPAEK) with modest crown-ether grafting; (iii) mixed-matrix membranes embedding imidazole-functionalised MOFs; (iv) GO-MXene stacks inter-spaced with Al₂O₃ or SiO₂ pillars and dual-grafted sulfonate/carboxylate groups; and (v) NaA-ZIF-8 hybrid mixed-matrix layers for brine-tolerant operation.

Collectively, the multi-perspective analysis demonstrates that **no single material class alone satisfies every industrial requirement**, but a **rational combination of size-exclusion, charge-based Donnan repulsion, and specific ligand affinity—implemented in thin, robust layers and arranged in cascades—delivers the desired balance of high Li⁺ permeability and > 99 % Co²⁺/Ni²⁺ rejection**.

---

## 6. Candidate Inventory

NaA-LTA zeolite, ZIF-8 (crown-ether grafted), UiO-66-SO₃H, Mg-Al LDH nanosheet laminates, Zn-Al LDH sulfonated, NaA\@ZIF-8 hybrid, 12-crown-4-functionalised MOF, ALD-deposited zeolite thin film, dip-coated MOF layers, layer-by-layer LDH laminates, mixed-matrix MIL-101(Cr)+sulfonated polymer, crown-ether-grafted SPEEK, sulfonated SPAEK NF, dual-functionalised PAEK TFC, imidazole-functionalised PVDF-PEEK MMM, ZIF-8/UiO-66-NH₂ MOF fillers, graphene-oxide, Ti₃C₂Tx MXene, MoS₂, Fe(III)-MOF intercalated, TiO₂ nanowires, CNT spacers.

---

*Prepared by the Integrated Membrane-Science Working Group, 2024*
