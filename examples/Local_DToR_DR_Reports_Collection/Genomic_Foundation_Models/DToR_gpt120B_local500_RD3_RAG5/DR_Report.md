# Final Research Report: Which architectural and pre-training strategies—including state-space models, long-context transformers, and hybrid masked/autoregressive objectives—enable foundation models for DNA, RNA, and protein sequences to most reliably predict regulatory function, variant effects, and zero-shot biological properties at genome scale?

**Integrated Research Report**  
*Architectural and Pre-Training Strategies for DNA, RNA, and Protein Foundation Models*  

---

## 1. Introduction  

Foundation models for biological sequences now span three related but non-identical regimes: **DNA** models for regulatory function and variant effects, **RNA** models for structure, splicing, and transcript-level function, and **protein** models for variant effect, zero-shot fitness, and sequence design. The central question is not whether one universal architecture dominates all biological sequence modeling, but which architectural and pre-training strategy is most reliable for each biological modality and end task.

Three independent research branches were examined to answer the question:

| Branch | Core Concept |
|--------|--------------|
| **8f3b9d11a6c4e2f0** | DNA long-context genomic foundation models for regulatory function and variant-effect prediction, emphasizing AlphaGenome-style supervised sequence-to-function hybrids, Evo 2-style very-long-context AR/SSM models, and Nucleotide Transformer-style masked transfer learning. |
| **27aa6e5cb91fd044** | RNA foundation models for structure, splicing, and transcript-level functional prediction, emphasizing MSA-aware structure modeling, single-nucleotide tokenization, ALiBi, and the limits of zero-shot splicing performance. |
| **f0b4d92e6a18c37b** | Protein structure-aware and MSA-augmented foundation models for variant effect and zero-shot function, emphasizing masked bidirectional models, structure tokens, retrieval augmentation, and causal/hybrid models for generation-compatible workflows. |

Together, the branches indicate a strongly task-dependent landscape. For **DNA regulatory prediction**, the most reliable systems are supervised, multi-resolution, long-context sequence-to-function models. For **zero-shot DNA variant scoring**, very-long-context autoregressive or SSM-like genome models are the strongest unsupervised family. For **RNA structure**, MSA-aware bidirectional models remain the safest option when homologs are available, while nucleotide-level sequence encoders are more deployable for transcriptome-scale tasks. For **proteins**, masked bidirectional models augmented by MSA, retrieval, or structure tokens remain the strongest zero-shot variant-effect recipe, while causal/hybrid models are best positioned for generation plus scoring.

---

## 2. Synthesized Findings  

### 2.1 Common Themes Across Branches  

| Theme | Evidence from Branches |
|-------|------------------------|
| **No single architecture wins across DNA, RNA, and proteins.** | DNA favors long-context supervised sequence-to-function hybrids for regulatory tasks; RNA structure favors MSA-aware bidirectional models; proteins favor masked bidirectional models with MSA/structure augmentation. |
| **Long context helps only when the model preserves biological granularity.** | DNA models need base-level outputs and motif sensitivity; RNA models need nucleotide-level base-pair information; protein models need residue-level or structure-aware tokens. |
| **Efficient context mechanisms are enabling but not sufficient.** | Longformer, BigBird, Performer, Mamba, Hyena, RoPE, and ALiBi improve scaling, but the strongest biological systems add domain-specific inductive bias: multi-resolution convolution, MSA, retrieval, or structure tokens. |
| **Pretraining objective should match the scoring problem.** | DNA zero-shot variant scoring benefits from AR likelihood changes over long contexts; protein substitution scoring maps naturally to masked marginal likelihoods; RNA structure benefits from MSA-aware masked/denoising-style objectives. |
| **Tokenization should remain close to the biological alphabet unless compression is empirically justified.** | Nucleotide Transformer finds six-mers useful for moderate-context DNA; Evo 2 uses single-nucleotide resolution; BEACON favors single-nucleotide RNA tokens; proteins mostly use amino-acid tokens plus optional structure tokens. |
| **Supervised refinement remains essential for high-confidence functional prediction.** | AlphaGenome-style track prediction and distillation outperform pure genomic language models on many regulatory tasks; supervised splicing tools remain strong; protein engineering splits require task-matched validation. |

### 2.2 Performance Highlights  

| Category | Representative Material / Methodology | Performance Highlights | Key Advantage | Main Limitation |
|----------|----------------------------------------|-----------------------|---------------|-----------------|
| **DNA supervised regulatory/variant prediction** | AlphaGenome-style U-Net encoder + transformer tower + decoder with teacher–student distillation | 1 Mb context; state-of-the-art on 22/24 genome-track tasks and 25/26 variant-effect tasks; distilled student variant scoring | Strongest current route for labeled genome-scale regulatory prediction | Label-hungry; expensive; less purely self-supervised |
| **DNA zero-shot variant scoring** | Evo 2-style long-context AR/SSM genome foundation model | 1M-token single-nucleotide context; trained on ≈9T DNA bases; strong unsupervised ClinVar/splicing/noncoding signals | Best current unsupervised genome-scale variant-prioritization recipe | Still trails supervised regulatory models on some tasks |
| **DNA transfer baseline** | Nucleotide Transformer-style masked transformer | Six-mer tokens; multispecies pretraining; useful masked-token signal for splice/polyA/CTCF features | Practical moderate-context transfer model | Shorter context than 1 Mb or 1M-token systems |
| **RNA structure prediction** | RNA-MSM-style MSA transformer | Best median F1/MCC among Class I zero-shot RNA structure models; beats larger sequence-only models in reported comparisons | Evolutionary context gives strong structure reliability | MSA generation is expensive and coverage-limited |
| **RNA transcript/splicing deployment** | RNA-FM / RiNALMo / SpliceBERT-style bidirectional encoders | RNA-FM trained on 23M ncRNAs; RiNALMo 650M on 36M ncRNAs; useful structure/splicing/function transfer | Practical when homologs are unavailable | Zero-shot splicing metrics remain modest; supervised adaptation often needed |
| **Protein zero-shot substitution scoring** | MSA Transformer, SaProt, AIDO.RAGPLM-style masked/MSA/structure/retrieval models | MSA Transformer beats ESM-1v on average DMS Spearman; SaProt reports strong ProteinGym/ClinVar gains; retrieval improves fitness/contact tasks | Strongest evidence for variant-effect scoring | Requires MSA, retrieval, or structure infrastructure |
| **Protein generation-compatible modeling** | ProtMamba / Proust-style causal or hybrid models | Fill-in-the-middle or causal objectives; supports generation and scoring in one model; Proust-style models narrow the substitution gap efficiently | Useful for design workflows requiring generation | Usually below top masked structure/MSA systems for substitutions |

### 2.3 Modality-Specific Strategic Synthesis  

**DNA.** The highest-confidence regulatory and causal variant prediction strategy is a **multi-resolution convolution/U-Net front end plus compressed long-range transformer tower**, trained on supervised multimodal functional genomics tracks and distilled with mutational perturbations. For unsupervised genome-wide variant prioritization, the strongest strategy is a **single-nucleotide, very-long-context AR/SSM genome model** trained across large multispecies corpora.

**RNA.** The most reliable structure strategy is an **MSA-aware bidirectional model** when homologs exist. For transcriptome-scale splicing or function tasks, a **large single-nucleotide bidirectional encoder with ALiBi** is more practical, but should be fine-tuned or calibrated against task-specific labels for high-confidence deployment.

**Protein.** The most reliable zero-shot variant-effect strategy is a **masked bidirectional protein model augmented with MSA, retrieval, or structure-aware tokens**. Causal or hybrid models become attractive when **generation and scoring must be unified**, but they should not yet be treated as the best substitution-effect predictors.

---

## 3. Contradiction Analysis & Resolution  

| Contradiction | Source(s) | Analysis & Resolution |
|---------------|-----------|-----------------------|
| **“One architecture wins everywhere” vs. “task-dependent split.”** | All branches | Biological modalities reward different inductive biases. DNA regulatory tasks need long-range sequence-to-function supervision; RNA structure benefits from evolutionary alignments; protein fitness benefits from masked scoring plus MSA/structure. The resolution is to select architecture by modality and endpoint rather than seeking one universal winner. |
| **Long-context AR/SSM genome models vs. supervised DNA sequence-to-function models.** | DNA branch | Evo 2-style models are the strongest unsupervised DNA zero-shot family, but supervised AlphaGenome-style systems remain more reliable for many labeled regulatory tasks. The resolution is to use AR/SSM models for unsupervised prioritization and supervised hybrids for high-confidence regulatory prediction. |
| **K-mer DNA tokenization vs. single-nucleotide tokenization.** | DNA branch | Six-mers are effective in Nucleotide Transformer-style moderate-context masked models, while Evo 2-style long-context models use single-nucleotide resolution. The resolution is contextual: use k-mers when they improve compact transfer learning, but preserve single-base granularity for million-token likelihood scoring and base-resolution outputs. |
| **RNA model scale vs. evolutionary context.** | RNA branch | Larger sequence-only RNA models can learn useful structure, but RNA-MSM-style MSA models outperform larger models on some structure metrics. The resolution is to use MSA-aware models for structure when homologs exist, and sequence-only encoders for broad or online deployment. |
| **RNA foundation models vs. dedicated splicing predictors.** | RNA branch | RNA LMs improve transfer, but zero-shot splice metrics remain modest; supervised splicing-specific models remain important. The resolution is to treat RNA FMs as representation backbones, not full replacements, for clinical or high-confidence splicing prediction. |
| **Masked protein encoders vs. decoder-only protein LMs.** | Protein branch | Causal models generate sequences naturally and can score variants, but masked MSA/structure-aware models remain stronger for substitution fitness. The resolution is endpoint-specific: masked/structure/MSA models for best zero-shot scoring; causal/hybrid models for generation-plus-scoring workflows. |
| **ProteinGym rank vs. deployment reliability.** | Protein branch | ProteinGym is a crucial benchmark, but FLIP2-style splits show that distribution shift can alter conclusions. The resolution is to validate models on deployment-matched splits, especially for engineering campaigns and out-of-family design. |

Overall, the apparent contradictions arise from comparing different biological tasks, supervision regimes, and deployment constraints. A reliable strategy must distinguish **zero-shot vs. supervised**, **local vs. long-context**, **sequence-only vs. MSA/structure-augmented**, and **scoring-only vs. generation-compatible** settings.

---

## 4. Unique Perspective Insights  

### 4.1 DNA Long-Context Genomic Models Branch  

The DNA branch contributes the clearest distinction between **sequence-to-function prediction** and **genomic language modeling**. Its main insight is that regulatory function is not solved by language-model pretraining alone: high-confidence regulatory and variant prediction requires a supervised, multi-resolution architecture that outputs many functional tracks and learns variant effects through perturbation and distillation. At the same time, the branch identifies very-long-context AR/SSM models as the strongest unsupervised route for genome-wide zero-shot scoring.

### 4.2 RNA Structure and Splicing Models Branch  

The RNA branch highlights that RNA remains the most fragmented modality. Its strongest contribution is the emphasis on **evolutionary context for structure** and **single-nucleotide tokenization with ALiBi for deployable sequence encoders**. It also prevents overclaiming: RNA foundation models help splicing, but specialized supervised splicing predictors remain necessary when the application requires high confidence.

### 4.3 Protein Structure/MSA Variant Models Branch  

The protein branch provides the most mature benchmark logic. It shows that **masked bidirectional scoring**, especially when augmented with MSA, retrieval, or structure tokens, remains the strongest evidence-backed approach for zero-shot protein variant effects. Its distinctive contribution is separating scoring reliability from generation utility: decoder-only and hybrid models are valuable for design workflows, but they do not yet displace masked structure/MSA-aware models for substitution fitness.

---

## 5. Synthesized Answer / Conclusions  

The most reliable answer is a **modality- and task-specific architecture portfolio** rather than a single universal biological foundation model.

For **DNA regulatory function and causal variant prediction**, the best-supported strategy is a **multi-resolution convolutional/U-Net-style sequence-to-function model with a long-context transformer tower**, trained on supervised multimodal functional genomics tracks and distilled for variant scoring. This is the most reliable recipe when labels and functional tracks are available. For **zero-shot DNA variant prioritization**, the best-supported unsupervised strategy is a **very-long-context AR/SSM-style genome foundation model** with single-nucleotide resolution and multispecies training.

For **RNA**, the safest structure-focused strategy is an **MSA-aware bidirectional transformer** when homologous alignments are available. For transcriptome-scale splicing and RNA function tasks, the most practical generic recipe is a **large bidirectional nucleotide-level encoder with single-nucleotide tokenization and ALiBi**, followed by task-specific adaptation. RNA foundation models should be treated as strong representation learners, not as complete replacements for supervised splicing predictors.

For **proteins**, the strongest evidence supports **masked bidirectional protein models augmented with MSA, retrieval, or structure-aware tokens** for zero-shot variant-effect and functional prediction. When sequence generation and scoring must be unified, **causal or hybrid models** such as ProtMamba/Proust-style systems become attractive, but they remain secondary to masked structure/MSA-aware systems for best substitution-effect scoring.

The cross-cutting design rule is: **choose the objective and architecture that match the biological signal**. Long context, efficient attention, state-space recurrence, and hybrid objectives are powerful only when paired with the right inductive bias—functional-track supervision for DNA, evolutionary alignment for RNA structure, and MSA/structure augmentation for protein fitness.

---

## 6. Candidate Inventory  

AlphaGenome, Borzoi, Enformer-like sequence-to-function models, ChromBPNet, Nucleotide Transformer, Evo 2, DNABERT-style masked transformers, HyenaDNA, Mamba/SSM genome models, Longformer, BigBird, Performer, Transformer-XL, Perceiver-style latent bottlenecks, RoPE, ALiBi, U-Net encoder–decoder architectures, convolutional motif encoders, transformer towers, teacher–student distillation, mutational perturbation training, autoregressive next-token likelihood scoring, masked-token scoring, RNA-FM, RiNALMo, RNA-MSM, AIDO.RNA, MP-RNA, SpliceBERT, DGRNA, SpliceAI, Pangolin, BEACON RNA benchmark, Rfam/RNAcmap-style MSA data, ESM-1v, ESM-2, MSA Transformer, SaProt, ProSST-style structure-aware models, AIDO.Protein, AIDO.RAGPLM, ProtMamba, Proust, ProtTrans/T5-style denoising models, xTrimoPGLM, ProstT5, Foldseek-derived structure tokens, amino-acid tokenization, single-nucleotide tokenization, six-mer tokenization, fill-in-the-middle objective, causal next-token objective, masked language modeling, denoising objectives, MSA objectives, retrieval-augmented pretraining, ProteinGym, FLIP2, ClinVar, CAGI, DNALONGBENCH, TraitGym, DART-eval, SpliceVarDB, BRCA1 variant benchmarks, caQTL/dsQTL evaluation, DMS fitness landscapes, contact prediction, protein sequence generation, indel scoring, genome-track prediction, RNA secondary-structure prediction, RNA 3D-structure prediction, protein–RNA binding prediction, viral genome analysis.

---

### Table 1 – Representative Architecture / Objective / Biological Use Cases  

| Category | Representative Material / Methodology | Performance Highlights | Key Advantage | Main Limitation |
|----------|----------------------------------------|-----------------------|---------------|-----------------|
| **DNA supervised sequence-to-function** | AlphaGenome-style U-Net + transformer + decoder | 1 Mb context; SOTA on 22/24 track tasks and 25/26 variant-effect tasks | Best reliable regulatory/variant predictor when labels exist | Requires supervised tracks, expensive training, and complex output heads |
| **DNA unsupervised zero-shot** | Evo 2-style AR/SSM long-context genome model | 1M-token context; ≈9T DNA bases; strong ClinVar/splice/noncoding zero-shot signals | Best unsupervised genome-scale prioritization route | Not uniformly better than supervised regulatory baselines |
| **DNA masked transfer model** | Nucleotide Transformer-style six-mer MLM | Multispecies pretraining; useful splice/polyA/CTF-like motif signals | Practical transfer learning under moderate contexts | Limited distal regulatory context |
| **RNA MSA-aware structure model** | RNA-MSM-style MSA transformer | Strong median F1/MCC for RNA secondary-structure-like tasks | Evolutionary context improves reliability | MSA generation cost and coverage limits |
| **RNA sequence encoder** | RNA-FM / RiNALMo / SpliceBERT-style bidirectional encoder | Broad ncRNA pretraining; useful for structure, binding, regulation, splicing transfer | Deployable when homologs are unavailable | Splicing zero-shot accuracy remains modest |
| **Protein masked MSA/structure model** | MSA Transformer / SaProt / AIDO.RAGPLM-style models | Strong DMS, ProteinGym, ClinVar, contact, and fitness signals | Best-supported zero-shot variant-effect family | Requires structure, retrieval, or homolog infrastructure |
| **Protein causal/hybrid generation model** | ProtMamba / Proust-style causal or FIM models | Supports generation and scoring in one model; efficient training possible | Attractive for sequence design workflows | Usually below top masked structure/MSA systems for substitution scoring |

*All performance highlights are taken from the consolidated branch material. “Representative Material / Methodology” is retained as the table-column convention from the strict DR template, even though the present topic concerns model families rather than physical materials.*  

---  

**End of Report**.
