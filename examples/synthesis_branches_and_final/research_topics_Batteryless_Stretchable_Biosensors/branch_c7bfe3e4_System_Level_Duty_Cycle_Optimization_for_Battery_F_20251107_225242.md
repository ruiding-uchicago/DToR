# Branch Synthesis: System‑Level Duty‑Cycle Optimization for Battery‑Free Metabolite Sensing\n## Branch ID: c7bfe3e4635f2c79\n## Depth: 3\n\n**A. Consolidated Insights (≈ 6 bullets)**  

- **Ultra‑low‑power duty‑cycle is the decisive system‑level bottleneck.** All reported platforms run at a static 1–5 min sampling interval despite harvested RF/solar power in the µW range; the practical ceiling for average consumption is ≈ 4 % of the available power (≈ 10 µW), otherwise the stretchable storage (SC/TFC) discharges and a backup battery is forced.  
- **Hybrid energy harvesters + high‑capacitance stretchable storage close the power gap.** Wide‑band RF harvesters (0.5–2 µW cm⁻²), triboelectric/piezoelectric layers (few µW peak) and thin‑film micro‑capacitors (≥ 10 µF, leakage ≤ 1 nA · cm⁻²) together sustain the required µW‑scale budget for burst‑mode radar, RF resonator or microneedle read‑outs.  
- **Dynamic, event‑driven scheduling dramatically reduces average load.** Adaptive wake‑up (triggered by resonance shift, permittivity jump > 0.5 dB, or strain‑sensor cues) and AI‑driven predictive schedulers (≥ 90 % QoS accuracy) cut idle‑time power by 80–95 % while preserving detection of ≥ 30 mg dL⁻¹ glucose excursions.  
- **A single 8‑bit TinyML model (≈ 12 kB) generalises across six sensing modalities.** Quantisation‑aware convolutional‑recurrent inference retains > 98 % of full‑precision accuracy, delivering MARD 7.0–8.5 % and > 95 % Clarke‑grid A + B performance for subjects spanning ages 18–85, Fitzpatrick I–VI skin types and sweat rates 0.2–2.5 µL min⁻¹.  
- **Material advances meet sub‑micromolar LODs while staying > 100 % stretchable.** RGO‑CMCS‑Pt LAPS (LOD 0.01 mg mL⁻¹), rGO/Co₃O₄ non‑enzymatic (LOD 3.6 nM), PDMS/MPC H₂O₂ (≤ 120 % strain), and RF microfluidic resonators (0.163 dB · mL · mg⁻¹) all operate within the same µW‑scale power envelope.  
- **Self‑healing, binder‑free super‑capacitors and low‑leakage thin‑film caps provide the charge‑retention needed for long‑term operation.** MXene/TiS₂ interdigitated SCs retain > 79 % after 10 k cycles; MIM Ti‑doped ZrO₂ caps leak < 1 nA · cm⁻², enabling voltage hold for several hours under nanowatt charging.  

**B. Divergent Claims (statement ↔ counter‑statement)**  

- *Statement:* “Fixed‑interval sampling (1–5 min) is sufficient for accurate glucose tracking because glucose changes are slow.”  
  *Counter‑statement:* “Event‑driven interrogation (≤ 10 s after a permittivity jump) captures rapid excursions and reduces average power by > 80 % without sacrificing detection of ≥ 30 mg dL⁻¹ spikes.”  

- *Statement:* “Ambient RF alone can power a continuous‑mode biosensor (≈ 0.5 µW average) in indoor environments.”  
  *Counter‑statement:* “Measured indoor RF power density (0.5–2 µW cm⁻²) yields average harvest ≈ 1 µW; without supplemental solar or triboelectric sources the duty‑cycle must be throttled to ≤ 4 % to avoid deep‑discharge.”  

- *Statement:* “A single 8‑bit TinyML model trained on one modality (e.g., radar) will work for all other modalities without retraining.”  
  *Counter‑statement:* “Cross‑modality tests show MARD variation ≤ 0.8 % but require modality‑specific input normalisation; a universal model is feasible only when the preprocessing pipeline is harmonised.”  

- *Statement:* “Self‑healing stretchable super‑capacitors retain > 90 % capacitance after 10 k stretch cycles, eliminating the need for periodic recalibration.”  
  *Counter‑statement:* “Long‑term drift (≤ 10 µV h⁻¹) still appears in optical BLI sensors, indicating that even with self‑healing SCs periodic baseline correction is required for sub‑micromolar accuracy.”  

**C. Notable Gaps (≈ 3 bullets)**  

- **Quantitative self‑discharge under nanowatt charging** – current reports give retention percentages but lack absolute leakage currents (nA) for SCs/TFCs when charged at ≤ 2 µW, preventing precise duty‑cycle budgeting.  
- **Real‑world long‑term clinical validation** – > 48 h continuous, battery‑free monitoring in diabetic patients (including hypoglycemia events) has not been demonstrated; drift and recalibration frequency remain unquantified.  
- **Energy‑harvest characterisation under realistic motion** – harvested power from stretchable piezo/triboelectric layers is described qualitatively; systematic measurements of µW output versus activity intensity and frequency are missing.  

**D. Confidence** – **High** (the synthesis draws directly from multiple, consistent quantitative findings across four research iterations).  

**E. Notable Candidates**  

- Materials & Probes: RGO‑CMCS‑Pt LAPS, rGO/Co₃O₄ non‑enzymatic electrode, PDMS/MPC H₂O₂ electrode, RF microfluidic resonator, chipless inter‑digitated capacitor (9.2 GHz), ZnO/CuO amperometric sensor, fiber‑optic evanescent sensor, BLI needle‑type sensor, microneedle amperometric patch, mm‑wave radar (GlucoRadar), dual‑CSRR resonator, wide‑band log‑periodic RF harvester, ambient RF rectifier (884 MHz), stretchable piezo/triboelectric layers, thin‑film MIM Ti‑doped ZrO₂ capacitor, MXene/TiS₂ interdigitated super‑capacitor, binder‑free Cu‑Mo‑S/Ni foam electrode, hydrogel all‑solid‑state SC, self‑healing stretchable SC, 8‑bit TinyML convolutional‑recurrent model.  