# Final Research Report: Which architectural and pre-training strategies—including state-space models, long-context transformers, and hybrid masked/autoregressive objectives—enable foundation models for DNA, RNA, and protein sequences to most reliably predict regulatory function, variant effects, and zero-shot biological properties at genome scale?

**Integrated Research Report**  
*Foundation Model Architectures and Pretraining Strategies for Genome-Scale DNA, RNA, and Protein Prediction*  

---

## 1. Introduction  

Foundation models for biological sequences now span three different but related modalities: **DNA**, **RNA**, and **proteins**. The central question is not simply whether long-context transformers, state-space models, or hybrid masked/autoregressive objectives are “best” in the abstract. The decisive issue is whether a model can reliably predict the relevant biological property: distal regulatory function and noncoding variant effects for DNA, splicing and RNA structure/function for RNA, and zero-shot fitness or pathogenicity for proteins.  

Three independent research branches were examined to answer the question in a structured way:

| Branch | Core Concept |
|--------|--------------|
| **a3f91c7d2e60b845** | DNA regulatory sequence-to-function models and million-token genome backbones, including Enformer/Borzoi, DNALONGBENCH, GPN-MSA, HyenaDNA, Caduceus, Evo 2, and JanusDNA. |
| **6e42b9a81d0f3c57** | RNA-specific foundation models, splicing baselines, and biologically informed objectives, including SpliceAI, RiNALMo, RNAErnie, RNA-FM/RNA-MSM, WT-LLR scoring, and RNA-specific benchmark gaps. |
| **c8d54f0e9a13b27f** | Protein zero-shot variant-effect models, evolutionary scoring, and objective selection, including ESM-family models, MSA Transformer, Tranception with retrieval, AlphaMissense-style systems, and ProteinGym-style evaluation. |

The present report integrates these branches into a single decision framework. It synthesizes the strongest convergent evidence, resolves contradictions, identifies modality-specific design rules, and produces a candidate inventory of architectures, objectives, benchmarks, and practical implementation strategies.

---

## 2. Synthesized Findings  

### 2.1 Common Themes Across Branches  

| Theme | Evidence from Branches |
|-------|------------------------|
| **Task-conditioned architecture selection** | DNA regulatory prediction is best served by supervised conv/patching + long-context attention or attention-SSM sequence-to-function models; RNA needs RNA-specific masked encoders plus structure/motif priors; proteins are strongest with masked or MSA/evolution-aware models for zero-shot variant effects. |
| **Long context is necessary but not sufficient** | HyenaDNA, Evo 2, and JanusDNA show that 1 Mb context is technically feasible, but DNALONGBENCH-style tasks still favor expert supervised DNA models; RNA also remains constrained by transcript-scale context limits. |
| **Biological priors outperform generic scaling when available** | Multispecies alignments, MSAs, motif-aware masking, secondary-structure objectives, direct sequence-to-function supervision, and task-adapted heads often provide more reliable gains than simply increasing parameters or token count. |
| **Objective choice must follow the biological use-case** | MLM is strongest for understanding and single-mutant scoring; AR is most useful for generation, indels, and combinatorial edits; RTD/FIM/span objectives are promising hybrid bridges but need strict benchmarking. |
| **Evaluation design determines whether claims are credible** | DNA requires chromosome/regulatory-neighborhood splits, RNA requires family-wise splits and scoring-rule control, and proteins require homology-cluster splits, DMS/clinical benchmarks, and calibration metrics. |

### 2.2 Modality-Specific Performance Highlights  

| Category | Representative Model / Methodology | Performance Highlights | Key Advantage | Main Limitation |
|----------|------------------------------------|-----------------------|---------------|-----------------|
| **DNA regulatory function** | Enformer, Borzoi, ChromBPNet-style sequence-to-function models | Enformer improves CAGE correlation over Basenji2 from 0.81 to 0.85; Borzoi improves fine-mapped eQTL AUROC from 0.747 to 0.794 and uses 524 kb windows with 7,611 tracks | Best validated for expression, enhancer, eQTL, and transcript-processing prediction | Task-specific supervision required; expensive long-window training |
| **Ultra-long DNA modeling** | HyenaDNA, Caduceus, Evo 2, JanusDNA | 100 kb–1 Mb contexts; HyenaDNA reports up to 160× faster long-context training; Evo 2 uses 1 Mb context and trillion-token curricula | Makes single-nucleotide long-context pretraining and generation tractable | Long context alone still trails expert models on distal regulation |
| **RNA splicing** | SpliceAI, OpenSpliceAI | Up to 10,000 nt context; 75% of predicted cryptic splice variants validated on RNA-seq in original report | Strong supervised baseline for splice-disrupting variants | Not a general-purpose RNA FM; must be paired with broader RNA models for other tasks |
| **RNA structure/function transfer** | RiNALMo, RNAErnie, RNA-FM, RNA-MSM | RiNALMo: 650M parameters, 36M ncRNAs, MLM + RoPE; RNAErnie: ~23M RNAcentral sequences with base/subsequence/motif masking | RNA-specific corpora and objectives outperform DNA LMs | Context often limited to ~1k–2k tokens; zero-shot RNA fitness remains weak |
| **Protein zero-shot variant effects** | ESM-1v, ESM1b, MSA Transformer | ESM-1v test absolute Spearman ρ ≈0.482; MSA Transformer ≈0.524; ESM1b scores ~450M human missense variants | Strongest mature zero-shot modality; good benchmark culture | Clinical calibration and indel/combinatorial landscapes remain harder |
| **Protein generation / indels** | Tranception with retrieval, ProtMamba, ProGen2, ProtT5 | Tranception with retrieval reaches average Spearman ≈0.451 on ProteinGym substitutions and ≈0.463 on indels | Stronger when generation, shallow alignments, indels, or multi-mutants matter | Less universally dominant for natural single substitutions than masked/MSA models |

### 2.3 Cross-Cutting Architecture Rules  

- **For DNA regulatory genomics:** choose **local convolutional/patching stems + long-context integration + relative positional bias + supervised multitask genomic-track heads**. Use SSM/Hyena/Mamba primarily to extend context, then validate against Enformer/Borzoi/ChromBPNet-style baselines.  
- **For RNA:** choose **RNA-specific masked encoders** with motif-, subsequence-, structure-, type-, and evolution-aware objectives. Keep **SpliceAI/OpenSpliceAI** as mandatory splicing baselines.  
- **For proteins:** choose **masked transformers or MSA/evolution-aware models** for zero-shot single-mutant scoring. Add AR/retrieval/FIM components when the task includes generation, indels, or combinatorial design.  
- **For broad biological FM development:** maintain both a **zero-shot likelihood-based scoring path** and a **lightweight supervised head** for label-rich tasks; this preserves interpretability while capturing task-specific signal.  

---

## 3. Contradiction Analysis & Resolution  

| Contradiction | Source(s) | Analysis & Resolution |
|---------------|-----------|-----------------------|
| **“Million-token context solves genome-scale biology” vs. “expert models still win on regulation”** | DNA branch | The contradiction resolves by separating **context capacity** from **biological supervision**. SSM/Hyena/Mamba models solve length scaling, but regulatory prediction still needs CAGE/RNA-seq/chromatin supervision, relative positional effects, and leakage-resistant benchmarks. |
| **“MLM is the best objective” vs. “AR is necessary for generation”** | RNA and protein branches | MLM is the safest understanding objective for bidirectional biological interpretation and single-mutant scoring. AR becomes valuable for generation, indels, multi-mutants, and sequence design. Hybrid FIM/RTD/span objectives should be treated as promising but not yet universally proven. |
| **“Universal sequence FMs can cover DNA/RNA/protein” vs. “modality-specific models dominate”** | All branches | DNA, RNA, and proteins encode different biological constraints. DNA regulation depends on distal context and cell state; RNA depends on motif/structure/class priors; proteins carry strong evolutionary covariation. Universal pretraining may help, but task-specific baselines remain necessary. |
| **“Single-sequence models are easier and sufficient” vs. “alignment-aware models score variants better”** | DNA and protein branches | Single-sequence models are operationally easier, but GPN-MSA and MSA Transformer show that evolutionary alignments add strong constraint when available. The practical rule is to use alignment-aware scoring when homologs or multispecies alignments are reliable, and retrieval/single-sequence models when alignments are shallow. |
| **“Scaling parameter count guarantees better predictions” vs. “data diversity and leakage control dominate”** | All branches | Bigger models help only when training data, objectives, and evaluation are well designed. Multispecies diversity, nonredundant corpora, homology/family/chromosome splits, and calibration can matter more than raw parameter count. |
| **“RNA zero-shot prediction is now mature” vs. “RNA metrics remain modest”** | RNA branch | RNA-specialized models clearly beat DNA LMs, but absolute zero-shot mutation-effect values remain weak compared with proteins. RNA should be treated as promising but not yet protein-like in zero-shot reliability. |

Overall, most apparent conflicts arise because different papers optimize different biological targets. A reliable model-selection rule must first identify the target task, then choose the architecture, objective, benchmark, and scoring rule appropriate to that task.

---

## 4. Unique Perspective Insights  

### 4.1 Branch a3f91c7d2e60b845 – DNA Regulatory Sequence-to-Function Models  

* **Core insight:** DNA regulatory prediction is still led by **supervised sequence-to-function learning**, especially Enformer/Borzoi-style designs that combine motif extraction, long-range integration, relative positional encoding, and thousands of genomic-track targets.  
* **Distinct value:** This branch prevents overclaiming from long-context DNA FMs by showing that 1 Mb context must be paired with biology-matched supervision and DNALONGBENCH-style evaluation.  
* **Practical rule:** For regulatory function, start with a two-stage workflow: pretrain on diverse genomes, then train supervised heads on RNA-seq/CAGE/accessibility/chromatin tracks using strict chromosome or regulatory-neighborhood splits.  

### 4.2 Branch 6e42b9a81d0f3c57 – RNA-Specific Foundation Modeling  

* **Core insight:** RNA requires **RNA-specific corpora and objectives**. Splicing, secondary structure, family classification, translation, and mutation effects should not be collapsed into one score.  
* **Distinct value:** This branch emphasizes that **SpliceAI remains a required supervised baseline** for splice-variant interpretation, while RiNALMo/RNAErnie/RNA-MSM-style models are better suited for broad RNA transfer and zero-shot exploration.  
* **Practical rule:** Use RNA-specific masked encoders with motif/structure/evolution priors, apply WT-LLR for mutation scoring, and evaluate with family-wise splits and separate panels for splicing, structure, translation, and fitness.  

### 4.3 Branch c8d54f0e9a13b27f – Protein Zero-Shot and Evolution-Aware Models  

* **Core insight:** Proteins provide the strongest evidence that self-supervised sequence models can predict biological properties zero-shot. Masked transformers and MSA-aware models are the safest defaults for single-substitution variant effects.  
* **Distinct value:** This branch supplies the most mature benchmark template—ProteinGym, DMS assays, clinical variant sets, homology-aware splits, and calibration—that DNA and RNA evaluations should emulate.  
* **Practical rule:** Use ESM/MSA-style models for zero-shot single mutants, AlphaMissense-style task-adapted multimodal systems for clinical pathogenicity, and Tranception/ProtMamba/AR-retrieval hybrids for generation, indels, and combinatorial design.  

---

## 5. Comprehensive Conclusion  

The integrated conclusion is deliberately task-conditioned: **there is no single universally best architecture or pretraining objective across DNA, RNA, and proteins**. The most reliable strategy is to match the biological task to the architecture, objective, and evaluation protocol.

1. **For DNA regulatory function and noncoding variant effects with labels available, the best current choice is supervised sequence-to-function modeling.** Conv/patching stems, long-context attention or attention-SSM modules, relative positional encoding, and multitask heads trained on CAGE/RNA-seq/accessibility/chromatin tracks remain more reliable than pure DNA LMs. Long-context SSM/Hyena/Mamba models are important, but they should be used as scalable backbones—not as evidence that supervision is unnecessary.  

2. **For genome-scale unsupervised DNA modeling or generation, SSM/Hyena/Mamba and hybrid attention-SSM backbones are the most promising route.** Their role is strongest when the key bottleneck is 100 kb–1 Mb context, single-nucleotide resolution, generative modeling, or broad phylogenetic pretraining.  

3. **For RNA, the best general direction is RNA-specific masked modeling with biological priors, while SpliceAI-class models remain essential for splicing.** RiNALMo/RNAErnie/RNA-MSM-style approaches are promising for transfer, but zero-shot RNA fitness prediction remains much less mature than protein zero-shot prediction.  

4. **For protein zero-shot fitness and variant effects, masked transformers and MSA/evolution-aware models are the most dependable.** ESM-family and MSA Transformer-style systems provide the strongest single-mutant evidence. Retrieval-augmented AR and hybrid objectives become especially useful for indels, shallow alignments, sequence generation, and multi-mutant landscapes.  

5. **For pretraining objectives, MLM is the best default for understanding, AR is best for generation and edit-rich landscapes, and hybrid RTD/FIM/span objectives are promising but still require rigorous validation.** Biological priors—MSA, multispecies alignment, motif masking, secondary structure, direct sequence-to-function supervision—are often more decisive than generic scale.  

6. **For evaluation, split design and scoring rules are part of the model.** DNA requires chromosome/regulatory-neighborhood splits; RNA requires family-wise splits and WT-LLR scoring controls; proteins require homology-cluster splits, DMS/clinical benchmarks, and calibration. Without these controls, apparent gains can reflect leakage or scoring artifacts rather than true biological understanding.  

In summary, the strongest practical answer is: **use supervised long-context sequence-to-function models for DNA regulatory prediction, RNA-specific masked models plus SpliceAI baselines for RNA, and masked/MSA/evolution-aware models for protein zero-shot variant effects; deploy SSM/Hyena/Mamba or hybrid attention-SSM models when ultra-long context or generation is the bottleneck, and select MLM, AR, or hybrid objectives according to whether the task is understanding, design, or edit-rich variant scoring.**

---

## 6. Candidate Inventory  

Enformer, Borzoi, Basenji2, BPNet, ChromBPNet, DeepSEA, Nucleotide Transformer, DNABERT-2, Caduceus-Ph, HyenaDNA, HybriDNA, Evo 2, StripedHyena-2, JanusDNA, GROVER, GPN-MSA, GUE, DNALONGBENCH, DART-eval, CAGE prediction, RNA-seq multitask heads, chromatin accessibility tracks, eQTL discrimination, enhancer–target prediction, TAD / 3D genome tasks, relative positional basis functions, RoPE, reverse-complement equivariance, convolutional stems, patching stems, dense attention on compressed tokens, SSM/Hyena/Mamba kernels, attention-SSM hybrids, SpliceAI, OpenSpliceAI, RiNALMo, RNAErnie, RNA-FM, RNA-MSM, UTR-LM, RNAElectra, RNAGym, BEACON-like panels, RNAcentral, Rfam, RfamSample, WT log-likelihood ratio, pseudo-likelihood difference scoring, motif-aware masking, subsequence masking, type-guided fine-tuning, secondary-structure objectives, minimum-free-energy objectives, ESM-1v, ESM1b, ESM-family masked transformers, MSA Transformer, AlphaMissense-style predictors, Tranception, Tranception with retrieval, ProtMamba, ProGen2, ProtT5, GENERator, ProteinGym, MaveDB, ClinVar, HGMD, UniProt, ProteinNet, FLIP, TAPE, DMS assays, clinical variant datasets, masked-token likelihood ratios, MSA-based scoring, retrieval augmentation, autoregressive modeling, fill-in-the-middle training, span corruption, replaced-token detection, calibration metrics, ECE, Brier score, Spearman ranking, AUROC/AUPRC, homology-cluster splits, chromosome-wise splits, family-wise splits, regulatory-neighborhood leakage control, context-length ablation, objective ablation, data-diversity ablation.

---

### Table 1 – Representative Model / Objective / Benchmark Platforms  

| Category | Representative Material / Methodology | Performance Highlights | Key Advantage | Main Limitation |
|----------|----------------------------------------|-----------------------|---------------|-----------------|
| **DNA supervised regulatory model** | Enformer / Borzoi-style conv-attention sequence-to-function model | Enformer CAGE correlation improvement 0.81 → 0.85; Borzoi eQTL AUROC 0.747 → 0.794; 524 kb windows and 7,611 tracks for Borzoi | Best validated for regulatory genomics, expression, eQTL, enhancer, and RNA-processing outputs | High compute cost; requires rich labeled genomic tracks |
| **DNA ultra-long-context backbone** | HyenaDNA / Evo 2 / JanusDNA | 1 Mb-scale context; Evo 2 uses 1 Mb window and trillion-token curricula; JanusDNA reports 1 Mb on one 80 GB GPU | Scales to genome-length context and generation | Still needs task-specific supervision for distal regulation |
| **RNA splicing baseline** | SpliceAI / OpenSpliceAI | Up to 10,000 nt context; strong cryptic splice-variant validation | Practical clinical splice-variant baseline | Narrower than general RNA FM; not sufficient for all RNA tasks |
| **RNA foundation model** | RiNALMo / RNAErnie / RNA-MSM | RiNALMo 650M parameters on 36M ncRNAs; RNAErnie ~23M RNAcentral sequences with motif/subsequence masking | RNA-specific objectives and corpora improve transfer | Long transcript context and zero-shot fitness remain weak |
| **Protein zero-shot model** | ESM-1v / ESM1b / MSA Transformer | ESM-1v test absolute Spearman ρ ≈0.482; MSA Transformer ≈0.524; ESM1b scaled to ~450M human missense variants | Strongest zero-shot biological property evidence | Calibration, clinical thresholds, indels, and epistasis remain difficult |
| **Protein generative / indel model** | Tranception with retrieval / ProtMamba / ProGen2 | Tranception with retrieval ≈0.451 ProteinGym substitutions and ≈0.463 indel benchmark | Strong for generation, shallow alignments, indels, and multi-mutants | Not universally superior for natural single-substitution ranking |
| **Evaluation framework** | DNALONGBENCH / RNAGym / ProteinGym / MaveDB / ClinVar | Separates representation, fine-tuning, zero-shot scoring, and calibration | Prevents leakage-driven or scoring-rule artifacts | DNA/RNA benchmarks remain less mature than protein benchmarks |

---

**End of Report**.
