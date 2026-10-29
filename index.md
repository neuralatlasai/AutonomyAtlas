# Agentic State: Context, Memory, and Control in Adaptive AI

A Technical Monograph on Conditioning, Tool Execution, Verification, and Self-Improvement

Literature cutoff and source review: **29 October 2026** for all 34 chapters. Primary-source inspection: **28 October 2026 to 29 October 2026**. Source review is complete. Final illustration and PDF validation are complete.

Planned substantive allocation: **370 pages** (minimum 360). These are editorial page budgets, not actual pagination.

Final audited body pages: **482**. Pagination audit is bound to PDF SHA-256 fd03ac45e6700a4dc4cf9ead84a3206407c6ee60388fe4c1519ca686989c9d0b.

## Contribution and evidence boundary

A cross-layer analysis of conditioning consistency, authority preservation, and effect reconstruction, with explicit implementation/evidence contracts and discriminating interventions. This is an original synthesis and analysis, not a claim of a new empirically validated AGI architecture.

Three separate obligations organize the analysis: preserve decision-relevant conditioning, prevent unauthorized expansion of executable actions, and retain the evidence needed to reconstruct external effects. The manuscript derives their non-implication, connects them to current implementations, and proposes experiments that can reject claims about their composition. It does not claim new empirical measurements, unrestricted AGI, or indefinite recursive improvement.

## Connected research threads

| Thread | Connected chapters | Boundary examined |
|---|---|---|
| Representation to decision | C03 &rarr; C05 &rarr; C06 &rarr; C10 &rarr; C11 | Decision-relevant distinctions under intervention. |
| Context to learning | C08 &rarr; C11 &rarr; C12 &rarr; C17 &rarr; C30 | Behavior conditioning and co-adaptation. |
| Memory to execution | C13 &rarr; C14 &rarr; C15 &rarr; C16 &rarr; C18 &rarr; C20 | Provenance, validity, applicability, and effect identity. |
| Authority to effects | C18 &rarr; C19 &rarr; C20 &rarr; C28 &rarr; C29 &rarr; C32 | Permission, enforcement, commitment, and recovery. |
| Measurement to improvement | C25 &rarr; C26 &rarr; C27 &rarr; C30 &rarr; C33 | Verifier error, leakage, longitudinal effects, and transfer. |
| Physical to semantic state | C04 &rarr; C12 &rarr; C17 &rarr; C31 &rarr; C32 | Computational cache identity and state migration. |

## Hierarchical chapter index

### System semantics and scientific identification

#### C01 [Agentic Computation: System Boundaries, Generality, and Evidence](book/chapters/01-system/chapter.tex)

**Objective and analytical output.** Versioned system boundary, model-harness interaction, three independent consistency contracts, and scoped diagnostic admission with separate effect and task evidence.

**Contemporary evidence anchor.** HRP separates interface opportunity from policy mismatch; Agent Lightning, ASAP, TraceTrial-Bench, ALE and AgentHorizon expose distinct conditioning and measurement boundaries.

**Prerequisites.** System-level problem formulation.

**Planned allocation.** 8 substantive pages. **Source review.** 29 October 2026.

1. [The agent is the unit of analysis](book/chapters/01-system/sections/01.tex)
2. [A stateful formulation of execution](book/chapters/01-system/sections/02.tex)
3. [Generality as a profile of conditional competence](book/chapters/01-system/sections/03.tex)
   - [Model--harness interaction and adaptation](book/chapters/01-system/sections/03.tex)
4. [An ontology of models and connecting components](book/chapters/01-system/sections/04.tex)
   - [Current implementation and training boundaries](book/chapters/01-system/sections/04.tex)
5. [What constitutes evidence in an evolving ecosystem](book/chapters/01-system/sections/05.tex)
   - [Search scope and inclusion rules](book/chapters/01-system/sections/05.tex)
   - [Contemporary measurements with distinct estimands](book/chapters/01-system/sections/05.tex)
   - [Provenance and population boundaries](book/chapters/01-system/sections/05.tex)
6. [Three consistency contracts and their non-implication](book/chapters/01-system/sections/06.tex)
   - [From preservation contracts to corrective evidence](book/chapters/01-system/sections/06.tex)
7. [Cross-layer questions that organize the analysis](book/chapters/01-system/sections/07.tex)

#### C02 [Probabilistic State, Decision Processes, and Statistical Identification](book/chapters/02-mathematics/chapter.tex)

**Objective and analytical output.** Stopped deployed action laws; bounded Bayes-risk compression gap; duration-aware control; finite and simultaneous evidence with explicit support conditions.

**Contemporary evidence anchor.** MemoryWalker behavior conditioning, pinned Agent Lightning probability dataflow, and REUSE adaptive-promotion assumptions.

**Prerequisites.** [C01](book/chapters/01-system/chapter.tex)

**Planned allocation.** 11 substantive pages. **Source review.** 29 October 2026.

1. [Conditional prediction and observable information](book/chapters/02-mathematics/sections/01.tex)
2. [Information loss and decision-relevant state](book/chapters/02-mathematics/sections/02.tex)
   - [A bounded decision-loss consequence](book/chapters/02-mathematics/sections/02.tex)
3. [Partial observability and beliefs](book/chapters/02-mathematics/sections/03.tex)
4. [Optimization and policy-gradient identities](book/chapters/02-mathematics/sections/04.tex)
5. [Risk calibration and constrained decisions](book/chapters/02-mathematics/sections/05.tex)
6. [Statistical comparison and adaptive selection](book/chapters/02-mathematics/sections/06.tex)
   - [Simultaneous evidence for fixed candidates](book/chapters/02-mathematics/sections/06.tex)
7. [From equations to falsifiable implementation claims](book/chapters/02-mathematics/sections/07.tex)

### Model computation and interactive learning

#### C03 [Foundation Model Policies: Tokenization, Architectures, and Action Interfaces](book/chapters/03-models/chapter.tex)

**Objective and analytical output.** A stopped deployed action law, explicit rejection mass, and model-decoder-parser-executor boundaries.

**Contemporary evidence anchor.** DeepSeek V4.1 prefill reuse, looped shared-cache prediction, and DeepSeek V3 latent attention.

**Prerequisites.** [C01](book/chapters/01-system/chapter.tex), [C02](book/chapters/02-mathematics/chapter.tex)

**Planned allocation.** 11 substantive pages. **Source review.** 29 October 2026.

1. [DeepSeek V4.1 and architecture level prefill reuse](book/chapters/03-models/sections/00-frontier.tex)
2. [The model distribution and the executed policy](book/chapters/03-models/sections/01.tex)
3. [Tokenization as a measurement and interface choice](book/chapters/03-models/sections/02.tex)
4. [Architectural state and access to history](book/chapters/03-models/sections/03.tex)
   - [Shared computational state in looped Transformers](book/chapters/03-models/sections/03.tex)
5. [A resource model at the policy boundary](book/chapters/03-models/sections/04.tex)
6. [From model output to a typed operation](book/chapters/03-models/sections/05.tex)
7. [Reproducible implementation and discriminating experiments](book/chapters/03-models/sections/06.tex)
8. [Implications for stateful agents](book/chapters/03-models/sections/07.tex)

#### C04 [IO-Aware Attention Kernels and Computational State Allocation](book/chapters/04-attention/chapter.tex)

**Objective and analytical output.** Online normalization invariants, finite-precision obligations, and logical-to-physical cache ownership.

**Contemporary evidence anchor.** FlashAttention-4 kernel constraints, compressed-position phase effects, and pinned vLLM cache allocation.

**Prerequisites.** [C02](book/chapters/02-mathematics/chapter.tex), [C03](book/chapters/03-models/chapter.tex)

**Planned allocation.** 11 substantive pages. **Source review.** 29 October 2026.

1. [FlashAttention 4 and asymmetric hardware scaling](book/chapters/04-attention/sections/00-frontier.tex)
2. [The computation being optimized](book/chapters/04-attention/sections/01.tex)
   - [Online normalization and tiled exact attention](book/chapters/04-attention/sections/02.tex)
3. [KV growth and the difference between storage and knowledge](book/chapters/04-attention/sections/03.tex)
4. [Paged allocation and shared prefixes](book/chapters/04-attention/sections/04.tex)
5. [Bandwidth limits and latency distributions](book/chapters/04-attention/sections/05.tex)
6. [Approximate caches and a bounded perturbation argument](book/chapters/04-attention/sections/06.tex)
   - [Compression phase is a distinct positional variable](book/chapters/04-attention/sections/06.tex)
7. [Implementation verification and workload design](book/chapters/04-attention/sections/07.tex)
8. [When recomputation is mathematically necessary](book/chapters/04-attention/sections/08.tex)

#### C05 [Predictive Representation Learning and Multimodal State Abstraction](book/chapters/05-representations/chapter.tex)

**Objective and analytical output.** Representation-loss and downstream-control contracts, with predictive features distinguished from interventional evidence.

**Contemporary evidence anchor.** V-JEPA 2.1 dense supervision, V-JEPA Policy context-key coupling, and latent projection for control.

**Prerequisites.** [C02](book/chapters/02-mathematics/chapter.tex), [C03](book/chapters/03-models/chapter.tex)

**Planned allocation.** 11 substantive pages. **Source review.** 29 October 2026.

1. [Dense predictive features and world action coupling in 2026](book/chapters/05-representations/sections/00-frontier.tex)
2. [Representation quality is relative to a decision](book/chapters/05-representations/sections/01.tex)
   - [A decision-preservation test for learned abstraction](book/chapters/05-representations/sections/08.tex)
   - [Directed progress and finite-budget reachability](book/chapters/05-representations/sections/08.tex)
   - [Latent projection and the difference between predictability and control](book/chapters/05-representations/sections/08.tex)
3. [Patch encoders and the cost of visual detail](book/chapters/05-representations/sections/02.tex)
4. [Contrastive alignment and what it identifies](book/chapters/05-representations/sections/03.tex)
5. [Joint embedding prediction and the collapse question](book/chapters/05-representations/sections/04.tex)
6. [Multimodal fusion and executable grounding](book/chapters/05-representations/sections/05.tex)
7. [Temporal sampling and observation freshness](book/chapters/05-representations/sections/06.tex)
8. [Implementation and controlled comparison](book/chapters/05-representations/sections/07.tex)

#### C06 [Action-Conditioned World Models, Diffusion, and Model-Based Control](book/chapters/06-world_models/chapter.tex)

**Objective and analytical output.** Typed imagined-versus-observed rollouts, response-consistency checks, and action-conditioned implementation contracts.

**Contemporary evidence anchor.** LeFlow and DualWM action coupling; Trace2Env, WildAWM and Qwen-AgentWorld distinguish reconstructed, executable and generated transitions.

**Prerequisites.** [C02](book/chapters/02-mathematics/chapter.tex), [C05](book/chapters/05-representations/chapter.tex)

**Planned allocation.** 11 substantive pages. **Source review.** 29 October 2026.

1. [LeFlow and amortized latent trajectory planning](book/chapters/06-world_models/sections/00-frontier.tex)
2. [Prediction under intervention](book/chapters/06-world_models/sections/01.tex)
   - [Latent dynamics and learning objectives](book/chapters/06-world_models/sections/02.tex)
   - [Two temporal scales require an executable refinement interface](book/chapters/06-world_models/sections/02.tex)
3. [Compounding error and a finite-horizon bound](book/chapters/06-world_models/sections/03.tex)
4. [Diffusion as a conditional generative mechanism](book/chapters/06-world_models/sections/04.tex)
5. [Flow matching and trajectory parameterization](book/chapters/06-world_models/sections/05.tex)
6. [Executable worlds for language-model agents](book/chapters/06-world_models/sections/06.tex)
   - [Current action conditioned implementations](book/chapters/06-world_models/sections/06.tex)
   - [Trace reconstruction and the scope of a simulated fact](book/chapters/06-world_models/sections/06.tex)
   - [Generated executable worlds and learned response simulators](book/chapters/06-world_models/sections/06.tex)
7. [Experiments that separate prediction from control](book/chapters/06-world_models/sections/07.tex)
8. [Practical limits of imagination](book/chapters/06-world_models/sections/08.tex)

#### C07 [Pretraining Objectives, Scaling, and Distributed Optimization](book/chapters/07-pretraining/chapter.tex)

**Objective and analytical output.** Global token-weighted gradients, partition-aware numerical checks, and reproducible model/data/optimizer state.

**Contemporary evidence anchor.** DeepSeek V4 training stages, PaW predictive supervision, DGS support targets, and pinned distributed optimizer paths.

**Prerequisites.** [C02](book/chapters/02-mathematics/chapter.tex), [C03](book/chapters/03-models/chapter.tex), [C04](book/chapters/04-attention/chapter.tex)

**Planned allocation.** 11 substantive pages. **Source review.** 29 October 2026.

1. [DeepSeek V4 staged pretraining and distributed state](book/chapters/07-pretraining/sections/00-frontier.tex)
2. [What pretraining supplies to an agent](book/chapters/07-pretraining/sections/01.tex)
   - [Data integrity and causal trace construction](book/chapters/07-pretraining/sections/05.tex)
3. [Scaling laws under an explicit compute model](book/chapters/07-pretraining/sections/02.tex)
4. [Optimizer state and distributed memory accounting](book/chapters/07-pretraining/sections/03.tex)
5. [Communication and parallel decomposition](book/chapters/07-pretraining/sections/04.tex)
6. [Numerical stability and reproducibility](book/chapters/07-pretraining/sections/06.tex)
7. [A worked training-budget calculation](book/chapters/07-pretraining/sections/07.tex)
8. [Experiments linking infrastructure to behavior](book/chapters/07-pretraining/sections/08.tex)
   - [Predictive supervision inside policy optimization](book/chapters/07-pretraining/sections/08.tex)

#### C08 [Post-Training Objectives for Interactive and Tool-Using Policies](book/chapters/08-posttraining/chapter.tex)

**Objective and analytical output.** Behavior-conditioned likelihoods, explicit normalization, reference-score compatibility, and shared-outcome segmented trajectories.

**Contemporary evidence anchor.** Native-quantized policy distillation, OpenForge, MOLT, MemoryWalker, and pinned TRL loss reductions.

**Prerequisites.** [C02](book/chapters/02-mathematics/chapter.tex), [C03](book/chapters/03-models/chapter.tex), [C07](book/chapters/07-pretraining/chapter.tex)

**Planned allocation.** 11 substantive pages. **Source review.** 29 October 2026.

1. [On policy distillation with precision matched rollout](book/chapters/08-posttraining/sections/00-frontier.tex)
2. [Behavioral targets and trajectory supervision](book/chapters/08-posttraining/sections/01.tex)
   - [KL-regularized control and preference optimization](book/chapters/08-posttraining/sections/02.tex)
3. [Policy gradients and the likelihood-ratio contract](book/chapters/08-posttraining/sections/03.tex)
4. [Group-relative advantages and sparse outcomes](book/chapters/08-posttraining/sections/04.tex)
5. [Executable rewards and verifier error](book/chapters/08-posttraining/sections/05.tex)
6. [Context edits and post-training consistency](book/chapters/08-posttraining/sections/06.tex)
7. [Implementation paths and controlled training studies](book/chapters/08-posttraining/sections/07.tex)
   - [Harness-native reinforcement learning and segmented behavior policies](book/chapters/08-posttraining/sections/07.tex)
8. [Credit assignment across tools and memory](book/chapters/08-posttraining/sections/08.tex)

#### C09 [Inference-Time Search, Verification, and Metareasoning](book/chapters/09-reasoning/chapter.tex)

**Objective and analytical output.** A cost-bounded search and verifier design with coverage, correlation and selection assumptions made explicit.

**Contemporary evidence anchor.** MetaReason budget allocation, executable search baselines, and separate coverage and selection evidence.

**Prerequisites.** [C03](book/chapters/03-models/chapter.tex), [C08](book/chapters/08-posttraining/chapter.tex)

**Planned allocation.** 11 substantive pages. **Source review.** 29 October 2026.

1. [Meta reasoning controllers and artifact selection in 2026](book/chapters/09-reasoning/sections/07.tex)
2. [A conditional computation rather than a verbal certificate](book/chapters/09-reasoning/sections/01.tex)
3. [Sampling coverage and repeated reliability](book/chapters/09-reasoning/sections/02.tex)
4. [Self-consistency and answer aggregation](book/chapters/09-reasoning/sections/03.tex)
5. [Selection error grows with the search space](book/chapters/09-reasoning/sections/04.tex)
   - [A calculated selector with an imperfect validator](book/chapters/09-reasoning/sections/04.tex)
6. [Structured search and the granularity of a thought](book/chapters/09-reasoning/sections/05.tex)
7. [Value of computation and stopping](book/chapters/09-reasoning/sections/06.tex)
8. [Experiments and failure attribution](book/chapters/09-reasoning/sections/08.tex)

#### C10 [Closed-Loop Planning with Partial Observability and Fallible Feedback](book/chapters/10-planning/chapter.tex)

**Objective and analytical output.** State-indexed planning, conditional trial hazards, and execution-time validation of observed preconditions.

**Contemporary evidence anchor.** WorldEvolver v2 memory-conditioned foresight, per-call gate behavior, and adaptive-trial evaluation.

**Prerequisites.** [C02](book/chapters/02-mathematics/chapter.tex), [C06](book/chapters/06-world_models/chapter.tex), [C09](book/chapters/09-reasoning/chapter.tex)

**Planned allocation.** 11 substantive pages. **Source review.** 29 October 2026.

1. [WorldEvolver and memory conditioned foresight](book/chapters/10-planning/sections/08.tex)
2. [Goals must refer to external state](book/chapters/10-planning/sections/01.tex)
3. [Belief states and information-gathering actions](book/chapters/10-planning/sections/02.tex)
4. [Plan contracts and compositional verification](book/chapters/10-planning/sections/03.tex)
5. [Receding-horizon execution and grounded feedback](book/chapters/10-planning/sections/04.tex)
6. [Self-correction can also damage correct work](book/chapters/10-planning/sections/05.tex)
7. [Hierarchical plans and reusable skills](book/chapters/10-planning/sections/06.tex)
8. [Partial effects and recovery planning](book/chapters/10-planning/sections/07.tex)
9. [A reproducible planning evaluation](book/chapters/10-planning/sections/09.tex)

### Context, sessions, memory, and conditioning

#### C11 [Long-Context Capability and Decision-Relevant Information](book/chapters/11-long_context/chapter.tex)

**Objective and analytical output.** Information sufficiency versus fixed-policy behavior, context accessibility diagnostics, and explicit KV/workload accounting.

**Contemporary evidence anchor.** The Compaction Cliff, pinned RULER generation/evaluation, and 2026 rate-distortion and selective-memory taxonomies.

**Prerequisites.** [C03](book/chapters/03-models/chapter.tex), [C04](book/chapters/04-attention/chapter.tex), [C09](book/chapters/09-reasoning/chapter.tex)

**Planned allocation.** 11 substantive pages. **Source review.** 29 October 2026.

1. [Capacity is a constraint on an inference procedure](book/chapters/11-long_context/sections/section-01.tex)
2. [A sufficiency criterion for retained state](book/chapters/11-long_context/sections/section-02.tex)
3. [Position effects and compositional difficulty](book/chapters/11-long_context/sections/section-03.tex)
4. [Training distributions and length generalization](book/chapters/11-long_context/sections/section-04.tex)
5. [Computation and memory over an interaction horizon](book/chapters/11-long_context/sections/section-05.tex)
6. [Experimental designs that isolate context use](book/chapters/11-long_context/sections/section-06.tex)
7. [A worked capacity and decision example](book/chapters/11-long_context/sections/section-07.tex)
8. [Effective context as controlled state](book/chapters/11-long_context/sections/section-08.tex)

#### C12 [Context Transformation: Selection, Compaction, and Policy-Controlled Editing](book/chapters/12-context_control/chapter.tex)

**Objective and analytical output.** A budget-admitted context transformation, complete edit lineage, action-time conditioning, and scoped cache-reuse approximation.

**Contemporary evidence anchor.** ContextPilot, CompactionRL v2, TRACE v2, PAIR, CLM and transparent compaction expose distinct editing and recovery boundaries.

**Prerequisites.** [C08](book/chapters/08-posttraining/chapter.tex), [C11](book/chapters/11-long_context/chapter.tex)

**Planned allocation.** 11 substantive pages. **Source review.** 29 October 2026.

1. [The working view as a controlled variable](book/chapters/12-context_control/sections/section-01.tex)
2. [Selection before abstraction](book/chapters/12-context_control/sections/section-02.tex)
3. [Reversible offload and explicit context actions](book/chapters/12-context_control/sections/section-03.tex)
4. [Compaction triggers and delayed credit](book/chapters/12-context_control/sections/section-04.tex)
5. [Editing and cache validity](book/chapters/12-context_control/sections/section-05.tex)
6. [A worked decision-preservation analysis](book/chapters/12-context_control/sections/section-06.tex)
7. [Evidence comparisons and causal boundaries](book/chapters/12-context_control/sections/section-07.tex)
8. [Failure recovery and implementation discipline](book/chapters/12-context_control/sections/section-08.tex)

#### C13 [Session Semantics, Event Histories, and Recoverable Execution State](book/chapters/13-sessions/chapter.tex)

**Objective and analytical output.** An event/effect history with defined resumption and concurrency semantics.

**Contemporary evidence anchor.** ACM snapshot/archive code paths and current durable-session contracts.

**Prerequisites.** [C01](book/chapters/01-system/chapter.tex), [C12](book/chapters/12-context_control/chapter.tex)

**Planned allocation.** 11 substantive pages. **Source review.** 29 October 2026.

1. [Session identity is a semantic boundary](book/chapters/13-sessions/sections/section-01.tex)
2. [Events as evidence rather than prose](book/chapters/13-sessions/sections/section-02.tex)
3. [Reducers checkpoints and replay](book/chapters/13-sessions/sections/section-03.tex)
4. [External effects and the ambiguous timeout](book/chapters/13-sessions/sections/section-04.tex)
5. [Concurrency ownership and session forks](book/chapters/13-sessions/sections/section-05.tex)
6. [Retention deletion and provenance boundaries](book/chapters/13-sessions/sections/section-06.tex)
7. [A failure-oriented evaluation protocol](book/chapters/13-sessions/sections/section-07.tex)
8. [A reference contract for continuity](book/chapters/13-sessions/sections/section-08.tex)

#### C14 [Persistent Memory: Writing, Consolidation, Validity, and Influence](book/chapters/14-memory/chapter.tex)

**Objective and analytical output.** Typed memory with provenance, temporal validity, permissions, and influence tests.

**Contemporary evidence anchor.** RecMem, InMind, Hy-Memory, and current prospective memory-use mechanisms.

**Prerequisites.** [C05](book/chapters/05-representations/chapter.tex), [C11](book/chapters/11-long_context/chapter.tex), [C13](book/chapters/13-sessions/chapter.tex)

**Planned allocation.** 13 substantive pages. **Source review.** 29 October 2026.

1. [Memory functions and physical substrates](book/chapters/14-memory/sections/section-01.tex)
2. [Admission as a constrained decision](book/chapters/14-memory/sections/section-02.tex)
3. [Episodic records and abstraction loss](book/chapters/14-memory/sections/section-03.tex)
4. [Semantic memory and the status of a proposition](book/chapters/14-memory/sections/section-04.tex)
5. [Hierarchy access and complete lifecycle cost](book/chapters/14-memory/sections/section-05.tex)
6. [Temporal validity conflicts and forgetting](book/chapters/14-memory/sections/section-06.tex)
7. [Retrieval does not imply appropriate use](book/chapters/14-memory/sections/section-07.tex)
   - [Identifying memory influence](book/chapters/14-memory/sections/section-07.tex)
8. [Memory transactions and a reference test suite](book/chapters/14-memory/sections/section-08.tex)

#### C15 [Procedural Memory and the Lifecycle of Executable Skills](book/chapters/15-skills/chapter.tex)

**Objective and analytical output.** Versioned procedural hypotheses, applicability and authority checks, maintenance evidence, and conditional failure-composition bounds.

**Contemporary evidence anchor.** HyperSkill retrieval/maintenance code and portable skill contracts.

**Prerequisites.** [C10](book/chapters/10-planning/chapter.tex), [C14](book/chapters/14-memory/chapter.tex)

**Planned allocation.** 11 substantive pages. **Source review.** 29 October 2026.

1. [A procedure has preconditions and effects](book/chapters/15-skills/sections/section-01.tex)
2. [Extracting procedures from experience](book/chapters/15-skills/sections/section-02.tex)
3. [Hypergraphs preserve trajectory membership](book/chapters/15-skills/sections/section-03.tex)
4. [Quality-guided maintenance and its assumptions](book/chapters/15-skills/sections/section-04.tex)
5. [An inspectable execution trace](book/chapters/15-skills/sections/section-05.tex)
6. [Reported results and unresolved attribution](book/chapters/15-skills/sections/section-06.tex)
7. [Compatibility authority and the skill supply chain](book/chapters/15-skills/sections/section-07.tex)
8. [Consolidation as controlled hypothesis revision](book/chapters/15-skills/sections/section-08.tex)

#### C16 [Retrieval Policies, Evidence Assembly, and Grounded Execution](book/chapters/16-retrieval/chapter.tex)

**Objective and analytical output.** An auditable evidence path and finite-horizon query controller with sufficient state, explicit kernels and stopping reasons.

**Contemporary evidence anchor.** JAM, MRAgent, MATM, MemCalib, ReFind v2 and LGM v2 distinguish adaptive access from representation and reranking.

**Prerequisites.** [C05](book/chapters/05-representations/chapter.tex), [C14](book/chapters/14-memory/chapter.tex)

**Planned allocation.** 11 substantive pages. **Source review.** 29 October 2026.

1. [Retrieval selects evidence for an action](book/chapters/16-retrieval/sections/section-01.tex)
2. [Index units and information boundaries](book/chapters/16-retrieval/sections/section-02.tex)
3. [Query construction and adaptive access](book/chapters/16-retrieval/sections/section-03.tex)
4. [State-conditioned procedural retrieval](book/chapters/16-retrieval/sections/section-04.tex)
5. [Evidence packing attribution and influence](book/chapters/16-retrieval/sections/section-05.tex)
6. [A worked multi-step evidence dependency](book/chapters/16-retrieval/sections/section-06.tex)
7. [Evaluation contamination and uncertainty](book/chapters/16-retrieval/sections/section-07.tex)
8. [An execution contract for grounded retrieval](book/chapters/16-retrieval/sections/section-08.tex)

#### C17 [Conditioning Consistency across Context, Memory, and Policy Updates](book/chapters/17-consistency/chapter.tex)

**Objective and analytical output.** Compatibility conditions for training, inference, memory, and context views.

**Contemporary evidence anchor.** MemoryWalker, CODA, and CLM state transformations.

**Prerequisites.** [C08](book/chapters/08-posttraining/chapter.tex), [C12](book/chapters/12-context_control/chapter.tex), [C13](book/chapters/13-sessions/chapter.tex), [C14](book/chapters/14-memory/chapter.tex), [C15](book/chapters/15-skills/chapter.tex), [C16](book/chapters/16-retrieval/chapter.tex)

**Planned allocation.** 11 substantive pages. **Source review.** 29 October 2026.

1. [One decision depends on several versions](book/chapters/17-consistency/sections/section-01.tex)
2. [The conditioning record is part of the data](book/chapters/17-consistency/sections/section-02.tex)
3. [Likelihood ratios require support and the right history](book/chapters/17-consistency/sections/section-03.tex)
4. [A bounded behavior-preservation proposition](book/chapters/17-consistency/sections/section-04.tex)
5. [Memory transactions and semantic validity](book/chapters/17-consistency/sections/section-05.tex)
6. [Model index and tool migration](book/chapters/17-consistency/sections/section-06.tex)
7. [Authority must survive every transformation](book/chapters/17-consistency/sections/section-07.tex)
8. [A consistency audit with causal counterexamples](book/chapters/17-consistency/sections/section-08.tex)

### Tools, protocols, execution, and domain systems

#### C18 [Tool Discovery, Routing, and Typed Execution Contracts](book/chapters/18-tools/chapter.tex)

**Objective and analytical output.** Typed effect outcomes, current feasible routes, simultaneous-error regret bounds, and configured privilege enforcement.

**Contemporary evidence anchor.** HyperTool, Uno-Orchestra, PruneTIR, and permission-aware tool routing.

**Prerequisites.** [C03](book/chapters/03-models/chapter.tex), [C10](book/chapters/10-planning/chapter.tex), [C17](book/chapters/17-consistency/chapter.tex)

**Planned allocation.** 11 substantive pages. **Source review.** 29 October 2026.

1. [A tool call is a typed state transition](book/chapters/18-tools/sections/section-01.tex)
2. [Discovery changes the action space](book/chapters/18-tools/sections/section-02.tex)
3. [Routing as constrained resource allocation](book/chapters/18-tools/sections/section-03.tex)
4. [Argument construction and result validation](book/chapters/18-tools/sections/section-04.tex)
5. [Execution granularity and local programs](book/chapters/18-tools/sections/section-05.tex)
6. [Retry pruning and failure memory](book/chapters/18-tools/sections/section-06.tex)
7. [Privilege control at the dispatch boundary](book/chapters/18-tools/sections/section-07.tex)
8. [A tool-use experiment that can falsify the mechanism](book/chapters/18-tools/sections/section-08.tex)

#### C19 [Versioned Interoperability: MCP, A2A, and Protocol Boundaries](book/chapters/19-protocols/chapter.tex)

**Objective and analytical output.** A versioned exchange whose transport guarantees remain separate from truth and permission.

**Contemporary evidence anchor.** MCP 2026-07-28 normative semantics and current A2A lifecycle contracts.

**Prerequisites.** [C13](book/chapters/13-sessions/chapter.tex), [C18](book/chapters/18-tools/chapter.tex)

**Planned allocation.** 11 substantive pages. **Source review.** 29 October 2026.

1. [Protocol compatibility is not agent competence](book/chapters/19-protocols/sections/section-01.tex)
2. [Modern MCP declares versions on every request](book/chapters/19-protocols/sections/section-02.tex)
3. [Tools resources prompts and skills remain distinct](book/chapters/19-protocols/sections/section-03.tex)
4. [Transport statelessness and explicit durable work](book/chapters/19-protocols/sections/section-04.tex)
5. [Authorization is separate from declared identity](book/chapters/19-protocols/sections/section-05.tex)
6. [A2A tasks artifacts and delegated autonomy](book/chapters/19-protocols/sections/section-06.tex)
7. [A concrete cross-protocol execution trace](book/chapters/19-protocols/sections/section-07.tex)
8. [Conformance performance and residual uncertainty](book/chapters/19-protocols/sections/section-08.tex)

#### C20 [Agent Harnesses: Control Flow, Isolation, and Durable Effects](book/chapters/20-harnesses/chapter.tex)

**Objective and analytical output.** Acknowledged journal transitions, independently authorized reconciliation, and linearizable admission/settlement accounting.

**Contemporary evidence anchor.** Harness^2 stage accounting, RRSI v3 selection controls, and current runtime/effect boundaries.

**Prerequisites.** [C10](book/chapters/10-planning/chapter.tex), [C13](book/chapters/13-sessions/chapter.tex), [C17](book/chapters/17-consistency/chapter.tex), [C18](book/chapters/18-tools/chapter.tex), [C19](book/chapters/19-protocols/chapter.tex)

**Planned allocation.** 11 substantive pages. **Source review.** 29 October 2026.

1. [The effective policy includes the harness](book/chapters/20-harnesses/sections/01.tex)
2. [Execution state and semantic commitments](book/chapters/20-harnesses/sections/02.tex)
3. [Crash consistency and uncertain effects](book/chapters/20-harnesses/sections/03.tex)
4. [Context construction is runtime scheduling](book/chapters/20-harnesses/sections/04.tex)
5. [Budgets cancellation and backpressure](book/chapters/20-harnesses/sections/05.tex)
6. [Implementation boundaries and evidence](book/chapters/20-harnesses/sections/06.tex)
7. [A worked analysis of a recoverable repository workflow](book/chapters/20-harnesses/sections/07.tex)

#### C21 [Multi-Agent Coordination, Information Routing, and Shared State](book/chapters/21-orchestration/chapter.tex)

**Objective and analytical output.** Coordination traffic and latent-payload accounting, representation compatibility, and evidence-preserving shared-state interfaces.

**Contemporary evidence anchor.** LatComm and Interlat representation channels, coding-team stage allocation, and independent-sample controls.

**Prerequisites.** [C09](book/chapters/09-reasoning/chapter.tex), [C17](book/chapters/17-consistency/chapter.tex), [C20](book/chapters/20-harnesses/chapter.tex)

**Planned allocation.** 11 substantive pages. **Source review.** 29 October 2026.

1. [Task graphs and the value of decomposition](book/chapters/21-orchestration/sections/01.tex)
2. [Independence diversity and correlated error](book/chapters/21-orchestration/sections/02.tex)
3. [Messages as evidence-bearing interfaces](book/chapters/21-orchestration/sections/03.tex)
   - [Learned latent channels and representation compatibility](book/chapters/21-orchestration/sections/03.tex)
4. [Shared memory and conflicting writes](book/chapters/21-orchestration/sections/04.tex)
5. [Ownership cancellation and failure propagation](book/chapters/21-orchestration/sections/05.tex)
6. [Experiments that isolate coordination mechanisms](book/chapters/21-orchestration/sections/06.tex)
7. [A bounded integration protocol](book/chapters/21-orchestration/sections/07.tex)
8. [When isolation is the stronger coordination mechanism](book/chapters/21-orchestration/sections/08.tex)

#### C22 [Agent Development Frameworks, SDKs, and Managed Runtimes](book/chapters/22-frameworks/chapter.tex)

**Objective and analytical output.** Version-specific SDK and runtime contracts, deterministic migration criteria, and conformance before performance ranking.

**Contemporary evidence anchor.** October 2026 release snapshots and exact runtime/persistence interfaces.

**Prerequisites.** [C19](book/chapters/19-protocols/chapter.tex), [C20](book/chapters/20-harnesses/chapter.tex), [C21](book/chapters/21-orchestration/chapter.tex)

**Planned allocation.** 11 substantive pages. **Source review.** 29 October 2026.

1. [A semantic basis for framework comparison](book/chapters/22-frameworks/sections/01.tex)
2. [Graph runtimes and opinionated harnesses](book/chapters/22-frameworks/sections/02.tex)
3. [Typed SDKs and model-owned loops](book/chapters/22-frameworks/sections/03.tex)
4. [Development kits interoperability and language boundaries](book/chapters/22-frameworks/sections/04.tex)
5. [Role-specific framework and runtime inventory](book/chapters/22-frameworks/sections/05.tex)
6. [Licensing lifecycle and migration evidence](book/chapters/22-frameworks/sections/06.tex)
   - [Release-specific evidence at the October cutoff](book/chapters/22-frameworks/sections/06.tex)
7. [A conformance suite before performance ranking](book/chapters/22-frameworks/sections/07.tex)
8. [From public API to executable control path](book/chapters/22-frameworks/sections/08.tex)

#### C23 [Repository, Terminal, and Computer-Use Agents](book/chapters/23-coding/chapter.tex)

**Objective and analytical output.** Artifact attestations, grader-mixture identification, serial cost-overshoot limits, and geometric click-margin conditions.

**Contemporary evidence anchor.** TerminalHorizon v2, pinned execution-loop accounting, current coding interfaces, and AgentHorizon grading boundaries.

**Prerequisites.** [C10](book/chapters/10-planning/chapter.tex), [C18](book/chapters/18-tools/chapter.tex), [C20](book/chapters/20-harnesses/chapter.tex), [C22](book/chapters/22-frameworks/chapter.tex)

**Planned allocation.** 11 substantive pages. **Source review.** 29 October 2026.

1. [Repository state as an executable environment](book/chapters/23-coding/sections/01.tex)
2. [Specifications tests and evaluator blind spots](book/chapters/23-coding/sections/02.tex)
3. [Terminal trajectories and learned execution policies](book/chapters/23-coding/sections/03.tex)
4. [Computer use grounding and hidden state](book/chapters/23-coding/sections/04.tex)
5. [Coding product families and observable tests](book/chapters/23-coding/sections/05.tex)
6. [A budget-matched evaluation protocol](book/chapters/23-coding/sections/06.tex)
7. [Artifact authority and reviewable completion](book/chapters/23-coding/sections/07.tex)
8. [A concrete grading failure and its discriminating controls](book/chapters/23-coding/sections/08.tex)

#### C24 [Research, Enterprise, and Domain-Specific Agent Systems](book/chapters/24-products/chapter.tex)

**Objective and analytical output.** Domain-specific grounding, state, review, and operational evidence.

**Contemporary evidence anchor.** Knowledge Activation, ALE and biological-agent evidence distinguish reported perceptions, benchmark outcomes and closed-loop empirical validation.

**Prerequisites.** [C16](book/chapters/16-retrieval/chapter.tex), [C20](book/chapters/20-harnesses/chapter.tex), [C21](book/chapters/21-orchestration/chapter.tex), [C22](book/chapters/22-frameworks/chapter.tex)

**Planned allocation.** 11 substantive pages. **Source review.** 29 October 2026.

1. [Research as evidence acquisition and revision](book/chapters/24-products/sections/01.tex)
   - [Biological agents: executable methods and empirical feedback](book/chapters/24-products/sections/01.tex)
   - [An October closed-loop result and its attribution limits](book/chapters/24-products/sections/01.tex)
   - [Replay laboratories, digital twins and live measurements](book/chapters/24-products/sections/01.tex)
2. [Enterprise grounding and permission propagation](book/chapters/24-products/sections/02.tex)
3. [Memory engines are distinct policy components](book/chapters/24-products/sections/03.tex)
4. [Work-product and vertical-system inventory](book/chapters/24-products/sections/04.tex)
5. [Causal evidence for organizational benefit](book/chapters/24-products/sections/05.tex)
6. [Professional benchmarks and economic interpretation](book/chapters/24-products/sections/06.tex)
7. [A reproducible evidence-review transaction](book/chapters/24-products/sections/07.tex)
8. [A changing-policy case in a shared knowledge workspace](book/chapters/24-products/sections/08.tex)

### Inspection, evaluation, security, and alignment

#### C25 [Model Inspection, Executable Verification, and Evaluator Reliability](book/chapters/25-verification/chapter.tex)

**Objective and analytical output.** Conditional verifier utility, adaptive inspection estimands, and scoped assurance claims.

**Contemporary evidence anchor.** TestJack, AgentHorizon, and current inspector/verifier failure cases.

**Prerequisites.** [C03](book/chapters/03-models/chapter.tex), [C09](book/chapters/09-reasoning/chapter.tex), [C20](book/chapters/20-harnesses/chapter.tex)

**Planned allocation.** 11 substantive pages. **Source review.** 29 October 2026.

1. [Properties observations and assurance boundaries](book/chapters/25-verification/sections/01.tex)
2. [Causal interventions in model computation](book/chapters/25-verification/sections/02.tex)
3. [Sparse features and their evaluation](book/chapters/25-verification/sections/03.tex)
   - [The 2026 monitorability boundary](book/chapters/25-verification/sections/03.tex)
4. [Quality gates as fallible classifiers](book/chapters/25-verification/sections/04.tex)
5. [Dynamic tests and requirement-grounded witnesses](book/chapters/25-verification/sections/05.tex)
6. [Judging long multimodal trajectories](book/chapters/25-verification/sections/06.tex)
7. [Verification experiments and implementation traceability](book/chapters/25-verification/sections/07.tex)
8. [A worked gate analysis with adaptive selection](book/chapters/25-verification/sections/08.tex)

#### C26 [Evaluation Harnesses, Contamination, and Statistical Validity](book/chapters/26-evaluation/chapter.tex)

**Objective and analytical output.** Population and denominator contracts, task-mixture reliability estimands, and restricted adaptive-reuse evidence.

**Contemporary evidence anchor.** 2026 evaluation findings and versioned harness implementations.

**Prerequisites.** [C02](book/chapters/02-mathematics/chapter.tex), [C20](book/chapters/20-harnesses/chapter.tex), [C23](book/chapters/23-coding/chapter.tex), [C25](book/chapters/25-verification/chapter.tex)

**Planned allocation.** 11 substantive pages. **Source review.** 29 October 2026.

1. [Define the estimand before the leaderboard](book/chapters/26-evaluation/sections/01.tex)
2. [Harness construction and artifact identity](book/chapters/26-evaluation/sections/02.tex)
3. [Attempts reliability and selection](book/chapters/26-evaluation/sections/03.tex)
4. [Contamination information leakage and task lineage](book/chapters/26-evaluation/sections/04.tex)
   - [Interference through persistent state](book/chapters/26-evaluation/sections/04.tex)
5. [Uncertainty paired designs and dependence](book/chapters/26-evaluation/sections/05.tex)
6. [Ablations and causal mechanism claims](book/chapters/26-evaluation/sections/06.tex)
7. [Evaluator audits and reproducible reporting](book/chapters/26-evaluation/sections/07.tex)
8. [A concrete audit of a paired repository comparison](book/chapters/26-evaluation/sections/08.tex)

#### C27 [Longitudinal Evaluation of Memory, Adaptation, and Recovery](book/chapters/27-longitudinal/chapter.tex)

**Objective and analytical output.** A stream-level adaptation/recovery estimand and independent uncertainty unit.

**Contemporary evidence anchor.** InMind, MemCalib v3, fragility v2, survival and carryover controls.

**Prerequisites.** [C13](book/chapters/13-sessions/chapter.tex), [C14](book/chapters/14-memory/chapter.tex), [C15](book/chapters/15-skills/chapter.tex), [C17](book/chapters/17-consistency/chapter.tex), [C26](book/chapters/26-evaluation/chapter.tex)

**Planned allocation.** 11 substantive pages. **Source review.** 29 October 2026.

1. [Define horizon and the unit of continuity](book/chapters/27-longitudinal/sections/01.tex)
2. [Factor the memory pipeline](book/chapters/27-longitudinal/sections/02.tex)
3. [Implicit relevance and appropriate influence](book/chapters/27-longitudinal/sections/03.tex)
4. [Task order adaptation and hidden curricula](book/chapters/27-longitudinal/sections/04.tex)
5. [Temporal change deletion and migration](book/chapters/27-longitudinal/sections/05.tex)
6. [Horizon-dependent reliability and survival](book/chapters/27-longitudinal/sections/06.tex)
7. [A longitudinal implementation and reporting contract](book/chapters/27-longitudinal/sections/07.tex)
8. [A counterfactual session-stream experiment](book/chapters/27-longitudinal/sections/08.tex)
   - [What a counterfactual replay can identify](book/chapters/27-longitudinal/sections/08.tex)

#### C28 [Stateful Agent Security: Red-Team and Blue-Team Mechanisms](book/chapters/28-security/chapter.tex)

**Objective and analytical output.** An explicit adversary, attack surface, defense, and residual-risk evaluation.

**Contemporary evidence anchor.** DTap, ExploitGym, CyberGym-E2E, and versioned privilege enforcement.

**Prerequisites.** [C17](book/chapters/17-consistency/chapter.tex), [C18](book/chapters/18-tools/chapter.tex), [C19](book/chapters/19-protocols/chapter.tex), [C20](book/chapters/20-harnesses/chapter.tex), [C25](book/chapters/25-verification/chapter.tex), [C26](book/chapters/26-evaluation/chapter.tex)

**Planned allocation.** 11 substantive pages. **Source review.** 29 October 2026.

1. [Threat models and attacker capabilities](book/chapters/28-security/sections/01.tex)
2. [Injection across context tools and persistent memory](book/chapters/28-security/sections/02.tex)
3. [Least privilege and symbolic action controls](book/chapters/28-security/sections/03.tex)
   - [Open privilege can remain invisible to executed attacks](book/chapters/28-security/sections/03.tex)
4. [Controlled red-team platforms and judge validity](book/chapters/28-security/sections/04.tex)
   - [Attacker--defender self-play changes the data distribution](book/chapters/28-security/sections/04.tex)
   - [A modular adversarial interface is a measurement contract](book/chapters/28-security/sections/04.tex)
5. [Cyber capability is not agent compromise](book/chapters/28-security/sections/05.tex)
   - [Symbolic search, fuzzing, and static analysis have different oracles](book/chapters/28-security/sections/05.tex)
6. [Blue-team detection containment and recovery](book/chapters/28-security/sections/06.tex)
   - [Detection must precede the relevant commitment](book/chapters/28-security/sections/06.tex)
7. [Security metrics and evidence interpretation](book/chapters/28-security/sections/07.tex)
8. [A bounded policy-expansion and memory-poisoning case](book/chapters/28-security/sections/08.tex)

#### C29 [Alignment, Authorization, and Constrained Autonomy](book/chapters/29-alignment/chapter.tex)

**Objective and analytical output.** Expected-versus-enforced constraints, conservative grants, and commit-time authorization boundaries.

**Contemporary evidence anchor.** Current authority and approval semantics; model preferences are separated from enforcement.

**Prerequisites.** [C08](book/chapters/08-posttraining/chapter.tex), [C18](book/chapters/18-tools/chapter.tex), [C20](book/chapters/20-harnesses/chapter.tex), [C25](book/chapters/25-verification/chapter.tex), [C28](book/chapters/28-security/chapter.tex)

**Planned allocation.** 11 substantive pages. **Source review.** 29 October 2026.

1. [Objectives proxies and constrained policies](book/chapters/29-alignment/sections/01.tex)
2. [Instruction hierarchy and authority-bearing records](book/chapters/29-alignment/sections/02.tex)
3. [Constitutional and preference-based alignment](book/chapters/29-alignment/sections/03.tex)
   - [Automated safety adaptation and independent confirmation](book/chapters/29-alignment/sections/03.tex)
4. [Human review and the semantics of approval](book/chapters/29-alignment/sections/04.tex)
5. [Privacy purpose and the lifecycle of memory](book/chapters/29-alignment/sections/05.tex)
6. [Operational constraints and residual risk](book/chapters/29-alignment/sections/06.tex)
7. [Evaluation of authority and aligned behavior](book/chapters/29-alignment/sections/07.tex)
8. [A governed model-and-harness update](book/chapters/29-alignment/sections/08.tex)

### Adaptation, infrastructure, and cross-layer synthesis

#### C30 [Continual Adaptation and the Evidence for Recursive Self-Improvement](book/chapters/30-improvement/chapter.tex)

**Objective and analytical output.** Separate executor and improver estimands, restricted-feedback promotion, and frozen-pair compatibility versus training effects.

**Contemporary evidence anchor.** RRSI v3, Harness^2, AIDE^2, MASS, Self-HPO and Terminal-RSI v2.

**Prerequisites.** [C08](book/chapters/08-posttraining/chapter.tex), [C15](book/chapters/15-skills/chapter.tex), [C17](book/chapters/17-consistency/chapter.tex), [C25](book/chapters/25-verification/chapter.tex), [C26](book/chapters/26-evaluation/chapter.tex), [C27](book/chapters/27-longitudinal/chapter.tex), [C29](book/chapters/29-alignment/chapter.tex)

**Planned allocation.** 11 substantive pages. **Source review.** 29 October 2026.

1. [What changes when an agent improves](book/chapters/30-improvement/sections/01.tex)
2. [Selection pressure and finite-feedback overfitting](book/chapters/30-improvement/sections/02.tex)
3. [Task-local recursion and reusable improvement memory](book/chapters/30-improvement/sections/03.tex)
4. [Policy and harness co-adaptation](book/chapters/30-improvement/sections/04.tex)
5. [Continual memory maintenance as controlled adaptation](book/chapters/30-improvement/sections/05.tex)
6. [Testing the improver rather than its selected artifact](book/chapters/30-improvement/sections/06.tex)
7. [Bounds on claims and conditions for deployment](book/chapters/30-improvement/sections/07.tex)

#### C31 [Agentic Inference: Scheduling, Speculation, and Tiered State](book/chapters/31-serving/chapter.tex)

**Objective and analytical output.** Workload-conditional throughput and latency analysis, retry/queueing assumptions, and valid cache-state reuse.

**Contemporary evidence anchor.** 2026 tiered vLLM state, hybrid cache semantics, and agentic serving workloads.

**Prerequisites.** [C04](book/chapters/04-attention/chapter.tex), [C12](book/chapters/12-context_control/chapter.tex), [C20](book/chapters/20-harnesses/chapter.tex)

**Planned allocation.** 11 substantive pages. **Source review.** 29 October 2026.

1. [The workload is a sequence of interrupted computations](book/chapters/31-serving/sections/01.tex)
2. [A complete capacity calculation](book/chapters/31-serving/sections/02.tex)
3. [Bandwidth arithmetic and the decode bottleneck](book/chapters/31-serving/sections/03.tex)
4. [Exact reuse, partial reuse, and cache identity](book/chapters/31-serving/sections/04.tex)
5. [Quantization speculation and structured action outputs](book/chapters/31-serving/sections/05.tex)
6. [Memory-conditioned speculation and exact verification](book/chapters/31-serving/sections/06.tex)
7. [Scheduling disaggregation and queueing](book/chapters/31-serving/sections/07.tex)
8. [A reproducible serving experiment](book/chapters/31-serving/sections/08.tex)

#### C32 [Operational Assurance: Monitoring, Migration, Rollback, and Recovery](book/chapters/32-operations/chapter.tex)

**Objective and analytical output.** A release compatibility closure, decoder-aware manifests, and bounded local recovery separated from eventual effect resolution.

**Contemporary evidence anchor.** October session/runtime interfaces and compatibility-aware release/recovery analysis.

**Prerequisites.** [C13](book/chapters/13-sessions/chapter.tex), [C17](book/chapters/17-consistency/chapter.tex), [C20](book/chapters/20-harnesses/chapter.tex), [C25](book/chapters/25-verification/chapter.tex), [C26](book/chapters/26-evaluation/chapter.tex), [C28](book/chapters/28-security/chapter.tex), [C29](book/chapters/29-alignment/chapter.tex), [C31](book/chapters/31-serving/chapter.tex)

**Planned allocation.** 11 substantive pages. **Source review.** 29 October 2026.

1. [A release is a state-compatible system configuration](book/chapters/32-operations/sections/01.tex)
2. [Observability must reconstruct decisions and effects](book/chapters/32-operations/sections/02.tex)
3. [Canaries with persistent state and delayed outcomes](book/chapters/32-operations/sections/03.tex)
4. [Rollback and compensation are different operations](book/chapters/32-operations/sections/04.tex)
5. [Failure detectors and bounded recovery policies](book/chapters/32-operations/sections/05.tex)
6. [Service objectives and incident learning](book/chapters/32-operations/sections/06.tex)
7. [A compatibility-first deployment procedure](book/chapters/32-operations/sections/07.tex)

#### C33 [Cross-Layer Causal Analyses and Compositional System Designs](book/chapters/33-case_studies/chapter.tex)

**Objective and analytical output.** Constructed cross-layer cases, finish-first selection risk, and experiments that test contract composition.

**Contemporary evidence anchor.** Joint analysis of current memory, harness, evaluator, and cache mechanisms through explicit cases.

**Prerequisites.** [C17](book/chapters/17-consistency/chapter.tex), [C20](book/chapters/20-harnesses/chapter.tex), [C21](book/chapters/21-orchestration/chapter.tex), [C25](book/chapters/25-verification/chapter.tex), [C26](book/chapters/26-evaluation/chapter.tex), [C27](book/chapters/27-longitudinal/chapter.tex), [C30](book/chapters/30-improvement/chapter.tex), [C31](book/chapters/31-serving/chapter.tex), [C32](book/chapters/32-operations/chapter.tex)

**Planned allocation.** 11 substantive pages. **Source review.** 29 October 2026.

1. [Composition changes the claim being tested](book/chapters/33-case_studies/sections/01.tex)
2. [Case one: a repository repair with bounded side effects](book/chapters/33-case_studies/sections/02.tex)
3. [Parallel repair branches and cache-aware orchestration](book/chapters/33-case_studies/sections/03.tex)
4. [Case two: a persistent enterprise research assistant](book/chapters/33-case_studies/sections/04.tex)
5. [Testing relevance and influence rather than retrieval alone](book/chapters/33-case_studies/sections/05.tex)
6. [Case three: an agent that modifies its own research harness](book/chapters/33-case_studies/sections/06.tex)
7. [A unified acceptance record and discriminating interventions](book/chapters/33-case_studies/sections/07.tex)

#### C34 [Synthesis: Consistency Contracts and Discriminating Research Questions](book/chapters/34-synthesis/chapter.tex)

**Objective and analytical output.** Prespecified resource-bounded improver estimands, compatibility limits, and supporting, ruling-out or inconclusive evidence.

**Contemporary evidence anchor.** Evidence-bounded synthesis and falsifiable cross-layer hypotheses, not an AGI forecast.

**Prerequisites.** [C26](book/chapters/26-evaluation/chapter.tex), [C27](book/chapters/27-longitudinal/chapter.tex), [C28](book/chapters/28-security/chapter.tex), [C29](book/chapters/29-alignment/chapter.tex), [C30](book/chapters/30-improvement/chapter.tex), [C33](book/chapters/33-case_studies/chapter.tex)

**Planned allocation.** 8 substantive pages. **Source review.** 29 October 2026.

1. [What the October 2026 evidence supports](book/chapters/34-synthesis/sections/01.tex)
2. [Decision-preserving memory as an experimental target](book/chapters/34-synthesis/sections/02.tex)
3. [Conditioning under joint adaptation](book/chapters/34-synthesis/sections/03.tex)
4. [Verification whose errors are measured independently](book/chapters/34-synthesis/sections/04.tex)
5. [World models and representations must face action tests](book/chapters/34-synthesis/sections/05.tex)
6. [A research program for reliable improvement](book/chapters/34-synthesis/sections/06.tex)
7. [The remaining systems boundary](book/chapters/34-synthesis/sections/07.tex)

## Companion research maps

- [Topic-to-source and passage coverage](book/coverage.csv). This distinguishes mechanism coverage from unresolved paper-specific evidence.
- [Section-level editorial page budgets](book/section_budgets.csv). The 370-page target is an allocation, not an actual page count.
- [Versioned bibliography](book/references.bib). Source verification does not imply experimental reproduction.
- [Chapter review status](book/chapter_review_status.json) records source completion separately from final illustration and PDF validation.
- [Chapter 1 source crosswalk](book/chapter_review_sources.csv) supplies its detailed source-to-claim mapping.
- [Figure manifest](book/figures/manifest.json) and [original prompts](book/figures/prompts). Scientific images use image generation; numerical evidence is typeset in tables.

The analytical contribution is the cross-layer synthesis, explicit counterexamples, resource accounting, and discriminating experimental designs. Existing concepts and mechanisms retain their prior-art attribution.
