# HTMAT: A Knowledge-Data Dual-Driven Agent for Autonomous Superalloy Design

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

HTMAT (**H**igh-**T**emperature **M**aterials **A**gent) is a knowledge-graph-guided, prompt-engineered AI agent for the autonomous design of nickel-based single-crystal superalloys. By integrating a metallurgical knowledge graph with physics-informed deep learning models within a multi-stage reasoning pipeline, HTMAT converges from ~1.37 × 10⁹ possible compositions to a single Pareto-optimal alloy — **CSU-T1** — without any target composition specified in its instructions.

## Repository Structure

```
├── Alloy design/              # Physics-based property prediction models
│   ├── Creep life prediction.py        # Phys+PINN creep rupture life predictor
│   ├── gamma prime solvus temp.py      # Gaussian process γ′ solvus model
│   ├── density prediction.py           # Rule-of-mixtures density model
│   └── Md value.py                     # New PHACOMP d-orbital energy calculation
│
├── Alloy_KG_Project/          # Superalloy knowledge graph
│   ├── 1_Data/                 # KG knowledge entries (JSONL, 8 categories)
│   ├── 2_Code/                 # Data transformation utilities
│   └── images/                 # KG construction figures
│
├── RAG+DeepSeek/              # Retrieval-augmented generation evaluation
│   ├── evaluate_rag_enhanced.py        # 60-question RAG benchmark (DeepSeek-V3)
│   └── rag_retriever.py                # TF-IDF hybrid retriever over KG data
│
├── Benchmark/                 # LLM benchmark evaluation
│   ├── bench_final_1000.py            # 1,000-question KG-enhanced QA benchmark
│   └── generate_table_s1.py           # Benchmark results table generation
│
├── Design_Pipeline/           # CSU-T1 design process documentation & data
│   ├── CSU-T1_Selection_Technical_Report_EN.md   # Full CSU-T1 selection report
│   ├── Physics_Funnel_Report_EN.md               # Four-layer physics funnel analysis
│   ├── Prompt_Chain_Engineering_Supplement.md    # Complete prompt chain (3 stages)
│   ├── CSU-T1_candidates_v2.xlsx                 # Top-22 candidate ranking
│   ├── 第一轮高通量计算结果_四维预测.xlsx        # Round 1: 675,000 compositions
│   ├── 第二轮_预测结果_完成.xlsx                 # Round 2: 96,943 compositions
│   └── TableS1_benchmark_details.xlsx            # Benchmark detailed results
│
└── CSU-T1 alloy/              # Neo4j knowledge graph database dump
    └── neo4j-2026-04-02T07-44-34.dump
```

## Design Pipeline Overview

### Phase I: Coarse Screening (Knowledge Graph → Physics Funnel)

1. **KG-Derived Initial Space**: Element ranges from published 2nd–4th generation SX superalloys, sampled at 1.0 wt% (Co, Cr, Ta, W) or 0.5 wt% (Al, Ti, Mo, Re) → 6.75 × 10⁵ candidate compositions
2. **Four-Layer Physics Funnel**: Sequential elimination cascade on computed physical properties:
   - **F1**: Density ≤ 9.05 g/cm³ → 549,535 survivors (81.4%)
   - **F2**: Md̄ < 0.98 eV (TCP phase suppression) → 367,331 survivors (54.4%)
   - **F3**: HTW > 60°C (solidification cracking defense) → 320,805 survivors (47.5%)
   - **F4**: Tγ′ > 1,280°C (γ′ stability) → 67,038 survivors (9.93%)
   - **Cumulative elimination**: 90.07% within the KG-constrained space

### Phase II: Refined Screening (Agent-Directed)

3. **Survivor Analysis**: Element-wise survival rate computation → autonomous range contraction by the Agent
4. **Refined Grid**: Al 5.2–5.8 (step 0.2), Ti 0–1.0 (step 0.5), W 7.0–9.0 (step 0.5), Re 3.0–4.5 (step 0.5), Ta 5.0–8.0 (step 1.0); Co, Cr, Mo retained → 380,160 compositions → 96,943 funnel survivors
5. **Phys+PINN Creep Prediction**: Physics-informed neural network (R² = 0.8683 CV, 0.8193 high-T) predicts creep life at 980°C/300 MPa and 1,120°C/137 MPa
6. **Six-Dimension Scoring**: Percentile-rank-based multi-objective scoring (Creep GM 60%, HTW 10%, Tγ′ 10%, Solidus 10%, Density 5%, Md̄ 5%)

### Phase III: Convergence

7. **Backbone Selection**: Agent selects Ti=0, Co=8, Cr=4, Ta=7 wt% based on global scoring + engineering constraints
8. **Within-Backbone Ranking**: 373 same-backbone alloys → **CSU-T1 (#1, Score = 0.7895)**

### CSU-T1 — Optimal Alloy

| Property | Value |
|----------|-------|
| Composition | Ni–5.6Al–8.0Co–4.0Cr–0.6Mo–8.5W–4.5Re–7.0Ta (wt%) |
| Density | 9.025 g/cm³ |
| Tγ′ | 1,285.9 °C |
| HTW | 86.8 °C |
| Creep (980°C/300 MPa) | 271.1 h |
| Creep (1,120°C/137 MPa) | 226.0 h |

## Key Technical Contributions

- **Prompt Engineering as Method**: The Agent's reasoning — not the KG alone — drives autonomous convergence. The KG provides the initial element space, but the four-layer physics funnel, survivor analysis, multi-objective scoring, and backbone selection are all emergent Agent behaviors guided by prompt engineering.
- **Phys+PINN Architecture**: Dual physical knowledge integration at input (5 physical descriptors: Md̄, δ, ln Z, T_h, Re_eff) and loss levels (LMP-based physics consistency penalty), achieving superior high-temperature extrapolation.
- **Geometric Mean Scoring**: GM = √(P₉₈₀ × P₁₁₂₀) penalizes single-temperature creep specialists.
- **Fully Auditable**: Complete prompt chain disclosed verbatim; every Agent decision traceable to specific physical justification.

## RAG + DeepSeek

The retrieval-augmented generation module uses **DeepSeek-V3** with a hybrid KG retrieval strategy:
- **Query rewriting**: Chinese → English symbol normalization
- **TF-IDF retrieval**: Lightweight, zero-dependency keyword matching over KG entries
- **60-question benchmark**: 40 base + 20 adversarial perturbation questions

## Data Security

HTMAT supports fully localized, offline deployment on high-performance workstations, ensuring absolute data privacy for proprietary alloy research.

## Citation

If you use HTMAT in your research, please cite:

```bibtex
@article{HTMAT2025,
  title={A Knowledge-Data Dual-Driven AI Agent for Reliable Reasoning and Autonomous Design of Superalloys},
  author={Yao, Jian and colleagues},
  journal={Nature Communications},
  year={2025},
  note={Under review}
}
```

## License

MIT License.
