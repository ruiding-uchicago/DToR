# Final Research Report: Which quantum error-correction architectures most efficiently reach logical error rates of 10⁻⁶, 10⁻⁹, and 10⁻¹⁵ on superconducting and neutral-atom platforms?

**Integrated Research Report**
*Resource-efficient quantum error correction architectures for superconducting and neutral-atom platforms*  

---

## 1. Introduction

Fault-tolerant quantum computing is no longer constrained only by abstract code parameters. The central design question is now architectural: **which error-correction family gives the best trade-off between physical-qubit efficiency, syndrome-extraction feasibility, decoder latency, and platform compatibility** at target logical memory error rates of **10⁻⁶**, **10⁻⁹**, and **10⁻¹⁵**?

This report synthesizes three branch perspectives:

| Branch perspective | Core scope | Role in the final synthesis |
|---|---|---|
| **Surface-code-family branch** | Rotated surface code, XZZX, dynamic/walking/hex variants, folded surface code, and Floquet-style alternatives. | Establishes the most implementation-ready route, especially for nearest-neighbor superconducting chips. |
| **qLDPC-family branch** | Bivariate-bicycle, LDPC-CSS, radial lifted-product, hypergraph-product / La-cross, and quantum Tanner families. | Establishes the strongest qubit-efficiency route and the main migration path for connectivity-rich platforms. |
| **Platform/decoder co-design branch** | Superconducting versus neutral-atom hardware, syndrome extraction, real-time decoding, erasure handling, and QEC-cycle constraints. | Resolves why the “best” architecture differs by hardware platform and target logical error rate. |

The synthesis deliberately separates two different notions of “best.” **Best-supported for deployment** means the architecture has the strongest hardware compatibility and decoder maturity. **Most qubit-efficient** means the architecture uses the fewest physical qubits per logical memory at the same logical-error target, assuming the hardware and decoder can support the required syndrome-extraction protocol.

---

## 2. Synthesized Findings

### 2.1 Cross-Branch Synthesis Matrix

| Theme | Surface-code-family evidence | qLDPC-family evidence | Platform / decoder interpretation |
|---|---|---|---|
| **Implementation readiness** | Rotated/dynamic surface codes fit 2D nearest-neighbor superconducting layouts and have below-threshold experimental lineage. | qLDPC has strong finite-size simulations but fewer end-to-end hardware demonstrations. | Superconducting devices should default to surface-code-family operation unless nonlocal routing and qLDPC decoding are explicit program goals. |
| **Physical-qubit efficiency** | Surface code requires roughly \(2d^2-1\) physical qubits per logical memory patch, so ultra-low targets become qubit-heavy. | Bivariate-bicycle and radial/lifted-product codes offer order-of-magnitude or near-order-of-magnitude savings in finite-size regimes. | qLDPC is the strategic winner when hardware connectivity and decoder integration are available. |
| **Noise-model adaptation** | XZZX can reduce required distance by one to three odd-distance steps under preserved biased noise. | qLDPC performance depends strongly on decoder choice and graph/circuit structure. | Code selection must be conditional on real device noise, not only abstract distance/rate. |
| **Syndrome extraction** | Surface-code checks are local, regular, and repeatedly measurable with mature control schedules. | Bicycle codes use weight-6, depth-7 syndrome circuits; radial codes exploit sliding-window / constant-depth-friendly schedules. | Theoretical qubit savings survive only if syndrome extraction does not introduce routing, idling, leakage, or cycle-time penalties that erase the gain. |
| **Decoder risk** | MWPM, union-find, belief-based, and neural decoders all have credible real-time paths for surface-code-style graphs. | BP+OSD is accurate but expensive; newer qLDPC decoders such as BP+LSD, Relay-BP, and GARI/NMS are promising. | Surface code minimizes decoder risk; qLDPC minimizes quantum hardware count. |
| **Platform fit** | Best matched to superconducting hardware with local couplers and fast repeated measurement. | Best matched to neutral atoms or other architectures with reconfigurable/nonlocal interactions. | Recommendations must be platform-specific: superconducting ≠ neutral atom. |

### 2.2 Architecture KPI Comparison

| Architecture family | Representative strengths | Representative limitations | Best-fit platform regime | Overall ranking role |
|---|---|---|---|---|
| **Rotated surface code** | Strongest hardware evidence, local checks, real-time decoder maturity, predictable scaling. | High physical-qubit overhead at \(10^{-9}\) and especially \(10^{-15}\). | Superconducting nearest-neighbor chips. | **Lowest-risk baseline.** |
| **XZZX surface code** | Same broad surface-code geometry with large savings under preserved noise bias. | Advantage collapses if gate/syndrome schedule destroys bias. | Superconducting devices with strong dephasing bias and bias-preserving gates. | **Best surface-code upgrade under biased noise.** |
| **Dynamic / walking / hex surface code** | Reduces coupler, leakage, reset, or gate-set constraints while keeping surface-code-class logic. | Does not fundamentally lower memory qubit count. | Superconducting or neutral-atom settings where scheduling constraints dominate. | **Hardware-embedding optimization.** |
| **Folded surface code** | Can reduce overhead for certain logical Clifford operations. | Not a memory-overhead breakthrough. | Logical-gate optimization layer. | **Gate-level optimization, not memory winner.** |
| **Hyperbolic/Floquet code** | Shallow low-weight measurements, high rate at modest targets. | Lower thresholds and weaker distance scaling for ultra-low logical errors. | Niche settings needing shallow checks and moderate suppression. | **Special-purpose moderate-target option.** |
| **Bivariate-bicycle / LDPC-CSS** | Best finite-size qubit efficiency in the source report; high-rate block encoding. | Requires degree-5/6 or layered/nonlocal connectivity and dedicated qLDPC decoders. | Neutral atoms; ambitious superconducting roadmaps with nonplanar routing. | **Most qubit-efficient finite-size candidate.** |
| **Radial lifted-product** | Strong qubit savings plus sliding-window / constant-depth-friendly decoding features. | Lower threshold than best bicycle codes; hardware evidence still less mature. | Connectivity-rich hardware where decoder locality matters. | **Second-tier qLDPC workhorse.** |
| **Hypergraph-product / La-cross** | Strong fit to nonlocal resources; can beat surface code when long-range interactions are available. | Standardized target maps are incomplete. | Neutral atoms or long-range/bilayer architectures. | **Connectivity-rich platform candidate.** |
| **Quantum Tanner / good qLDPC** | Excellent asymptotic promise. | Finite-size circuit-level evidence is still sparse. | Longer-term architecture research. | **Asymptotic frontier, not yet practical default.** |

### 2.3 Estimated Memory-Qubit Efficiency at \(p_{phys}\approx10^{-3}\)

| Code family | Target \(10^{-6}\) | Target \(10^{-9}\) | Target \(10^{-15}\) | Interpretation |
|---|---:|---:|---:|---|
| **Rotated surface code** | 161–241 | 449–577 | 1457–1681 | High-confidence, implementation-ready, but qubit-heavy. |
| **XZZX surface code** | ≈97–161 if bias preserved | ≈289–449 if bias preserved | ≈985–1249 if bias preserved | Strong savings only under preserved biased noise. |
| **Dynamic / walking / folded surface variants** | Surface-code class | Surface-code class | Surface-code class | Useful for hardware/circuit logistics rather than memory count. |
| **Bivariate-bicycle / LDPC-CSS** | 22–25 | 25–50 | 60–100, extrapolated | Best finite-size qubit-efficiency candidate if hardware and decoder cooperate. |
| **Radial lifted-product** | 23–40 | 40–80 | ≥80, uncertain | Strong but somewhat less mature qLDPC alternative. |
| **Hypergraph-product / La-cross** | Can beat surface code on long-range hardware | Insufficient standardized data | Insufficient standardized data | Attractive for neutral atoms, but target-specific maps remain incomplete. |
| **Quantum Tanner / good qLDPC** | Promising at 200–250 qubits | Insufficient standardized data | Insufficient standardized data | Asymptotically strong, finite-size evidence still developing. |

### 2.4 Decoder and Syndrome-Extraction Trade-Offs

| Family | Syndrome extraction | Decoder state | Primary risk | Practical consequence |
|---|---|---|---|---|
| **Rotated / standard surface code** | Local weight-4 checks; one ancilla per stabilizer; repeated every cycle. | MWPM, union-find, belief-based, and neural decoders are mature and increasingly real-time. | High qubit count. | Best near-term superconducting choice. |
| **XZZX surface code** | Same footprint class; schedule must preserve bias. | Similar latency class to surface code with correlated/noise-aware decoding. | Bias can be destroyed by gates. | Use only when hardware noise bias is measured and preserved. |
| **Dynamic / walking surface code** | Time-dependent detectors; reset/replacement opportunities. | Matching / correlated / learned decoders plausible. | More complex schedule validation. | Useful when leakage, coupler degree, or reset logistics dominate. |
| **Bivariate-bicycle qLDPC** | Weight-6 checks; depth-7 CNOT cycles; degree-5/6 connectivity in optimized variants. | BP+OSD accurate; BP+LSD, Relay-BP, GARI/NMS promising for hardware. | Connectivity and decoder determinism. | Best qubit saver, but not yet lowest-risk. |
| **Radial lifted-product** | Low-weight checks and sliding-window-friendly schedules. | BP-style and windowed decoding. | Less hardware-grade latency evidence. | Good compromise between qLDPC efficiency and decoder structure. |
| **Neutral-atom qLDPC implementations** | Reconfigurable or shuttled parity extraction. | Erasure-aware and qLDPC decoders must be integrated. | Measurement, atom loss, replacement, and cycle time. | Long-term architectural target once repeated parity extraction is reliable. |

---

## 3. Contradictions & Reconciliations

| Contradiction | Why it appears | Reconciliation |
|---|---|---|
| **“Surface code is obsolete because qLDPC uses far fewer qubits.”** | qLDPC finite-size memory simulations are dramatically more qubit-efficient. | qLDPC is the qubit-efficiency winner, but surface code remains the implementation-readiness winner on superconducting hardware. |
| **“XZZX should always replace the rotated surface code.”** | XZZX shows strong improvements under biased noise. | XZZX is conditional: it is preferred only when the physical noise bias is large and the syndrome-extraction schedule preserves it. |
| **“Neutral atoms should immediately use qLDPC.”** | Neutral atoms provide reconfigurable connectivity and natural erasure information. | qLDPC is the strategic neutral-atom target, but surface/walking codes remain useful while mid-circuit measurement, atom loss, and replacement logistics dominate. |
| **“Decoder latency is solved.”** | Surface-code decoders have credible sub-μs and even ns-class paths. | Decoder latency is largely de-risked for surface-code-style graphs, but qLDPC decoder determinism and tail latency remain active engineering risks. |
| **“Floquet codes are the best high-rate route.”** | Floquet/hyperbolic-Floquet codes offer low-weight, shallow measurement circuits. | They are promising for moderate targets but are not yet compelling for \(10^{-15}\)-class memory because of weaker thresholds/distance scaling. |
| **“Folded surface code reduces the surface-code overhead.”** | Folded constructions improve some logical-operation costs. | They should be classified as logical-gate overhead improvements, not physical-memory overhead reductions. |
| **“qLDPC is impossible on superconducting chips.”** | Standard superconducting chips are planar and nearest-neighbor. | qLDPC is difficult, not impossible; it requires bilayer routing, nonplanar packaging, morphing circuits, or other connectivity changes plus dedicated decoders. |

---

## 4. Unique Perspective Insights

| Perspective | Distinct contribution | What the final synthesis keeps |
|---|---|---|
| **Surface-code-family branch** | Separates rotated, XZZX, dynamic/walking, folded, and Floquet variants by their actual role rather than treating all surface-family changes as qubit savings. | Surface code is the safest superconducting baseline; XZZX is a conditional biased-noise upgrade; dynamic/walking variants optimize hardware embedding; folded/Floquet are special-purpose. |
| **qLDPC-family branch** | Identifies bivariate-bicycle and radial/lifted-product families as the most credible finite-size qubit savers, while keeping Tanner/HGP claims appropriately bounded. | qLDPC is the best path to low qubit counts, especially for neutral atoms, but current evidence is uneven across families and targets. |
| **Platform/decoder branch** | Converts code-family comparisons into platform-specific recommendations by adding decoder latency, syndrome extraction, connectivity, atom loss, and QEC-cycle time. | Architecture selection must be hardware-conditional: superconducting and neutral-atom platforms should not receive the same recommendation. |

---

## 5. Synthesized Answer / Conclusions

### 5.1 Platform-Specific Recommendations

| Platform | Target \(10^{-6}\) | Target \(10^{-9}\) | Target \(10^{-15}\) |
|---|---|---|---|
| **Superconducting** | **Rotated or dynamic surface code.** Use XZZX only if bias-preserving gates and measured noise bias exist. | **Surface code for lowest engineering risk; bivariate-bicycle qLDPC for lowest qubit count** if routing and decoder infrastructure are explicit goals. | **Surface code for evidence-backed execution; qLDPC only as a medium/long-term migration** after connectivity and decoder risks are de-risked. |
| **Neutral atoms** | **Surface/walking surface code if readout/loss/replacement dominate; qLDPC if repeated nonlocal parity extraction is already reliable.** | **qLDPC becomes the preferred architectural target**, especially bicycle, HGP/La-cross, and lifted-product descendants. | **qLDPC is the likely long-term winner**, provided erasure-aware decoding, atom replacement, and faster QEC cycles are solved. |

### 5.2 Overall Ranking by Decision Objective

| Decision objective | Best architecture choice | Rationale |
|---|---|---|
| **Lowest near-term engineering risk on superconducting hardware** | Rotated / dynamic surface code | Strongest hardware compatibility, local checks, and decoder maturity. |
| **Best surface-code-family optimization** | XZZX under preserved biased noise | Same broad footprint with meaningful distance savings only when bias is preserved. |
| **Fewest physical qubits in finite-size memory simulations** | Bivariate-bicycle / LDPC-CSS | Best evidence-backed qLDPC qubit-efficiency point in the source report. |
| **qLDPC compromise with structured decoding** | Radial lifted-product | Useful trade-off between qubit savings and sliding-window / constant-depth-friendly decoding. |
| **Best long-term neutral-atom target** | qLDPC: bicycle + HGP/La-cross + lifted-product descendants | Neutral atoms supply the connectivity and erasure information that qLDPC needs. |
| **Most promising asymptotic frontier** | Quantum Tanner / good qLDPC | Excellent theoretical direction, but not yet the best finite-size practical default. |

### 5.3 Bottom-Line Answer

The most defensible answer is **not one universal code family**, but a split recommendation:

- **For superconducting platforms**, the **rotated/dynamic surface-code family** remains the best-supported architecture for \(10^{-6}\), \(10^{-9}\), and \(10^{-15}\) if the priority is reliable execution on hardware with local couplers and fast repeated measurement. **XZZX** is the preferred variant only when the hardware provides and preserves exploitable noise bias. **qLDPC** should be treated as the qubit-saving migration path, not the lowest-risk immediate default.

- **For neutral-atom platforms**, **qLDPC architectures** are the more compelling long-term answer because the platform’s reconfigurable geometry, shuttling, zoned operation, and erasure information align with the needs of high-rate LDPC codes. Surface/walking surface codes remain useful while measurement, atom loss, and atom replacement are the dominant bottlenecks.

- **For pure qubit efficiency**, the ranking is: **bivariate-bicycle / LDPC-CSS first**, **radial lifted-product second**, then **HGP/La-cross and quantum Tanner/good qLDPC families** as promising but less standardized finite-size options. **For implementation readiness**, the ranking reverses: **surface code first**, then **XZZX/dynamic surface variants**, then **qLDPC**.

---

## 6. References / Future Work

### 6.1 Candidate Inventory

| Category | Candidates |
|---|---|
| **Surface-code family** | Rotated surface code, standard surface code, XZZX surface code, dynamic surface code, walking surface code, hexagonal surface code, folded surface code. |
| **Floquet / dynamical family** | Hyperbolic Floquet code, biased-noise Floquet variants, weight-2 measurement schedules, depth-3 measurement circuits. |
| **qLDPC family** | Bivariate-bicycle code, LDPC-CSS code, radial lifted-product code, hypergraph-product code, La-cross code, quantum Tanner code, good qLDPC families. |
| **Decoder stack** | MWPM, Micro Blossom, union-find, weighted union-find, belief matching, belief-find, neural decoders, BP+OSD, BP+LSD, localized statistics decoding, Relay-BP, GARI, normalized-min-sum. |
| **Superconducting implementation tools** | 2D nearest-neighbor layouts, bilayer routing, nonplanar packaging, degree-5/6 connectivity, morphing circuits, leakage-aware schedules, FPGA/ASIC real-time decoders. |
| **Neutral-atom implementation tools** | Reconfigurable tweezer arrays, shuttling, zoned storage/entangling/readout/reservoir architectures, atom-loss detection, erasure-aware decoding, atom replacement, mid-circuit measurement. |

### 6.2 Priority Experiments and Benchmarks

| Priority | Required benchmark | Why it matters |
|---|---|---|
| **1** | End-to-end repeated-round qLDPC memory on hardware with decoder in the loop. | Converts qLDPC from simulation-dominant evidence to architecture-dominant evidence. |
| **2** | Bias-preserving XZZX demonstrations under full syndrome schedules. | Determines whether XZZX is a real qubit saver or only a model-level advantage. |
| **3** | Neutral-atom qLDPC cycle-time reduction with loss-aware repeated parity extraction. | Tests whether neutral atoms can turn their connectivity advantage into practical logical memory. |
| **4** | Unified target-by-target benchmark for \(10^{-6}\), \(10^{-9}\), and \(10^{-15}\). | Enables fair comparisons across surface, bicycle, radial, HGP, Tanner, and Floquet families. |
| **5** | Worst-case decoder tail-latency reporting, not only average latency. | Fault-tolerant operation needs bounded streaming behavior over many QEC cycles. |
| **6** | Integrated cost model including qubits, ancillas, routing, measurement, decoder, and logical-gate overhead. | Prevents misleading conclusions from qubit count alone. |

**End of Report**.
