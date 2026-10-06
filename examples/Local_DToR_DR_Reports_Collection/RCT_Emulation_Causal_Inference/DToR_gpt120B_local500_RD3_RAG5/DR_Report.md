# Final Research Report: Recovering RCT Effects From Observational Health Data — Which target‑trial designs, causal estimators, diagnostics, and benchmarks most reliably reproduce randomized‑trial effects?

**Integrated Research Report**
*Design‑first causal inference and doubly robust learning for RCT‑concordant real‑world evidence*  

---

## 1. Introduction  

Recovering randomized clinical trial (RCT) effects from observational health data is not primarily an “algorithm selection” problem. It is a **trial‑emulation problem**: the analyst must specify the hypothetical randomized trial that would answer the clinical question, map that protocol into real‑world data (RWD), assess whether the data source can measure the required variables, and only then choose an estimator. The source report’s central message is therefore deliberately sequential: **target trial first, data fit second, estimator third, diagnostics always**.

Three independent branch syntheses were constructed to mirror the DToR branch‑to‑final workflow:

| Branch | Core Concept | Role in the Final Synthesis |
|--------|--------------|-----------------------------|
| **9c4a2f10d7b1a8e3** | Target‑trial specification, estimand discipline, and fit‑for‑purpose data | Defines the causal object: eligibility, treatment strategies, time zero, outcome, follow‑up, censoring, confounders, overlap, and data‑source feasibility. |
| **4e8b0c91af65d2b4** | Doubly robust estimators, causal machine learning, and method reliability | Ranks analysis methods after identification is plausible: AIPW/TMLE/DML for point treatments, longitudinal g‑methods for dynamic/adherence‑sensitive questions, ML as nuisance/HTE support. |
| **b7f3d6a2c19e0f45** | Benchmark evidence, specialty transferability, and empirical validation | Grounds the recommendations in RCT DUPLICATE, SWEDEHEART/TASTE/VALIDATE/REDUCE‑AMI, hormone‑therapy reanalysis, oncology examples, and endpoint‑specific data‑fit failures. |

The following sections synthesize these branches, resolve contradictions, identify unique contributions, and deliver a consolidated answer on when observational health data can credibly recover RCT effects.

---

## 2. Synthesized Findings  

### 2.1 Common Themes Across Branches  

| Theme | Evidence from Branches | Integrated Interpretation |
|-------|------------------------|---------------------------|
| **Design decisions dominate algorithm choice** | RCT DUPLICATE showed better agreement when PICOT elements and measurements were closely emulated; branch 9c4a2f10 emphasizes time zero, eligibility, follow‑up, outcomes, and estimand alignment. | An observational analysis cannot recover the RCT effect unless it is trying to estimate the same causal contrast as the RCT. |
| **Fit‑for‑purpose data are non‑negotiable** | Claims, EHRs, and registries have distinct strengths and weaknesses; branch b7f3d6a2 shows endpoint‑specific successes and failures. | A stronger model cannot rescue missing trial variables, poorly observed endpoints, or unmeasured treatment‑choice drivers. |
| **Doubly robust estimators are the best point‑treatment default** | Branch 4e8b0c91 ranks AIPW, TMLE, and orthogonal DML above singly robust methods when overlap and measured confounding are plausible. | Once the target trial is well posed, cross‑fit DR estimation is the most defensible general‑purpose estimator family. |
| **Longitudinal questions require longitudinal g‑methods** | Sustained use, per‑protocol effects, dynamic regimens, adherence, censoring, and time‑varying confounding require MSMs, g‑formula, clone–censor–weight, or LTMLE. | Baseline PS or baseline outcome regression can estimate the wrong effect when treatment and confounders evolve over time. |
| **Machine learning is useful inside the causal workflow** | ML improves nuisance estimation and heterogeneity exploration, but singly robust ML plug‑ins can be biased or undercover. | Use ML under orthogonalized, diagnostics‑heavy causal estimators rather than as a replacement for trial emulation. |
| **Benchmarking is a validation scaffold, not a decorative add‑on** | RCT DUPLICATE, SWEDEHEART, WHI/Nurses’, KEYNOTE‑189, French breast cancer, and BIG 1‑98 illustrate where emulation succeeds or fails. | Benchmarking reveals whether the protocol, data, and estimator are jointly credible before extension analyses are attempted. |

### 2.2 Performance Highlights  

| Category | Representative Material / Methodology | Performance Highlights | Key Advantage | Main Limitation |
|----------|----------------------------------------|-----------------------|---------------|-----------------|
| **Design architecture** | Target trial emulation with active‑comparator new‑user design | RCT DUPLICATE: overall encouraging agreement; close emulations had much higher significance and estimate agreement. | Directly aligns observational analysis with the trial protocol. | Fails if eligibility, time zero, outcome, or treatment strategy cannot be mapped. |
| **Primary point‑treatment estimator** | AIPW / TMLE / orthogonal DML with cross‑fitted flexible nuisance models | Low bias and better coverage in nonlinear or high‑dimensional simulation patterns when identification and overlap are adequate. | Doubly robust protection and principled ML integration. | Still vulnerable to unmeasured confounding and weak overlap. |
| **Longitudinal estimator family** | MSM/IPW, parametric g‑formula, clone–censor–weight, longitudinal TMLE | Targets per‑protocol, sustained‑use, dynamic‑regimen, and time‑varying treatment questions. | Handles time‑varying confounding affected by prior treatment. | Requires sequential exchangeability, longitudinal positivity, and accurate timing. |
| **Claims‑based proxy adjustment** | hdPS, Super Learner PS, balance‑oriented PS modeling | Can improve proxy confounding control in large claims datasets. | Scales to high‑dimensional healthcare utilization variables. | Prediction‑oriented feature selection can harm balance or include instruments/colliders. |
| **HTE / flexible modeling tools** | Causal forests, BART, Bayesian causal forests, neural networks | Useful for CATE discovery and nuisance modeling. | Captures nonlinearities and heterogeneity. | Limited direct evidence as stand‑alone primary ATE estimators for RCT recovery. |
| **Benchmark validation** | RCT‑versus‑RWE agreement plots, control outcomes, KM overlays | Identifies concordant and discordant emulations; supports extension only after acceptable benchmark. | Makes design/data failures visible. | Requires an existing or subsequent RCT benchmark and comparable effect scale. |

### 2.3 Benchmark Evidence Matrix  

| Benchmark Context | Result Pattern | What It Teaches |
|------------------|----------------|-----------------|
| **RCT DUPLICATE** | Positive but imperfect agreement overall; much stronger agreement for close emulations. | Design/measurement closeness is the dominant empirical driver. |
| **TASTE / SWEDEHEART** | Registry emulation reproduced the no‑major‑difference death/MI result. | Registries can work well when initiation, procedures, covariates, and hard outcomes are captured. |
| **VALIDATE / SWEDEHEART** | Death/MI aligned, but bleeding did not. | A data source can be fit for one endpoint and not another. |
| **REDUCE‑AMI** | Prospective observational emulation predicted no large beta‑blocker benefit before the RCT result. | RWE‑before‑RCT benchmarking is especially persuasive. |
| **WHI vs Nurses’ Health Study** | Timing‑aware emulation narrowed the apparent hormone‑therapy discrepancy. | Many RWE/RCT conflicts are estimand and timing conflicts. |
| **KEYNOTE‑189 EHR emulation** | Observational mortality estimate diverged strongly from the trial. | EHR richness is insufficient if survival determinants and treatment pathways are not captured. |
| **French metastatic‑breast‑cancer emulations** | Most tested strategies aligned with trial evidence. | Oncology emulation can succeed when treatment pathways and prognostic burden are measured well enough. |
| **BIG 1‑98 breast‑cancer benchmark** | Initial discordance improved after restricting likely channeling variables. | Unmeasured treatment‑choice drivers can dominate even structured emulations. |

### 2.4 Practical Workflow  

| Step | Required Action | Failure if Skipped |
|------|-----------------|--------------------|
| **1. Define estimand** | Specify ITT analogue, per‑protocol, sustained use, dynamic regimen, effect scale, intercurrent events, and target population. | The observational study answers a different causal question from the trial. |
| **2. Write target‑trial protocol** | Specify eligibility, assignment, treatment strategies, time zero, follow‑up, outcome, censoring, and analysis. | Immortal time, prevalent use, post‑baseline selection, endpoint mismatch. |
| **3. Audit data source** | Verify treatment initiation, covariates, endpoints, adherence, censoring, and specialty‑specific variables. | Key confounders or outcomes are not measured. |
| **4. Build covariate set causally** | Use clinical knowledge first; add proxies such as hdPS where appropriate. | Prediction‑driven adjustment includes instruments/colliders or misses true confounders. |
| **5. Choose estimator by estimand** | Point treatment → AIPW/TMLE/DML; longitudinal strategy → MSM/g‑formula/LTMLE; poor overlap → overlap target or trimming. | The estimator is elegant but targets the wrong effect. |
| **6. Diagnose design and estimator** | Balance, overlap, effective sample size, weight stability, calibration, negative/positive controls. | No evidence the emulation worked. |
| **7. Benchmark when possible** | Compare effect size, CI, curves, endpoint definitions, and control outcomes against RCT evidence. | Extension claims are unanchored. |
| **8. Extend cautiously** | Only after acceptable benchmark; then ask subgroup, longer follow‑up, transportability, or under‑represented‑population questions. | External‑validity work transports internal bias. |

---

## 3. Contradiction Analysis & Resolution  

| Contradiction | Source(s) | Analysis & Resolution |
|---------------|-----------|-----------------------|
| **“Design matters most” vs. “Estimator choice matters.”** | Target‑trial branch vs. estimator branch | These statements are sequential, not conflicting. **Design identifies the target causal effect; the estimator controls estimation error** after identification is plausible. |
| **“Claims are too crude” vs. “Claims benchmarks work.”** | Data‑fit branch vs. RCT DUPLICATE/cardio benchmarks | Claims are weak for nuanced clinical severity but strong for dispensing, procedures, hospitalizations, and hard outcomes. Claims are credible when the target trial’s necessary variables are claims‑observable. |
| **“EHRs are richer” vs. “EHR emulations fail.”** | Data‑fit branch vs. KEYNOTE‑189 example | Richness does not imply completeness. EHRs can still miss outside care, performance status, progression, adherence, and line‑of‑therapy details. |
| **“ML improves adjustment” vs. “ML can worsen bias.”** | Estimator branch | ML improves nuisance estimation when embedded in cross‑fit DR/orthogonal scores. ML used as a singly robust plug‑in can optimize prediction instead of balance and causal identification. |
| **“PS matching is benchmark‑tested” vs. “DR is preferred.”** | RCT DUPLICATE practice vs. method simulations | PS matching is a useful transparent comparator; DR estimators are preferred when feasible because they use both treatment and outcome models and are less exposed to single‑model misspecification. |
| **“Oncology RWE is unreliable” vs. “Oncology RWE can succeed.”** | KEYNOTE‑189 vs. French metastatic‑breast‑cancer emulations | Oncology is not uniformly impossible. Success depends on whether the data capture treatment pathway, biomarker status, performance status, tumor burden, and progression for the specific question. |
| **“Transportability can fix RWE/RCT differences” vs. “Standardization may not improve agreement.”** | Transportability discussion vs. RCT DUPLICATE population‑standardization results | Transportability is late‑stage. It can align target populations but cannot repair unmeasured confounding, endpoint mismatch, wrong time zero, or non‑emulable eligibility. |

Overall, most contradictions resolve by enforcing the correct order: **estimand → target trial → data‑fit audit → causal covariates → estimator → diagnostics → benchmark → extension**.

---

## 4. Unique Perspective Insights  

### 4.1 Branch 9c4a2f10d7b1a8e3 – Target‑Trial Design & Data‑Fit  

* **Protocol alignment as internal validity** – The branch reframes RWE credibility around the target trial protocol rather than the sophistication of the model.  
* **Endpoint‑ and variable‑specific data auditing** – It shows why the same data source can be valid for one endpoint and invalid for another.  
* **Confounding taxonomy** – It separates measured, unmeasured, and time‑varying confounding, preventing a single adjustment recipe from being misapplied.  
* **Overlap‑aware estimands** – It emphasizes that trimming, matching, and overlap weighting may change the target population and must be reported explicitly.  

### 4.2 Branch 4e8b0c91af65d2b4 – Doubly Robust / Causal‑ML Reliability  

* **DR estimators as the default point‑treatment engine** – AIPW, TMLE, and orthogonal DML provide the most defensible general workflow when the emulation is well posed.  
* **Longitudinal g‑methods as necessary tools** – MSM, g‑formula, clone–censor–weight, and LTMLE are required when treatment and confounders evolve over time.  
* **Machine learning as nuisance infrastructure** – ML is most credible when used to estimate nuisance functions or discover heterogeneity inside a causal estimator.  
* **Prediction is not causation** – The branch explains why AUC, RMSE, or treatment‑assignment prediction cannot substitute for balance, overlap, and causal diagnostics.  

### 4.3 Branch b7f3d6a2c19e0f45 – Benchmark Evidence & Specialty Transferability  

* **RCT DUPLICATE as empirical baseline** – It provides a broad, multi‑trial anchor showing that close emulations work better than loose emulations.  
* **Cardiology as a high‑fit exemplar** – SWEDEHEART examples show how registries can support credible emulation when endpoints and procedures are well recorded.  
* **Oncology as a data‑fit stress test** – KEYNOTE‑189 and metastatic breast‑cancer examples show that success depends on disease‑specific variables and treatment pathways.  
* **Prospective benchmarking as gold‑standard validation** – REDUCE‑AMI style RWE‑before‑RCT comparisons reduce hindsight bias and should become more common.  

Each branch therefore contributes one layer of the final answer: **causal design**, **estimator reliability**, and **empirical validation**. The integrated workflow is strongest only when all three layers are present.

---

## 5. Comprehensive Conclusion  

The integrated answer is clear: **observational health data can recover RCT effects only when the observational study is a disciplined emulation of the right trial, implemented in a fit‑for‑purpose data source, analyzed with an estimator matched to the estimand, and validated through diagnostics and benchmarks.**

The most reliable practical default is:

> **Pre‑specified target trial emulation + fit‑for‑purpose data + causal covariate construction + overlap diagnostics + cross‑fit doubly robust estimation for point‑treatment effects, or longitudinal g‑methods for sustained/dynamic/adherence‑sensitive estimands, followed by benchmark and control‑outcome validation.**

**Which methods are most reliable?**

1. **For point‑treatment RCT recovery:** target trial emulation analyzed with AIPW, TMLE, or orthogonal DML using cross‑fit flexible nuisance models.  
2. **For longitudinal or adherence‑sensitive effects:** MSM/IPW, parametric g‑formula, clone–censor–weight designs, or LTMLE.  
3. **For simpler point‑treatment questions:** g‑computation and overlap weighting can be strong when overlap and outcome modeling are credible.  
4. **For large claims studies:** PS matching/weighting, hdPS, and Super Learner PS are useful, especially as transparent comparators or nuisance components.  
5. **For causal ML tools:** BART, causal forests, Bayesian causal forests, neural nets, random forests, and boosting are best used for nuisance estimation and heterogeneity discovery, not as stand‑alone replacements for design‑first DR emulations.  

**Where is RWE most likely to match an RCT?**

| More Likely to Succeed | More Likely to Fail |
|------------------------|--------------------|
| Incident treatment initiation is observable | Prevalent use or unclear initiation |
| Active comparator exists | No credible comparator; severe confounding by indication |
| Hard endpoints are consistently captured | Soft, subjective, or poorly coded outcomes |
| Key confounders or valid proxies are measured | Treatment choice driven by unmeasured severity |
| Adequate treatment overlap exists | Extreme propensities and extrapolation |
| Registry/claims follow‑up is complete | Fragmented EHR care outside network |
| ITT‑like initiation question | Sustained adherence or dynamic strategy without longitudinal methods |
| Existing RCT benchmark validates design | No benchmark, controls, or sensitivity analyses |

In short, **algorithmic complexity cannot compensate for poor design or unfit data**. The strongest RWE studies behave like disciplined trials without randomization: they specify the trial, audit the data, choose the correct causal estimator, prove balance/overlap, test controls, and benchmark before extrapolating.

---

## 6. Candidate Inventory  

target trial emulation, target estimand, target trial protocol, TARGET reporting guideline, ICH E9(R1), active‑comparator new‑user design, time‑zero alignment, eligibility mapping, treatment‑strategy specification, grace period, incident‑user cohort, follow‑up window, censoring rule, intercurrent event, intention‑to‑treat analogue, per‑protocol effect, sustained‑use estimand, dynamic treatment strategy, RCT DUPLICATE, SWEDEHEART, TASTE, VALIDATE, REDUCE‑AMI, Women’s Health Initiative, Nurses’ Health Study, KEYNOTE‑189, French metastatic‑breast‑cancer cohort, BIG 1‑98, PARADIGM‑HF benchmark, AIPW, TMLE, longitudinal TMLE, orthogonal machine learning, double machine learning, Super Learner, balance Super Learner, high‑dimensional propensity score, propensity‑score matching, IPTW, stabilized weights, overlap weighting, trimming, g‑computation, outcome regression, marginal structural model, parametric g‑formula, clone–censor–weight design, random forests, gradient boosting, neural networks, BART, Bayesian causal forests, causal forests, outcome‑adaptive lasso, negative controls, positive controls, double‑negative controls, quantitative bias analysis, E‑value, positivity diagnostics, effective sample size, Love plot, propensity‑density plot, RCT‑versus‑RWE agreement plot, Bland–Altman view, Kaplan–Meier overlay, cumulative‑incidence overlay, endpoint observability audit, EHR missingness audit, registry linkage, transportability, population standardization.

| Category | Representative Material / Methodology | Performance Highlights | Key Advantage | Main Limitation |
|----------|----------------------------------------|-----------------------|---------------|-----------------|
| **Design framework** | Target trial emulation | Aligns eligibility, assignment, time zero, follow‑up, outcomes, and estimand with the hypothetical RCT. | Prevents structural design bias. | Requires data elements that may not exist. |
| **Point‑treatment estimator** | AIPW / TMLE / orthogonal DML | Doubly robust, cross‑fit, ML‑compatible effect estimation. | Best default after credible identification. | Weak overlap and unmeasured confounding remain fatal. |
| **Longitudinal estimator** | MSM / g‑formula / LTMLE / clone–censor–weight | Handles time‑varying treatment, adherence, censoring, and confounding. | Correct target for sustained/dynamic effects. | Requires careful longitudinal timing and positivity. |
| **Claims proxy strategy** | hdPS / Super Learner PS | Captures empirical healthcare‑utilization proxies. | Useful in high‑dimensional claims data. | Can include instruments/colliders without causal review. |
| **HTE / nuisance ML** | BART / causal forests / neural nets / boosting | Flexible nonlinear modeling and subgroup discovery. | Powerful inside DR or HTE workflows. | Insufficient benchmark evidence as stand‑alone ATE replacement. |
| **Validation scaffold** | RCT benchmark, negative/positive controls, agreement plots | Tests whether the emulation reproduces expected effects and controls. | Reveals design/data failure modes. | Requires suitable benchmarks or controls. |

**End of Report**.
