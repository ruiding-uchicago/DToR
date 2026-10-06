## 3) Standard Operating Procedures (SOP)

### A) Au‑IDE + Inkjet‑Printed GFET (Back‑Gated on Si/SiO₂)

**A1. Substrate prep**  
1. Dice Si/SiO₂ wafers to chip size if not already patterned.  
2. If fabricating IDEs in‑house: perform photolithography (or lift‑off) to define IDEs. **Target geometry**: S≈**200 µm**, W≈**100 µm** (see QA section for masks).  
3. Clean chips (solvent rinse IPA/acetone/DI → N₂ dry). Optional O₂ plasma: 30–60 s, low power, to increase wettability.

**A2. Graphene ink printing**  
1. Mount chips on heated stage at **~60 °C**.  
2. Load **10 pL** cartridge; verify drop formation and alignment.  
3. **Drop spacing** (typical recipes): **25 µm**; **coats/passes**: **5–10** depending on target sheet resistance.  
4. Print the channel to bridge IDE gaps (design span often **~500 µm** across the active area).  
5. Dry on stage 2–5 min between passes.  
6. Post‑print **anneal**: **200–350 °C** in air or inert (lab recipe dependent). Common sets used historically:  
   - IDE stack baked **350 °C**; graphene channel **200–350 °C**.

**A3. Optional surface functionalization (for biosensing)**  
- If using graphene as sensing interface directly (solution‑gated), functionalize with **PBASE** (π–π linker) followed by probe molecules (e.g., aptamers/antibodies). See RFG section **C3** for timings/solutions.

**A4. Electrical bring‑up (back‑gate)**  
1. Place on probe station.  
2. Bias **V_D = 0.05–0.5 V**; sweep **V_G** on Si back gate (range depends on oxide thickness and leakage; for **300 nm SiO₂** lab often sweeps up to tens of volts; for **90 nm SiO₂**, proportionally less).  
3. Record **transfer curves** (Id–Vg) and **output curves** (Id–Vd).  
4. For temperature studies, use a stage at **30–60 °C** (e.g., datasets named `30c.xls`, `40c.xls`, `55C.xls`).

**A5. Solution‑gate option**  
- Add a droplet of buffer across the channel; immerse **Ag/AgCl** micro‑reference as gate; sweep **0–0.5 V** relative to source. See section **D** for measurement hygiene.

---

### B) All‑Printed / Hybrid MoS₂ FET Variants

**B1. MoS₂ ink preparation (summary)**  
- Electrochemical intercalation of bulk MoS₂ with tetrahexylammonium bromide; sonication to form nanoplates; disperse in printable solvent system. (Detailed recipe lives with the ink supplier/lab notebook.)

**B2. Printing & device stack**  
1. Print **graphene S/D**, **MoS₂ channel**, and optionally **hBN dielectric**.  
2. For back‑gate on **300 nm SiO₂**, expect higher gate voltages (tens of volts).  
3. For **low‑voltage** operation, print an **ion‑gel gate** atop the channel and use a side‑gate; the gel’s high capacitance enables **≤2 V** gating.

**B3. Thermal treatments**  
- Bake printed films to remove solvent/surfactant (times/temps depend on ink formulation). Avoid exceeding substrate limits for PI/PET.

**B4. Characterization**  
- Measure Id–Vg and Id–Vd; evaluate mobility, on/off, and gas sensing (e.g., NO₂, NH₃) if relevant.

---

### C) RFGFET (Remote Floating‑Gate) Sensing Module

**C1. RFG electrode wafer prep**  
1. **Substrate:** 4" Si with **300 nm SiO₂**.  
2. **O₂ plasma**: 5 min at ~250 W, ~10 sccm O₂.  
3. **Silane functionalization** *(choose one)*:
   - **APTMS**, 5% in ethanol, 2 h immersion → rinse → **120 °C** bake 20 min.  
   - **HMDS**, 5% in ethanol, 2 h immersion → rinse → **120 °C** bake 20 min.

**C2. GO deposition & reduction**  
1. Prepare **0.24 mg/mL GO** in DI water; ultrasonicate 20 min.  
2. **Drop‑cast 16 mL** GO across the full 4" wafer.  
3. **Bake 120 °C, 1 h** to dry/laminate multilayer GO.  
4. Dice to **1 × 2 cm²** RFG modules.  
5. **Post‑anneal** modules **10 min @ 200 °C** in **Ar** to partially reduce GO (forming rGO).

**C3. Surface functionalization for sensing**  
- **PBASE** adsorption: immerse in **10 mg/mL PBASE in DMF** for **0–120 min** (typical 90–120 min). Rinse in DMF.  
- **Probe immobilization** examples:  
  - **Heavy metal (Pb²⁺)**: incubate **10 mM glutathione (GSH)** in water for **2 h**; rinse, dry.  
  - **Protein assays**: immobilize aptamers/antibodies via PBASE NHS ester; block with ethanolamine/BSA as needed.  
- **Characterization** (optional): SEM, XPS, contact angle, QCM‑D to confirm coverage and chemistry.

**C4. Electrical transducer & measurement**  
1. Use a commercial **n‑MOSFET (CD4007UB)** as the transducer.  
2. Place a **20 µL** droplet of test solution on the RFG module; contact with **Ag/AgCl** reference gate.  
3. Measure with semiconductor analyzer (double‑sweep): **V_D = 50 mV**, **V_G = 0–5 V**.  
4. For each condition, repeat **20 cycles** and use quasi‑equilibrium final **ΔV_th** for analysis.  
5. pH sensing typically shows near‑Nernstian **~54 mV/pH** with low drift when interfaces are properly engineered.

---

## 4) Typical Geometries, Thicknesses & Process Windows

**Back‑gated GFET (Au IDE):**  
- **Oxide thickness (t_ox)**: **90 nm** or **300 nm**.  
- **IDE geometry**: gap **S ≈ 200 µm**; finger width **W ≈ 100 µm**.  
- **Graphene printing**: **10 pL** nozzles; **drop spacing 25 µm** (typ.); **5–10 coats**; stage **~60 °C**; **anneal 200–350 °C**.  
- **Data collection temperatures**: typically **30–60 °C**.

**RFG module:**  
- **GO concentration**: **0.24 mg/mL**; **16 mL** per 4" wafer.  
- **Silanes**: **APTMS/HMDS (5% in EtOH, 2 h)**; **120 °C** post‑bake.  
- **Reduction**: **200 °C**, **10 min**, **Ar**.  
- **PBASE**: **10 mg/mL in DMF**, **0–120 min**; example probes as above.

**Printed MoS₂ FET:**  
- Back‑gated on **300 nm SiO₂** (higher |Vg|) or **ion‑gel** top‑gated (≤**2 V**).  
- Example channel sizes: **L = 50 µm**, **W = 150 µm** (illustrative).  
- Interdigitated S/D for gas‑sensing variants: **50 µm** spacing, **200 µm** finger length (illustrative).

> **Ranges** listed reflect the lab’s historical datasets and common literature‑consistent process windows. Always verify with your current ink batch and equipment.

---

---

> **Editor’s notes (non‑destructive additions):**
- Inkjet percolation: fewer coats can leave discontinuities across **S=200 µm** gaps. Increase coats or reduce drop spacing if resistance is too high.
- Anneal atmosphere matters: inert gas reduces oxidation and can raise conductivity; air anneals may roughen films at high T.
- For flexible substrates (PET/PEN), enforce a **≤130 °C** thermal budget and compensate with longer, low‑T bakes.
