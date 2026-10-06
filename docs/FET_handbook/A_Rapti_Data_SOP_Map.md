# Appendix A — Rapti data mapping & SOP variations (AJP/CNC on ITO)

## A1. Scope
This appendix translates Rapti’s folder/filename conventions into experimental metadata and connects them to the fabrication/measurement steps in the main SOP. It covers: AJP-printed CNC–graphene devices on ITO (glass/PET/PEN), CVD-graphene controls, Hoagland nutrient experiments (P1/P2/P3), pH and anion selectivity sets, stabilization runs, and the handheld-reader real‑time logs.

> **Key takeaway:** most files encode (i) substrate, (ii) graphene source/process, (iii) concentration series for analyte, and (iv) the gate–drain sweep macro and repeat counts. Use this appendix as a “Rosetta stone” to read those names as structured parameters you can enter into ELN or the structured spreadsheet template from the main manual.

---

## A2. Folder grammar & filename decoder
The examples in the tree can be parsed with this grammar (tokens in **bold** are the parts you should capture in a metadata sheet):

**Top-level cohort** → `AJP‑CNC gr devices/` | `CNC graphene/` | `CVD graphene/` | `phosphate detection/` | `phosphate detection on different substrates/` | `pH sensitivity of different substrates/` | `stabilization data/` | `Thresold voltage/` | `Raman/` | `Handheld/`

**Device label** → `Device <#>[_<context>]`
- *Context* examples: `Janan 2L`, `AJP CNC my sample 2`, `ITO PET`, `EC`, etc.

**Substrate** → `ITO_glass` | `ITO glass` | `ITO_PET` | `ITO_PEN` (aka PEN) | `Si_SiO2`

**Graphene source/process** →
- `AJP CNC graphene <1L|2L>`: **A**erosol **J**et **P**rinting of **CNC‑stabilized graphene ink**; trailing `1L`/`2L` = **number of printed passes/layers**.
- `EC graphene`: **electrochemistry configuration** (device used in 3‑electrode measurement context with a reference electrode; see A6) rather than the printing method.
- `CVD graphene`: CVD sheet transfer used as **control** devices.

**Measurement macro** → strings containing `vg id <N> cycles` or `DI water vg id <N> cycles`
- `vg` = **gate voltage**, `id` = **drain current**; `<N> cycles` = **number of Vg sweeps** executed for averaging/stabilization.
- `repeat`, `repeat <m>` = replicate datasets under the same macro.

**Analyte & concentration** → tokens like `1 pg_mL …`, `100 ng per mL …`, `1 mg_mL …`
- Units follow standard SI prefixes (**pg, ng, µg, mg** per **mL**). These are **solution concentrations** used during sensing (e.g., phosphate).

**Buffers/solutions** → `DI water`, `hepes buffer`, `Hoagland`, `P 1`/`P 2`/`P 3` series (see A7).

**Processed data** → folders/files prefixed with `fitdata_…` contain **derived quantities** (e.g., ΔVth, slopes, R²), typically computed from the raw `vg–id` cycles.

**Real-time logs & projects** → `.txt` time‑stamped strips (handheld), `.opju` Origin project files aggregating traces/plots.

**Raman** → `gr ink sample anneal at <T>c.txt` → Raman spectra for graphene ink at **no anneal / 200 °C / 400 °C / 600 °C**, used to justify anneal windows.

> **Tip:** When you see `Janan 1L/2L` in a device label, treat `Janan` as the sample owner/origin tag and `1L/2L` as the **AJP pass count**.

---

## A3. What each cohort is for
- **AJP‑CNC gr devices/**: Per‑device folders combining AJP passes (1L/2L), substrates (ITO glass/PET/PEN), and handheld/Origin results—including copper reference‑electrode runs. Use to benchmark **printing parameters vs. substrate**.
- **CNC graphene/**: Systematic **calibration series** in DI/buffer (pH 2–12) and phosphate titrations from **pg/mL → mg/mL**, plus **selectivity** vs. common anions (Cl⁻, HCO₃⁻, OH⁻, SO₄²⁻). Includes `fitdata_…` post‑processing.
- **CVD graphene/**: CVD‑graphene controls measured with the same `vg–id` macros to provide **baseline** vs. printed graphene.
- **Hoagland sol/** and **Device 8_CNC/** sub‑trees: Phosphate sensitivity in **Hoagland nutrient matrices** (see A7) with P1/P2 sweeps and DI controls; includes fitdata.
- **pH sensitivity of different substrates/**: Cross‑substrate pH response consistency (ITO‑glass vs ITO‑PET vs ITO‑PEN) at 80–100 cycles.
- **phosphate detection/** and **…on different substrates/**: Cross‑device cross‑substrate phosphate titrations with harmonized cycles.
- **stabilization data/**: Long sequences in DI at 20/50/100 cycles to quantify drift/hysteresis vs. cycle count.
- **Thresold voltage/**: Centralized **Vth extraction** “fitdata” mirrored per device and per substrate (spelling as in folders).
- **Handheld/**: Origin projects for the **reader** (real‑time response) and multi‑anion response visualizations.

---

## A4. Abbreviation & unit map (for non‑specialists)
- **AJP** = Aerosol Jet Printing.
- **CNC graphene** = graphene ink stabilized with **cellulose nanocrystals** (binder/dispersant → robust prints).
- **EC graphene** = graphene device measured in **electrochemistry** setup (3‑electrode) using a reference (e.g., Cu); not necessarily a different graphene type.
- **ITO** = Indium Tin Oxide **electrodes**; substrates list the **carrier**: glass, PET, or PEN (flexible).
- **Si/SiO₂** = silicon wafer with thermal oxide; oxide thickness is typically encoded elsewhere (see main SOP).
- **vg**/**id** = gate voltage / drain current. `vg id 50 cycles` = 50 Vg sweeps per dataset.
- **L** in `1L, 2L` = number of **printed layers/passes**.
- **pg/ng/µg/mg per mL** = solution concentration units used during sensing tests.
- **fitdata** = processed results (ΔVth, slopes, LODs), derived from raw sweeps.

---

## A5. SOP specifics inferred for the AJP/CNC on ITO family
Use these with the fabrication/testing sections of the main manual; values below are **validated by file cohorts** and **Raman anneal notes** here, not by external assumptions.

### A5.1 Substrate preparation
- **ITO‑glass**: solvent clean (IPA/H₂O), N₂ dry, optional O₂ plasma (gentle: ≤60 s) to boost wettability pre‑AJP.
- **ITO‑PET / ITO‑PEN**: as above **without** high‑temp steps; keep thermal budget ≤130 °C unless the PET/PEN spec allows higher. Use longer, lower‑T bakes to drive off solvent.

### A5.2 AJP printing & layer count
- `1L` vs `2L` determines **sheet resistance and continuity**. Track layer count in the sample label (already present in folder names like `Janan 1L/2L`).
- Keep stage temp warm (40–80 °C) to aid solvent flash‑off; record atomizer/sheath flows in the ELN (not encoded in filenames).

### A5.3 Post‑print anneal (from Raman cohort)
- You have Raman runs at **no anneal**, **200 °C**, **400 °C**, **600 °C**. Use these to justify your chosen anneal for conductivity vs. substrate limits:
  - **ITO‑glass**: 200–350 °C typical; evaluate 400 °C sparingly (watch ITO sheet‑R changes).
  - **ITO‑PET/PEN**: ≤120–130 °C (polymer constraint)—prefer longer time rather than higher T.

### A5.4 Contacts & measurement setup
- Many AJP/CNC device folders include `.opju` with **“Cu ref electrode”** → copper used as reference during **solution‑gated** tests on handheld. Maintain consistent reference placement and droplet volume (see main SOP droplet‑gating guidance).
- Raw logs: `real time ... .txt` are strip‑chart outputs synchronized with the handheld reader.

### A5.5 Gate‑drain sweep macros & stability
- Macros named `vg id <N> cycles` implement **N forward‑back Vg sweeps**. Use **50 cycles** for standard sensitivity and **100 cycles** when quantifying drift or stabilizing the Dirac point.
- `repeat` files are biological/physical replicates or immediate repeats for statistics.

---

## A6. How to read specific device folders (examples)
- `AJP‑CNC gr devices/Device 1_Janan 2L/…xlsx` → AJP‑printed **2‑layer** CNC‑graphene on **ITO‑glass**; Device owner tag `Janan`; measured on handheld with Cu reference; 
  raw: time‑stamped `.txt`, processed: `.xlsx` with ΔVth/Id metrics; visualization in `.opju`.
- `Device 3_ITO PET/EC graphene on ITO 19_11_2024.xlsx` → graphene **on ITO‑PET** measured in **electrochemistry (EC)** configuration on **2024‑11‑19**; same macro naming; compare vs. glass.
- `Device 7_Janan 1L/…1L…xlsx` → identical to Device 1 but **1‑layer** print; use as direct **1L vs 2L** comparison under same substrate and macro.

---

## A7. Hoagland, buffers & selectivity experiments
- **Hoagland solution** experiments appear under `Hoagland sol/` and `Device 8_CNC/1_hoagland/`.
  - `P 1`, `P 2` (and `P 3` where present) denote **phosphate‑bearing stock parts** of Hoagland; the filenames sweep **0–100 %** to modulate phosphate concentration and ionic strength.
  - Use `…DI water…` files in the same folder as **matrix blanks**.
- **Buffer sets** under `20240508_CNC buffer/` use **HEPES** to decouple pH effects from phosphate.
- **Selectivity** (`20240509_CNC selectivity/`) compares responses to **Cl⁻, HCO₃⁻, OH⁻, SO₄²⁻, PO₄³⁻** across pg/ng/µg/mg per mL.

> **Analysis tip:** For each matrix (DI, HEPES, Hoagland), keep separate calibration curves (ΔVth or transconductance vs. log concentration) and report LOD/LOQ per matrix, not globally.

---

## A8. Threshold‑voltage extraction & reporting
- The `Thresold voltage/` and `…/Thresold voltage data_1/` trees consolidate **Vth fitdata** computed from the cycle sets. When compiling a manuscript, prefer these central `fitdata_…` sheets to ad‑hoc per‑device spreadsheets.
- Document: **(device ID, substrate, graphene type, cycles, analyte/matrix, concentration, mean ΔVth, σ, N repeats)**.

---

## A9. Stabilization experiments
- Long DI‑water sequences at **20/50/80/100 cycles** (devices 1–8) are designed to quantify **drift over time** and optimum **cycle budget** before analyte additions.
- Recommended practice:
  1) run a 50‑cycle pre‑condition, 2) track Dirac‑point position over the last 10 cycles, 3) proceed to analyte titration only if drift ≤ **2 mV/cycle** (or lab‑approved threshold).

---

## A10. Suggested master‑manifest columns
Use these columns to convert Rapti’s tree to a tidy dataset (copy/paste this header row into a sheet):

`device_id, owner_tag, process (AJP/CNC | CVD | EC), layer_passes (L), substrate (ITO-glass | ITO-PET | ITO-PEN | Si/SiO2), date(YYYY-MM-DD), matrix (DI | HEPES | Hoagland | other), reference_electrode (Cu | Ag/AgCl | other), analyte (PO4 | Cl | HCO3 | OH | SO4 | pH), concentration_value, concentration_unit, vg_sweep_cycles, repeat_index, file_path, fitdata_path`

Populate `reference_electrode` from `.opju` titles (e.g., “Cu ref electrode”).

---

## A11. Open items to confirm with Rapti (flagged in filenames)
1) **“EC graphene”** → treated here as **electrochemistry setup**; confirm if any **electrochemical reduction** or special surface step was also applied.
2) **AJP printing parameters** not encoded in filenames (nozzle, atomizer/sheath flows, stage temperature) → pull from ELN or add to a run‑sheet for future experiments.
3) **Cu reference electrode** details (geometry, placement, junction leakage) for handheld → standardize in the measurement checklist.
4) **P1/P2/P3** exact stock compositions & pH targets in Hoagland → add to buffer‑prep appendix for reproducibility.

---

## A12. Where this plugs into the main SOP
- **Fabrication**: use A5.1–A5.3 to choose substrate and anneal within the thermal budget inferred from Raman files; layer passes from the device label.
- **Testing**: use A5.4–A5.5 to select cycles (50 vs 100), reference electrode, and droplet matrix. Map concentration series directly from filenames when building calibration.
- **Reporting**: pull ΔVth and slopes from the `fitdata_…` files; follow the LOD/LOQ and repeat‑handling guidance in the main manual.

_End of Appendix A._

---

> **Editor’s notes (non‑destructive additions):**
- Consider maintaining a **master manifest** (CSV/Sheet) using the suggested columns for rapid ELN population and reproducible analysis.
- When possible, mirror `fitdata_…` summaries in a central location to avoid file drift across device folders.
- Flag open items (A11) in the ELN with owners and due dates to close gaps on EC setup details and Hoagland compositions.
