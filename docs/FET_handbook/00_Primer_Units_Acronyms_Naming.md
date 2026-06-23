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

---

### Supplementary domain context (added)
- **Debye screening for solution-gated FETs:** In high-ionic-strength buffers (e.g., 1× PBS), the Debye length can drop below 1 nm, strongly screening charges farther from the surface. For affinity sensing, consider reduced ionic strength or surface architectures that bring charges close to the channel.
- **SiO₂ thickness vs. gate range:** Thicker oxides (e.g., 300 nm) typically require larger |Vg| to reach comparable surface potentials than thinner oxides (e.g., 90 nm). Observe leakage limits and avoid dielectric stress.
