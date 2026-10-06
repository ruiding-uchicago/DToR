# Final Research Report: Which quantum error-correction architectures can achieve below-threshold logical operation with the fewest physical qubits while accounting for syndrome extraction, decoder latency, and hardware platform constraints?

**Integrated Research Report**
*Minimal-Qubit Paths to Below-Threshold Quantum Error Correction Across Surface-Code, qLDPC, and Platform-Co-Designed Architectures*  

---

## 1. Introduction  

Fault-tolerant quantum computing requires a quantum error-correction (QEC) architecture that can suppress logical errors below a useful target while remaining physically buildable. The practical question is not simply which code has the highest threshold. A viable architecture must balance **physical-qubit overhead**, **syndrome-extraction depth**, **hardware connectivity**, **classical decoder latency**, and **noise realism**—including leakage, correlated events, erasures, measurement faults, and nonuniform hardware errors.  

Three independent research branches have been examined to answer the central question:

| Branch | Core Concept |
|--------|--------------|
| **Surface-code / surface-like branch** | Rotated / ZXXZ surface codes, heavy‑hex embeddings, Floquet / honeycomb codes, and subsystem surface codes as the most experimentally mature path to below-threshold operation. |
| **qLDPC minimal-qubit branch** | Bivariate‑bicycle, hypergraph‑product / La‑cross, lifted‑product, quantum‑Tanner, and single-shot qLDPC families as the most compelling route to reducing physical qubits per logical qubit. |
| **Decoder / platform co-design branch** | Real-time decoding, latency tails, syndrome scheduling, superconducting vs neutral-atom constraints, and system-level co-design as the deciding layer between theoretical overhead and deployable QEC. |

Each branch contributes a distinct perspective on the same central trade-off: **surface codes are the safest below-threshold route today; bivariate-bicycle qLDPC is the strongest minimal-qubit route; and neutral atoms are the platform where qLDPC may become advantageous earliest once gates, measurement, motion, and real-time decoding are co-optimized**.  

---

## 2. Synthesized Findings  

### 2.1 Common Themes Across Branches  

| Theme | Evidence from Branches |
|-------|------------------------|
| **Below-threshold maturity is not the same as minimal qubit overhead.** | The Surface-code branch shows direct below-threshold experimental evidence for rotated/ZXXZ-style codes, while the qLDPC branch shows that BB codes can use **24–48 physical qubits per logical qubit** at p ≈ 10⁻³ for memory targets inaccessible to similarly small surface-code patches. |
| **The decisive trade-off is three-way, not binary.** | The Decoder / platform branch frames the contest as **qubit count × syndrome extraction × decoder burden**. Surface code wins geometric regularity; qLDPC wins physical-qubit rate; Floquet/subsystem codes lower check weight but complicate timing and decoding. |
| **Finite-length evidence is strongest for rotated surface codes and BB qLDPC.** | Surface code has hardware below-threshold demonstrations; BB qLDPC has explicit finite-length points such as **[[144,12,12]]** and **[[288,12,18]]**. Lifted‑product, Tanner, single-shot, and La‑cross families remain promising but less directly benchmarked at low p_L. |
| **Connectivity determines whether theoretical overhead survives implementation.** | Heavy‑hex layouts make qLDPC routing hard and favor optimized embedded surface codes today; neutral atoms and long-range Rydberg gates directly reduce qLDPC locality penalties. |
| **Decoder average latency is no longer the only bottleneck.** | Surface-code decoders are mature; qLDPC decoders now show sub‑microsecond average feasibility. The remaining question is **tail latency, error floors, and correlated-noise robustness**. |

These convergences imply that the architecture choice must be platform-specific: **surface code for lowest near-term risk, BB qLDPC for lowest qubit overhead when hardware and decoder co-design are available, and neutral-atom qLDPC as the most plausible early route to high-rate QEC if physical error rates and cycle times improve**.

### 2.2 Performance Highlights  

| Category | Representative Architecture / Methodology | Performance Highlights | Key Advantage | Main Limitation |
|----------|--------------------------------------------|-----------------------|---------------|-----------------|
| **Experimentally validated local code** | Rotated / ZXXZ surface code on superconducting hardware | d = 7 memory; **49 data + 48 measure + 4 leakage-removal qubits**; **1.1 µs** cycles; **0.143 % logical error/cycle**; **Λ = 2.14** | Strongest hardware validation; mature decoders; local layout | Physical-qubit overhead remains high for low p_L targets |
| **Low-connectivity superconducting layout** | Heavy‑hex SWAP/flag embedded surface code | **p_th ≈ 0.30 %**; at p = 10⁻³, **≈600 physical qubits/logical** for p_L ≈ 10⁻⁴ | Best near-term path on heavy‑hex devices | Lower threshold headroom than square-grid surface code; large overhead |
| **Low-weight measurement alternative** | Floquet / honeycomb code | Native parity checks can approach **≈2 % threshold**; planar benchmark **≈900 physical qubits** for one-in-a-trillion target with native parity | Low ancilla/check-weight potential | Decomposed parity measurements reduce thresholds to **≈0.17–0.19 %** on heavy‑hex |
| **Best minimal-qubit memory** | Bivariate‑bicycle qLDPC [[144,12,12]] | **288 physical qubits total**, **12 logical**, **24 qubits/logical**; p_L ≈ 2 × 10⁻⁷ with earlier decoding; **≈6.7 × 10⁻⁹** with improved min‑sum ensemble | Best finite-length qubit economy | Requires degree‑6/thickness‑2 connectivity and robust BP-family decoding |
| **Ultra‑low logical memory target** | Bivariate‑bicycle qLDPC [[288,12,18]] | **576 physical qubits total**, **12 logical**, **48 qubits/logical**; p_L ≈ 2 × 10⁻¹² at p = 10⁻³ | Clearest direct qLDPC advantage over surface-code memory | Logical operations and full architecture overhead still require more accounting |
| **Neutral-atom long-term candidate** | HGP / La‑cross / BB qLDPC on Rydberg arrays | qLDPC can overtake surface code when two-qubit error falls below **≈0.1 %**; long-range interactions reduce locality penalty | Natural connectivity for high-rate checks | Current experimental below-threshold evidence is still surface-code based |
| **Real-time decoder stack** | Sparse Blossom / union‑find / Relay‑BP / FPGA min‑sum | Surface-code decoding can be sub‑µs to ns‑scale per round; qLDPC FPGA-class BB decoding can average **<1 µs** with improved methods | Decoder bottleneck is becoming engineering-manageable | Tail latency and rare-event floors remain hard |

### 2.3 Platform-Specific Synthesis  

| Platform / Objective | Best Near-Term Choice | Best Minimal-Qubit Medium-Term Choice | Rationale |
|----------------------|-----------------------|---------------------------------------|-----------|
| **Superconducting square-grid or flexible local layout** | Rotated / ZXXZ surface code | BB qLDPC only if higher-degree / long-range couplers are added | Surface code is already below threshold and decoder-safe; BB qLDPC needs connectivity beyond simple locality. |
| **Superconducting heavy‑hex layout** | Optimized SWAP‑embedded surface code | Possibly subsystem / BB variants only with hardware redesign | Current evidence places heavy‑hex-native subsystem/Floquet options behind optimized surface embedding. |
| **Neutral atoms with long-range Rydberg gates** | Surface code for immediate below-threshold validation | HGP / La‑cross / BB qLDPC | Neutral atoms naturally support nonlocal checks and erasure-aware decoding, making high-rate qLDPC especially attractive once gate and measurement error fall. |
| **Fastest route to experimental below-threshold memory** | Rotated / ZXXZ surface code | Not qLDPC yet | Direct hardware evidence and mature decoding dominate. |
| **Fewest physical qubits per logical memory** | Not surface code | BB qLDPC | BB finite-length resource points dominate surface-code footprints at p ≈ 10⁻³. |
| **Lowest architectural risk for first logical operations** | Surface code | qLDPC later | Logical-gate toolchains, decoders, and scheduling are most mature for local topological codes. |

---

## 3. Contradiction Analysis & Resolution  

| Contradiction | Source(s) | Analysis & Resolution |
|---------------|-----------|-----------------------|
| **“Surface codes are best” vs “qLDPC uses far fewer qubits.”** | Surface-code branch vs qLDPC branch | Both statements are true in different senses. Surface codes are best validated and lowest risk; BB qLDPC is best for physical-qubit economy. The resolution is to separate **experimental maturity** from **minimal-qubit efficiency**. |
| **“Heavy‑hex-native codes should win on heavy‑hex hardware” vs “embedded surface codes perform better.”** | Surface-code branch | Matching the hardware graph is not enough. Heavy‑hex-native subsystem/Floquet schedules can lose threshold headroom; optimized embedded surface codes currently have better quantitative support. |
| **“Floquet codes have high thresholds” vs “Floquet codes are weak on heavy‑hex.”** | Surface-code branch | Native pairwise parity measurement can make Floquet/honeycomb codes attractive; decomposing those measurements into ordinary operations removes the advantage. The key condition is whether parity checks are genuinely native. |
| **“qLDPC decoders are too slow” vs “qLDPC decoders are now sub‑µs.”** | qLDPC branch and Decoder / platform branch | Average latency has improved dramatically through Relay‑BP, min‑sum ensembles, and predecoding. The remaining unresolved issue is not average speed but **tail latency, memory bandwidth, correlated errors, and error floors**. |
| **“Neutral atoms already favor qLDPC” vs “neutral-atom experiments still use surface code.”** | Decoder / platform branch | Neutral atoms are structurally favorable for qLDPC, but current end-to-end demonstrations are still surface-code memories. The resolution is a staged roadmap: surface code now, qLDPC as the long-term high-rate target. |
| **“Asymptotically good qLDPC should dominate” vs “BB has the best current finite-length evidence.”** | qLDPC branch | Asymptotic code quality does not automatically imply better finite-length circuit-level performance. BB codes currently have the strongest directly useful memory points; lifted-product/Tanner/single-shot families need more comparable data. |
| **“Decoder latency must be shorter than the QEC cycle” vs “pipelined decoders can be slower.”** | Decoder / platform branch | The relevant distinction is **throughput versus reaction time**. A decoder can have longer end-to-end latency than the physical cycle if it pipelines and supplies corrections before logical feedforward requires them. |

Overall, the contradictions arise from **different optimization targets**—first demonstration, fewest qubits, easiest routing, simplest decoder, or best long-term architecture. Once the target is specified, the recommendations become consistent.

---

## 4. Unique Perspective Insights  

### 4.1 Surface-Code / Surface-Like Branch  

* **Experiment-first discipline** – This branch anchors the synthesis in hardware-demonstrated below-threshold operation rather than purely asymptotic code claims.  
* **Geometry matters at finite size** – Rotated layouts save ≈25 % qubits relative to unrotated planar layouts at matched logical targets.  
* **Hardware embedding is decisive** – Heavy‑hex results show that a code matching the native graph is not automatically best; routing and threshold headroom must be evaluated together.  
* **Floquet/subsystem value is conditional** – Low‑weight or time-dependent checks matter only if the hardware natively supports them with high fidelity and if the decoder can track the schedule.  

### 4.2 qLDPC Minimal-Qubit Branch  

* **Bivariate‑bicycle codes define the current minimal-qubit frontier** – The [[144,12,12]] and [[288,12,18]] operating points provide the clearest finite-length evidence for large qubit savings.  
* **Decoder progress changes the feasibility picture** – BP-family, min‑sum, and predecoder approaches make qLDPC real-time operation increasingly plausible.  
* **Other qLDPC families remain strategically important** – HGP/La‑cross, lifted-product, Tanner, and single-shot families may become decisive as hardware connectivity and benchmarking improve.  
* **Memory advantage is not the whole architecture** – Full logical computation requires gate implementation, routing, magic-state production, and failure-mode accounting beyond memory p_L.  

### 4.3 Decoder / Platform Co-Design Branch  

* **Platform determines the winner** – Superconducting heavy‑hex layouts favor embedded surface code today; neutral atoms make qLDPC more natural because long-range gates reduce locality penalties.  
* **Throughput and reaction time must be separated** – Pipelined decoding can tolerate longer reaction time than cycle time if throughput keeps up and corrections arrive before logical decisions.  
* **Tail behavior is the next decoder bottleneck** – Average sub‑µs decoding is no longer enough; fault-tolerant systems need controlled worst-case latency and rare-event behavior.  
* **Roadmaps must co-design hardware and decoding** – qLDPC only wins practically if qubit layout, syndrome scheduling, leakage/erasure handling, and decoder hardware are developed together.  

Each branch therefore contributes a separate layer: **surface-code maturity**, **qLDPC qubit economy**, and **system-level co-design**. The final answer depends on which layer is the bottleneck for a given platform.

---

## 5. Comprehensive Conclusion  

The integrated analysis supports a deliberately narrow answer. **The most mature architecture for experimentally demonstrated below-threshold logical operation remains the rotated / ZXXZ surface-code family on superconducting hardware.** It has direct below-threshold evidence, the cleanest real-time decoder stack, and the lowest near-term architectural risk. For near-term superconducting experiments—especially those targeting first logical memories, logical gates, or hardware-calibrated decoder demonstrations—the rotated surface code remains the safest choice.  

At the same time, **the most compelling minimal-qubit architecture is now bivariate‑bicycle qLDPC**. The BB family provides explicit finite-length memory points at p ≈ 10⁻³ where **24–48 physical qubits per logical qubit** can reach p_L values from ≈10⁻⁷ to ≈10⁻¹² depending on code size and decoder. This is a qualitatively different resource regime from surface-code memory. The condition is that hardware must provide the required connectivity and the decoder stack must maintain low tail latency and low error floors under realistic noise.  

The platform-specific recommendation is therefore:

1. **For superconducting qubits today:** choose rotated / ZXXZ surface codes, or optimized embedded surface codes on heavy‑hex layouts. These are the most reliable paths to below-threshold operation and near-term logical experiments.  
2. **For superconducting qubits with redesigned connectivity:** invest in BB qLDPC only if the roadmap includes higher-degree interconnects, long-range couplers, leakage handling, and dedicated BP-family decoder hardware.  
3. **For neutral atoms:** use surface-code demonstrations as the near-term validation path, but prioritize qLDPC for the long-term architecture because reconfigurable tweezer arrays and long-range Rydberg interactions directly address qLDPC connectivity needs.  
4. **For minimal physical qubits per logical memory:** BB qLDPC is the present leader.  
5. **For lowest total implementation risk:** surface code remains the leader.  

The strongest final synthesis is therefore: **surface codes are the safest below-threshold architecture; bivariate‑bicycle qLDPC is the strongest minimal-qubit architecture; and neutral atoms are the platform where qLDPC may win earliest once two-qubit fidelity, measurement/motion cycle time, erasure handling, and real-time decoding mature together**.  

---

## 6. Candidate Inventory  

**Architectures, decoders, platforms, and techniques (de‑duplicated):**  

Rotated planar surface code, ZXXZ surface code, unrotated planar surface code, heavy‑hex SWAP‑embedded surface code, heavy‑hex flag‑based surface code, heavy‑hexagon code, rotated subsystem surface code (RSSC), subsystem toric code, gauge fixing, Floquet honeycomb code, planar honeycomb code, native pairwise parity measurement, decomposed parity measurement, bivariate‑bicycle qLDPC, [[144,12,12]] BB code, [[288,12,18]] BB code, quantum LDPC code, hypergraph‑product code, La‑cross code, lifted‑product code, lift‑connected surface code, quantum‑Tanner code, good qLDPC construction, balanced‑product code, single-shot qLDPC, 3D toric code, 4D toric code, MWPM decoder, Sparse Blossom decoder, union‑find decoder, BP‑OSD decoder, Relay‑BP decoder, graph‑augmented min‑sum decoder, GARI‑NMS decoder, qLDPC predecoder, FPGA decoder, cryogenic ASIC decoder, neural decoder, streaming decoder, windowed decoder, leakage-aware decoder, erasure/loss-aware decoder, superconducting square‑grid processor, superconducting heavy‑hex processor, long‑range superconducting coupler, neutral‑atom tweezer array, Rydberg CZ gate, atom movement/reconfiguration, qubit reuse, teleportation primitive, syndrome extraction, syndrome cadence, code-cycle time, decoder throughput, reaction time, tail latency, calibrated circuit-level noise, leakage noise, correlated noise, erasure information, magic-state routing, logical-memory benchmark, logical-gate benchmark.

---

### Table 1 – Representative QEC Architecture / Decoder Platforms  

| Category | Representative Architecture / Methodology | Performance Highlights | Key Advantage | Main Limitation |
|----------|--------------------------------------------|-----------------------|---------------|-----------------|
| **Experimentally safest QEC memory** | Rotated / ZXXZ surface code | d = 7 below-threshold memory; Λ = 2.14; 0.143 % logical error/cycle; 1.1 µs cycles | Best hardware validation and decoder maturity | Large qubit overhead for very low p_L |
| **Best current heavy‑hex route** | Optimized SWAP‑embedded surface code | p_th ≈ 0.30 %; ≈600 qubits/logical for p_L ≈ 10⁻⁴ at p = 10⁻³ | Compatible with existing heavy‑hex hardware | Threshold headroom and overhead remain limiting |
| **Conditional low-check-weight option** | Floquet / honeycomb code | Native parity threshold ≈2 %; decomposed heavy‑hex threshold ≈0.17–0.19 % | Potentially low ancilla/check burden | Advantage disappears without native parity measurement |
| **Best minimal-qubit memory** | BB qLDPC [[144,12,12]] | 288 physical qubits for 12 logical; 24 qubits/logical; p_L from ≈2 × 10⁻⁷ to ≈6.7 × 10⁻⁹ depending on decoder | Strongest finite-length qubit economy | Requires nonlocal connectivity and advanced decoder hardware |
| **Ultra-low p_L qLDPC memory** | BB qLDPC [[288,12,18]] | 576 physical qubits for 12 logical; 48 qubits/logical; p_L ≈ 2 × 10⁻¹² | Direct low-error qLDPC resource point | Full logical-computation overhead not yet equally mature |
| **Neutral-atom long-term candidate** | HGP / La‑cross / BB qLDPC | qLDPC crossover expected below ≈0.1 % two-qubit error in simulations | Long-range Rydberg gates reduce locality penalty | Still lacks end-to-end qLDPC memory demonstration |
| **Decoder-safe local-code stack** | MWPM / Sparse Blossom / union‑find | Sub‑µs to ns‑scale per-round decoding reported for surface-code settings | Lowest decoder-risk path | Does not remove surface-code qubit overhead |
| **qLDPC real-time stack** | Relay‑BP / min‑sum ensemble / predecoding | FPGA-class sub‑µs average decoding plausible; 273 ns average reported for improved BB decoding | Makes high-rate qLDPC deployable in principle | Tail latency, error floors, and correlated noise remain open |

**End of Report**.
