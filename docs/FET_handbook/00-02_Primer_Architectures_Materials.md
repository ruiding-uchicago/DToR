# Chen Lab FET Sensor Fabrication & Testing Manual (Draft v1.0)

*Prepared for internal knowledge transfer and external collaborators. Audience: researchers new to FET biosensing (no prior microfabrication background required).*  
*Maintainer: Chen Lab. Please keep a change log at the end of this file when editing.*

---

## 0) Quick Primer: Units, Acronyms & Naming Conventions

**Units**  
- **nm** (nanometer) = 10⁻⁹ meters. We use nm for thin films like gate oxides (e.g., **90 nm** or **300 nm** SiO₂).
- **µm** (micrometer) = 10⁻⁶ meters. We use µm for lateral geometry: finger **width** *W*, finger **gap/spacing** *S*, channel **length** *L*.

**Acronyms**  
- **FET**: Field-Effect Transistor  
- **GFET**: Graphene FET (inkjet-printed graphene channel)  
- **IDE**: Interdigitated Electrodes (comb-like source/drain fingers)  
- **RFGFET**: Remote Floating-Gate FET (external sensing pad capacitively coupled to a MOSFET)  
- **Si/SiO₂**: Heavily doped silicon wafer / thermal silicon dioxide (gate dielectric in back-gated devices)  
- **APTMS/HMDS**: Silanes used to functionalize SiO₂ before GO/rGO transfer (APTMS = 3-aminopropyltrimethoxysilane; HMDS = hexamethyldisilazane)  
- **GO/rGO**: Graphene oxide / reduced graphene oxide  
- **PBASE**: 1-pyrenebutyric acid N-hydroxysuccinimide ester (π–π linker for probes on graphene)  
- **Ag/AgCl**: Silver/silver-chloride reference electrode for solution gating

**File/Folder naming (Hyun‑June style, examples)**  
- `IDE (S_200um_W_100um)_(300nm_SiO2)`: IDE geometry with **gap S=200 µm**, **finger width W=100 µm**, on **300 nm SiO₂**.  
- `GFET_IDE_200C_(90nm_SiO2)`: Graphene FET on IDEs, **annealed 200 °C**, built on **90 nm SiO₂**.  
- `2023.01.16 IDE (25um_10c)_350C_G (500um_5c)_350C vs temp_#5`: Date + print/anneal recipe. A common interpretation used by printer operators:  
  - `25um_10c` ⇒ **25 µm drop spacing** and **10 coats/passes** (inkjet).  
  - `G (500um_5c)` ⇒ graphene channel region printed with **500 µm** feature span (context-dependent) and **5 coats**.  
  - `350C` ⇒ post-print anneal at **350 °C**; similarly `200C` means **200 °C**.  
  - `vs temp` ⇒ dataset measured across temperatures; subfiles like `30c.xls` are **30 °C** setpoints.

> **Note:** If any shorthand seems unclear, check the Excel design sheet `example table for Rapti and Hyun June to indicate the FET design_HJ.xlsx` in the Handheld Reader Device folder.

---

## 1) Device Architectures We Use

1. **Back‑gated GFET on Si/SiO₂ with Au IDEs**  
   - Interdigitated Au IDEs on **90 nm** or **300 nm** SiO₂; graphene inkjet‑printed to bridge the IDE gap (S typically **200 µm**, W **100 µm**).  
   - Post-print anneal **200–350 °C** (recipe-dependent).  
   - Used for temperature/pH characterization and general platform development.

2. **Remote Floating‑Gate FET (RFGFET)**  
   - A **separate rGO sensing pad** on functionalized SiO₂ is capacitively coupled to a commercial MOSFET (e.g., CD4007UB).  
   - Surface chemistry (e.g., APTMS/HMDS, PBASE) stabilizes the rGO–solution interface and enables probe immobilization.  
   - Used for robust pH and heavy‑metal/protein assays at low bias with reduced drift/hysteresis.

3. **Printed 2D‑material FET variants (MoS₂/graphene/hBN)**  
   - All‑inkjet or hybrid stacks (graphene S/D + MoS₂ channel; hBN dielectric; optional ion‑gel top gate).  
   - Operate as back‑gated on 300 nm SiO₂ or low‑voltage with printed ion gel top gate.

---

## 2) Materials & Equipment

**Substrates**  
- Heavily doped **Si** with **90 nm** or **300 nm** thermal **SiO₂** (4" wafers for RFG; diced chips for GFET).

**Electrodes & channels**  
- **Au IDEs** (typ. Ti/Au adhesion/metal stack, thickness lab‑standard; fingers W≈100 µm, gaps S≈200 µm).  
- **Graphene ink** for channels (inkjet printable; 10 pL cartridge; see printing section).  
- **MoS₂ ink** (electrochemically intercalated + exfoliated platelets, printable).  
- Optional **hBN ink** (dielectric), **ion‑gel** (for low‑voltage gating).

**Surface treatments & reagents**  
- **O₂ plasma** system, **APTMS** (5% in ethanol), **HMDS** (5% in ethanol), **PBASE** (10 mg/mL in DMF), **GSH** (10 mM in water) or other probes.  
- Solvents: ethanol, DMF, DI water.

**Printing & Processing**  
- Inkjet printer (e.g., Dimatix class): 10 pL cartridges; substrate stage heating up to 60–70 °C.  
- Hotplates/oven/furnace (200–350 °C for post‑bakes/anneals; inert gas available).  
- Microscopes (optical), profilometer/AFM (optional), Raman (optional).

**Electrical test**  
- Semiconductor parameter analyzer (e.g., Keithley 4200A), probe station, **Ag/AgCl** reference electrode for solution gating.  
- Handheld reader prototype (group device) for field tests.

**Safety**  
- Follow CHO/departmental SOPs for plasma, silanes, DMF, hot surfaces, and nanomaterials. Work in fume hood for silanization/DMF steps. Wear appropriate PPE.

---

---

> **Editor’s notes (non‑destructive additions):**
- Back‑gate oxide capacitance rough guide: **300 nm SiO₂ ≈ 11.5 nF cm⁻²**, **90 nm SiO₂ ≈ 38 nF cm⁻²** (εr≈3.9). Useful when converting transconductance to mobility or estimating Vg ranges.
- For solution‑gated tests, keep ionic strength modest (e.g., **1–10 mM**) to balance Debye length vs. screening. Rinse thoroughly between matrices to minimize memory effects.
- Graphene inks often contain binders; expect conductivity to improve with post‑print anneal (see process windows).
