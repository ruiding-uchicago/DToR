## 5) Electrical Testing Protocols (Detailed)

**5.1 Back‑gate sweep (GFET)**  
1. Wire S/D to two IDE buses; tie Si substrate as global back gate.  
2. **V_D** = 0.1 V (start); sweep **V_G** across sufficient range to see Dirac point (for 300 nm, ±20–60 V depending on leakage).  
3. Extract **Dirac voltage V_Dirac** (minimum conductance), **μ_FE** from transconductance if desired.  
4. Log **transfer** and **output** curves; maintain a per‑device index (`#1`, `#2`, ...).

**5.2 Solution‑gate sweep (GFET or RFG)**  
1. Add droplet (10–30 µL); place **Ag/AgCl** reference; avoid bubbles.  
2. For RFG: keep the MOSFET dry and isolated; only the rGO pad touches solution.  
3. Sweep **V_G 0–0.5 V** (GFET) or **0–5 V** (RFG transducer), **V_D** = 50–100 mV.  
4. For pH calibration: buffer from pH 2 → 11 in steps; rinse between steps; log **ΔV_th** or **ΔI_D**.  
5. For affinity assays: incubate analyte at graded concentrations; hold fixed gate bias; record time‑traces to extract response and limit of detection.

**5.3 Temperature sweeps**  
- Stabilize stage at **30/35/40/50/55/60 °C**; re‑measure transfer curves. Use consistent dwell times before reading. Pair raw XLS/CSV names with setpoints for traceability.

**5.4 Data logging**  
- Keep per‑device folders (`transfer curves/#3.csv`, `30c.xls`, etc.). Record recipe keys: oxide thickness, IDE S/W, print spacing/coats, anneal temp, measurement temp, gate type.

---

## 6) Surface Chemistry Playbook

- **PBASE → probe attachment**: PBASE forms π–π stacking on graphene/rGO; NHS ester reacts with amine‑terminated probes (aptamers/antibodies). Typical **10 mg/mL in DMF, 1–2 h**.  
- **Blocking**: ethanolamine for residual NHS; BSA/Casein to suppress non‑specific binding.  
- **Heavy metals**: GSH (thiol) for Pb²⁺ capture (**10 mM, 2 h**).  
- **Rinses**: DMF → ethanol → buffer (as compatible). Dry gently under N₂.

---

## 7) QA, Troubleshooting & Notes

**Printing quality**  
- Watch line continuity across **S = 200 µm** gaps; adjust coats if sheet resistance too high.  
- If coffee‑ringing or overspray: increase stage temperature slightly (≤70 °C), or reduce drop spacing / add passes.

**Anneal choices**  
- **200 °C** preserves polymer binders (smoother films) but lower conductivity than **350 °C**. Use inert gas when possible to avoid oxidation.

**Back‑gate leakage**  
- On **90 nm SiO₂**, lower leakage enables smaller |V_G|; **300 nm** may require higher |V_G|. Ensure clean backside contact and check for cracks/pinholes.

**RFG drift/hysteresis**  
- Ensure complete silanization and adequate PBASE adsorption time; use double‑sweep and multiple cycles to reach quasi‑equilibrium.

**Interpret file names**  
- `#(number)` suffixes are **device index** or **transfer curve index**.  
- `xxc.xls` files denote **temperature in °C**.  
- When in doubt, cross‑reference the **Excel design sheet**.

---

---

> **Editor’s notes (non‑destructive additions):**
- Ideal pH response has a theoretical limit of **59.16 mV pH⁻¹ @ 25 °C**; temperature affects the slope (∝ RT/F·ln10). Calibrate at the measurement temperature.
- For affinity assays, fit calibration curves with **4‑parameter logistic (4PL)** or **Langmuir** models; report **LOD/LOQ** with replicate statistics.
- Mitigate drift by performing a pre‑conditioning sequence (e.g., 50 cycles) and using the final cycles for parameter extraction, as already practiced here.
