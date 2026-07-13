# HTMAT Agent — Physics Funnel Convergence Report

## 1. General Approach

Confronted with a 675,000-composition ultra-high-dimensional elemental space, the Agent operates without reliance on any empirical creep calibration. It converges autonomously, layer by layer, guided solely by metallurgical physics red lines. The core logic is: **each red line corresponds to an independent failure mechanism; only compositions that survive all mechanisms simultaneously qualify for further evaluation**.

---

## 2. Deployment of the Four Physics Red Lines

### F1 | Lightweight Centrifugal Stress Control: Density ≤ 9.05 g/cm³

**Physical motivation**: Ni-based single-crystal turbine blades experience enormous centrifugal stress during high-speed rotation. Each 0.1 g/cm³ increase in density raises blade-root centrifugal stress by approximately 3–5%. Excessive loading of high-density refractory elements (W, Re, Ta) may enhance solid-solution strengthening, but it drives a malignant rise in density, promoting creep–fatigue interactive failure during service.

**Filtering outcome**: 675k → 549k (18.6% eliminated)

---

### F2 | Detrimental Phase Topological Suppression: Md̄ < 0.98 eV

**Physical motivation**: The d-orbital energy level Md̄ is a key electronic parameter for predicting the precipitation tendency of topologically close-packed phases (TCP: σ, μ, P). When Md̄ ≥ 0.98 eV, the probability of TCP precipitation during long-term high-temperature service (>1,000 h) rises sharply. TCP phases, as brittle lamellar precipitates, heavily deplete the matrix of refractory solid-solution strengtheners (especially Re and W), directly causing a cliff-like drop in creep resistance.

**Filtering outcome**: 549k → 367k (45.6% cumulative elimination)

---

### F3 | Single-Crystal Solidification Manufacturability: HTW = Solidus − Tγ′ > 60°C

**Physical motivation**: The heat treatment window (HTW) is defined as the difference between the solidus temperature and the γ′ solvus temperature. When HTW ≤ 60°C, γ′ phase dissolution remains incomplete when the solidus is approached during solution heat treatment, making the alloy highly susceptible to incipient melting and the formation of micro-hot-tears in the directionally solidified microstructure. These cracks act as fatigue crack initiation sites during subsequent service.

**Filtering outcome**: 367k → 321k (52.5% cumulative elimination)

---

### F4 | Ultra-High-Temperature Strengthening-Phase Stability: Tγ′ > 1280°C

**Physical motivation**: The γ′ phase (L1₂ ordered structure) is the most critical strengthening phase in Ni-based single-crystal superalloys. As service temperature approaches or exceeds the γ′ solvus, large-scale γ′ dissolution occurs, the coherency stress field vanishes, the Orowan bypass mechanism fails, and the creep rate rises by 2–3 orders of magnitude. Modern single-crystal blades require a γ′ solvus temperature > 1280°C to retain a sufficient γ′ volume fraction (>50%) within the ≥1100°C service window.

**Filtering outcome**: 321k → **67,038** (90.07% cumulative elimination)

---

## 3. Agent-Directed Further Restriction of the Composition Space

After four-layer physics screening, the elemental distributions within the survivor space exhibit clear physics-imposed preferences. The Agent analyzed these survivor statistics and issued directives to further constrain each element's range, tightening the composition space around physically viable regions. The independent decision logic for each element is presented below.

### Al: Agent directive → 5.2–5.8, step 0.2

**Survivor distribution**: Al = 5.0–6.0 accounts for 76.2% of survivors; Al = 4.0 contributes only 5.5%. Al is the critical γ′ (Ni₃Al) forming element, its content directly governing γ′ volume fraction and solvus temperature. Below 5%, the γ′ volume fraction is insufficient to sustain high-temperature strength; above 6%, excessive eutectic γ/γ′ forms in the as-cast microstructure, degrading the incipient melting temperature.

**Agent's directive**: Restrict the space to the 5.2–5.8 intermediate-to-high Al window. A step of 0.2 resolves the sensitivity of Tγ′ to 0.4% Al variation (~8–10°C per 0.1% Al).

---

### Ti: Agent directive → 0.0–1.0, step 0.5

**Survivor distribution**: As Ti content increases from 0 to 2.0, survival rate decreases linearly from 33.1% to 6.4%. Ti carries the highest Md̄ value (2.271 eV) among all alloying elements, making it the strongest contributor to elevating the overall Md̄ level. High-Ti combinations readily trigger TCP phase precipitation (F2 red line). Furthermore, Ti contributes less to the γ′ solvus temperature than Al and Ta, and excess Ti degrades oxidation resistance.

**Agent's directive**: Constrain Ti to the low range of 0–1.0. Ti = 0 is fully viable (Ti-free designs already exist in modern second-generation single-crystal alloys). A step of 0.5 is sufficient to resolve its influence.

---

### Co: Agent directive → retain 6–11, step 1

**Survivor distribution**: Co is uniformly distributed across the full 6–11 range (15.0–17.6%), with no discernible preference imposed by the physics filters. Co primarily lowers the stacking fault energy (SFE), promoting dislocation cross-slip and rafting, but its contributions to γ′ formation temperature, Md̄, and density are all relatively mild.

**Agent's directive**: Retain the full 6–11 range at step 1; no contraction warranted.

---

### Cr: Agent directive → retain 3–8, step 1

**Survivor distribution**: Cr = 3–8 is uniformly distributed (15.8–17.3%), with a slight downward trend at higher Cr. Cr is essential for oxidation and hot-corrosion resistance, but excessive Cr (>8%) tends to form σ-phase with Mo and Re during solidification.

**Agent's directive**: Retain the full 3–8 range at step 1.

---

### Ta: Agent directive → 5–8, step 1

**Survivor distribution**: Ta = 4 shows an extremely low survival rate (3.1%), while Ta = 6–8 accounts for 80.9% of survivors. Ta partitions into both γ and γ′ phases, delivering strong solid-solution strengthening and significantly elevating the γ′ solvus temperature. At Ta = 4, the γ′ volume fraction and high-temperature stability are insufficient to pass the F4 (Tγ′ > 1280°C) red line.

**Agent's directive**: Eliminate Ta = 4; restrict the space to 5–8. Ta = 5 as the lower bound preserves a low-cost design margin.

---

### Mo: Agent directive → retain 0.0–2.0, step 0.2

**Survivor distribution**: Mo is uniformly distributed across the full 0–2.0 range (18.2–20.7%), with no preference from the physics filters. Mo provides significant solid-solution strengthening at a cost far below Re, although excess Mo promotes σ and μ phase formation. A step of 0.2 enables precise resolution of the critical Mo content.

**Agent's directive**: Retain the full 0–2.0 range at step 0.2.

---

### W: Agent directive → 7.0–9.0, step 0.5

**Survivor distribution** (a pivotal decision point):

| W (wt%) | Initial Samples | Survivors | Survival Rate |
|---------|----------------|-----------|---------------|
| 5 | 112,500 | 19,897 | 17.7% |
| 6 | 112,500 | 19,904 | 17.7% |
| 7 | 112,500 | 16,316 | 14.5% |
| 8 | 112,500 | 8,770 | 7.8% |
| 9 | 112,500 | 2,048 | 1.8% |
| 10 | 112,500 | 103 | 0.09% |

W survival rate exhibits a **clear staircase decay**: W = 5–6 have comparable survival (~17.7%), W = 7 shows a mild decline (14.5%), W = 8 is halved (7.8%), W = 9 is halved again (1.8%), and W = 10 is nearly extinguished (0.09%). This decay pattern is driven by the coupling of two red lines:

1. **F1 density red line**: W has the highest atomic weight (183.84) among the alloying elements, contributing 0.0436 g/cm³ per wt%. Excessive W directly pushes the overall density beyond the 9.05 upper limit.
2. **F4 Tγ′ red line**: W partitions almost exclusively to the γ matrix; excessive W leads to W supersaturation in the matrix, which paradoxically depresses the γ′ solvus temperature.

Conversely, W below 7% provides insufficient high-temperature solid-solution strengthening. W enhances creep resistance by retarding dislocation climb and reducing diffusion coefficients — an effect that only becomes pronounced at W ≥ 7%.

**Agent's directive**: Restrict the space to W = 7.0–9.0, step 0.5. This interval retains adequate W solid-solution strengthening while avoiding density violation and γ′ stability loss.

---

### Re: Agent directive → 3.0–4.5, step 0.5

**Survivor distribution**: For Re = 3.0–5.0, the survival rate rises slowly with increasing Re (6.9% → 11.6%), exhibiting no obvious decay. Re is the most potent solid-solution strengthener (producing ~2.5% lattice misfit per atom), effectively reducing diffusion coefficients and climb rates, and is the single most important contributor to creep resistance in modern single-crystal superalloys.

However, Re is subject to three concurrent constraints:
1. **Density penalty**: density contribution coefficient of 0.0508 per wt%, second only to W.
2. **TCP precipitation risk**: excess Re (>5%) is a strong promoter of μ and P phases.
3. **Cost penalty**: Re costs ~3,000 USD/kg, over 100 times that of W.

Given that W has already been compressed to 7–9% (thereby consuming much of the density budget), capping Re at 4.5% strikes a balance between solid-solution strengthening and density control.

**Agent's directive**: Re = 3.0–4.5, step 0.5. The lower bound of 3.0% preserves the baseline Re content of second-generation single-crystal alloys; the upper bound of 4.5% approaches third-generation levels.

---

## 4. Design Space Summary

| Element | Range (wt%) | Step | Grid Points | Physics-Based Rationale |
|---------|------------|------|-------------|------------------------|
| Al | 5.2–5.8 | 0.2 | 4 | γ′ volume fraction & Tγ′ control |
| Ti | 0.0–1.0 | 0.5 | 3 | Md̄ suppression (Ti is the largest Md̄ contributor) |
| Co | 6–11 | 1 | 6 | Uniform distribution; full range retained |
| Cr | 3–8 | 1 | 6 | Uniform distribution; full range retained |
| Ta | 5–8 | 1 | 4 | γ′ stability & Tγ′ (Ta = 4 eliminated) |
| Mo | 0.0–2.0 | 0.2 | 11 | Solid-solution strengthening (TCP risk governed by Md̄ red line) |
| W | 7.0–9.0 | 0.5 | 5 | Precise balance: high-W strengthening vs. density/Tγ′ constraints |
| Re | 3.0–4.5 | 0.5 | 4 | Strengthening upper bound constrained by density and cost |

**Theoretical grid**: 4 × 3 × 6 × 6 × 4 × 11 × 5 × 4 = **380,160**

**Post four-layer physics screening survivors**: **96,943** (survival rate 25.5%)

---

## 5. Deliverables

- Output file: `第二轮高通量网格_待蠕变预测.xlsx` (96,943 entries)
- Contains pre-computed density, Md̄, γ′ solvus temperature, solidus temperature, and HTW
- The user's PINN creep prediction model need only supplement the creep life columns upon ingestion

---

*This report was autonomously generated by the HTMAT Agent. All boundary decisions are grounded in physics, derived from the survival statistics of the multi-layer failure-mechanism filters.*
