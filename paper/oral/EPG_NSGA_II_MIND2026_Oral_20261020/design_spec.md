<!-- ppt-master-schema: design-spec/v1 -->
# EPG-NSGA-II MIND 2026 Oral - Design Spec

## I. Project Information

| Item | Value |
| --- | --- |
| Project Name | EPG_NSGA_II_MIND2026_Oral |
| Canvas Format | ppt169, 1280 × 720 |
| Page Count | 5 |
| Primary Language | en |
| Target Audience | MIND 2026 researchers in evolutionary computation and power-system planning |
| Communication Intent | Explain the high-PV CLR planning problem, the engineering-prior method, then the experimental evidence in that order |
| Desired Audience Outcome | Understand the variables, objectives, constraints and changed algorithm components, and retain the conditional 4.8% HV and 3.4% cost results |
| Core Message / Ask / Action | Engineering-prior seeding and feasibility repair improve constrained search and support differentiated CLR and storage-power planning |
| Delivery Context | Presenter-led English conference short talk, approximately 4–5 minutes; exactly cover, problem, solution, results, ending |
| Artifact Afterlife | Editable English PPTX, separate word-for-word English script and matching speaker notes for rehearsal and later review |
| Reading Mode | presentation |
| Content Strategy | Balanced condensation within the supplied camera-ready paper; historical code/data verify reported facts |
| Design Style | Research figure system, upgraded under the user's visual-quality revision; five-page structure retained |
| AI Image Acquisition Path | not applicable |
| Generation Mode | continuous |
| Spec Refinement | disabled |
| Speaker Notes | enabled — explicit user request for a corresponding verbatim script |
| Custom Animations | disabled — delegated production decision |
| Narration Audio | disabled — delegated production decision |
| Created Date | 2026-10-20 |

## II. Canvas Specification

| Property | Value |
| --- | --- |
| Format | PPT 16:9 |
| Dimensions | 1280 × 720 |
| viewBox | `0 0 1280 720` |
| Margins | 60 px horizontal, 42 px vertical |
| Content Area | x=60..1220, y=42..660 |

## III. Visual Theme

### Theme Style

- **Mode**: custom
- **Mode References**: narrative
- **Mode Behavior**: Follow the user-fixed cover, problem, solution, results, ending sequence; explain the planning tension, reveal the modified candidate construction, then resolve the argument with measured comparisons and a compact scientific takeaway.
- **Visual style**: custom
- **Visual Style References**: swiss-minimal
- **Visual Style Behavior**: Pair dark navy opening and closing pages with white scientific body pages. Use a large graphical abstract, native mathematical notation, thin engineering connections, panel letters and data-driven vector plots. Stable navy and teal encode baseline and proposed method; amber identifies repair-only. Keep the fixed problem, method and evidence sequence.
- **Theme**: Research figure system; native vector engineering schematics and exact experimental curves supply the visual detail, with no decorative photographs or invented quantitative traces.
- **Tone**: Clear, precise and restrained.

### Color Scheme

| Role | HEX | Purpose |
| --- | --- | --- |
| Background | #FFFFFF | Main page field |
| Secondary background | #F2F6F8 | Method and evidence zones |
| Primary | #102B46 | Titles and strong engineering elements |
| Accent | #087E83 | Proposed method and favorable reported outcomes |
| Secondary accent | #426D9B | Baseline and supporting relationships |
| Body text | #172B3A | Main text |
| Secondary text | #536774 | Source and annotation text |
| Divider | #D3DFE4 | Rules and guides |
| Grid | #E6EDF0 | Subtle table row separation |
| Dark field | #0B233B | Cover and ending |
| On dark | #F2F8FC | Text on dark fields |
| Bright accent | #66D5D0 | Engineering highlight on dark |
| Comparison | #B87232 | Repair component and CLR cap reference |
| Muted series | #7C8791 | Seeding-only and neutral references |

## IV. Typography System

### Font Plan

| Role | Character (Reference) | Primary | English if non-English | Fallback tail |
| --- | --- | --- | --- | --- |
| Title | Precise bold sans | Arial | | sans-serif |
| Body | Neutral readable sans | Arial | | sans-serif |

- **Title stack**: Arial
- **Body stack**: Arial
- **Role rationale**: The same family keeps a five-page engineering talk coherent. Dedicated cover, display, table and footnote size roles support the title, evidence and sources without changing families.

### Font Size Hierarchy

| Purpose | Anchor Size (px) |
| --- | ---: |
| Body | 28 |
| Title | 42 |
| Subtitle | 32 |
| Lead | 30 |
| Annotation | 20 |
| Table | 22 |
| Footnote | 14 |
| Display | 76 |
| Cover title | 34 |
| Plot | 18 |
| Plot tick | 18 |
| Formula | 28 |
| Metric | 54 |

The body anchor is 28 px because the fixed three-body-page budget needs a small amount of mathematical terminology; detailed explanation remains in the script. Target is Microsoft PowerPoint on Windows; Arial is a standard target face. PDF delivery uses Chromium with embedded fonts and outlined vector math previews; the PPTX retains editable Office Math. Formula previews are rendered from the same exact mathematical content, with side limits on the aggregate summations for compact display.

## V. Layout Principles

### Deck-wide Direction

- **Hierarchy direction**: One clear claim, then its relationship or experimental evidence, then necessary units and scope.
- **Composition tendency**: Open title field; large engineering explanation on problem/method pages and an asymmetric split for the two distinct results.
- **Cross-page continuity**: Bus-and-branch motif at the opening and close; teal consistently denotes the proposed method and selected outcomes.
- **Spacing posture**: Open opening/ending; focused body pages; concentrated evidence on the results page.
- **Spacing anchors**: page margin 60 px; block gap 24 px; column gutter 40 px; corner radius 0 px; body leading 38 px.

## VI. Icon Usage Specification

- **Primary bundled library**: none

| Icon Path | Suitable Scenarios |
| --- | --- |

## VII. Visualization Reference List

| Page | Family | Template | Usage |
| --- | --- | --- | --- |
| P02 | chart | scatter_chart | Show the 20 individual station CLR values against source-load ratio in the paper's reported design |
| P04 | chart | line_chart | Show K=40 EPG/NSGA-II convergence with mean and sample SD, alongside all five methods' raw final-run HV values |

## VIII. Image Resource List

| Filename | Dimensions | Ratio | Purpose | Type | Image pattern | Crop Policy | Acquire Via | Status | Reference | text_policy | page_role |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

No image resource is required. The extracted paper figure remains in sources for provenance and is unused on the presentation pages.

## IX. Content Outline

### Part 1: Conference short talk

#### Slide 01 - Cover

- **Audience move**: Unfamiliar with the work → recognize the algorithm, engineering task and paper authors.
- **Relationships**: EPG-NSGA-II is the named method for differentiated county-level CLR planning under high distributed PV penetration; six authors belong to the two organizations printed in the source.
- **Composition**: A dark title-led cover with a large technical graphical abstract, arranged as grid inputs, prior-guided search and differentiated planning.
- **Title**: EPG-NSGA-II
- **Core message**: Engineering-prior-guided search for differentiated 110 kV planning.
- **Cover impact**: Binding hook: engineering priors guide differentiated planning. The title and supporting network provide an open, precise conference cover.
- **Content**:
  - Full paper title: Engineering-Prior-Guided NSGA-II for Differentiated Capacity-Load Ratio Optimization in County-Level 110 kV Grids with High Distributed PV Penetration.
  - Dunbin Xu · Ke Wang · Yan Xu* · Ziyue Huang · Fei Geng · Rui Yuan. Yan Xu is the corresponding author.
  - State Grid Xuzhou Power Supply Company; State Grid Jiangsu Electric Power Design & Consulting Co., Ltd., Xuzhou Survey and Design Branch. MIND 2026.

#### Slide 02 - Background and problem

- **Audience move**: Know high PV is challenging → understand reverse flow, heterogeneous stations and the joint planning variables/objectives.
- **Relationships**: Distributed PV causes midday export through 110 kV substations toward the upstream grid; station PV and transfer conditions differ; CLR and storage power jointly affect annualized cost and EENS, subject to the source's reverse-flow and aggregate-CLR constraints.
- **Composition**: A technical power-flow explanation and model equation on the left, paired with a large station-level scientific scatter on the right.
- **Title**: High PV calls for differentiated planning
- **Core message**: Jointly choose station CLR and storage power while balancing cost and N−1 supply inadequacy.
- **Content**:
  - Midday PV export creates reverse power flow; a fixed CLR cap of 2.0 does not capture station differences in PV penetration and transfer capability.
  - CLR means planned transformer capacity divided by forecast peak load and is dimensionless. Station decisions: Rj and storage power Pj in MW.
  - Minimize annualized cost in million CNY/yr and expected energy not supplied, EENS, in MWh/yr. EENS quantifies N−1 supply inadequacy.
  - Constraints: station reverse-flow limits, load-weighted aggregate CLR band 1.80–3.00, and optional upstream reverse-flow limit. Five-year forecast uses 5% annual growth.
  - The reported K=20 design retains all 20 station records: source-load ratio 1.809–3.492 and selected CLR 1.55–2.64; R=2.0 is a comparison reference, not the elastic limit. This source-load ratio divides installed PV capacity by current peak load.
- **Mathematical content**: 1.8\leq\frac{\sum_{j=1}^{K} R_j L_j^p}{\sum_{j=1}^{K} L_j^p}\leq3.0
- **Visualization**: station-heterogeneity: all 20 station CLR versus source-load ratio points, linear x=1.7..3.6 and y=1.2..3.0, with the 2.0 cap as a dashed reference. No regression or causal claim.
- **Native-ready**: station-heterogeneity=no

#### Slide 03 - Proposed solution

- **Audience move**: Understand the planning problem → identify where seeding and repeated repair modify standard NSGA-II.
- **Relationships**: Initial seeding and repair precede evaluation; variation is followed by repair and then evaluation/selection; selected candidates enter the next generation. Repair addresses aggregate CLR, station reverse flow, then optional upstream reverse flow. Residual infeasibility is handled by constraint domination.
- **Composition**: A scientific workflow with station inputs, an initial seeding route, a repeated variation-repair-evaluation-selection loop and a source-backed repair equation.
- **Title**: Engineering priors guide the search
- **Core message**: EPG-NSGA-II adds engineering-prior seeding and feasibility repair to standard NSGA-II.
- **Content**:
  - Seed and repair → vary → repair → evaluate and select → next generation. Initial R values are sampled and storage starts at zero.
  - Repair 1: bounded common CLR offset enforces the aggregate band. Repair 2: increase station storage to address reverse-flow violations. Repair 3: if enabled, allocate storage by descending residual reverse injection until the upstream limit or rating bounds are reached.
  - Standard variation, non-dominated ranking and environmental selection are retained. Constraint domination handles remaining violations.
- **Mathematical content**: P_j\leftarrow\operatorname{clip}\left(\max\left\{P_j,\left[r_j^0-\beta R_j L_j^p\right]^+\right\},0,P_{\max}\right)

#### Slide 04 - Results

- **Audience move**: Recognize the algorithm → assess both the ablation evidence and the reported planning outcome with budgets and model scope visible.
- **Relationships**: NSGA-II, NSGA-III, seeding-only, repair-only and EPG-NSGA-II are compared on normalized mean final HV; the 20-station elastic design is compared with the paper's 2.0-capped design on cost and EENS. These are different comparisons at different K.
- **Composition**: A compact result strip above two scientific panels: convergence on the left and raw-run ablation on the right. Planning cost and EENS comparisons retain their own K=20 labels and units.
- **Title**: Better search, lower modeled planning cost
- **Core message**: Mean final HV improves 4.8% at K=40; the reported elastic design lowers cost 3.4% and modeled EENS to zero at K=20.
- **Content**:
  - K=40 table: NSGA-II 1.000 / 800 generations; NSGA-III 0.985 / 800; seeding-only 0.998 / 400; repair-only 1.048 / 400; EPG-NSGA-II 1.048 / 400. HV normalized to NSGA-II at its termination with a common reference point; population 100; three runs. The repair component nearly matches the full method.
  - K=40 mean EPG curve reaches standard NSGA-II's final 800-generation HV at generation 84.
  - K=20 reported design comparison: annualized cost 236.40 → 228.43 million CNY/yr, decrease 3.4%; modeled EENS 561.00 → 0.00 MWh/yr. Source reports the same knee-point selection rule.
  - Public-data benchmark: scaled IEEE 33-bus loads and PVGIS-derived profiles. Storage energy/SOC constraints and real-grid calibration remain future work.
- **Visualization**: convergence-hv: mean EPG and NSGA-II trajectories with sample SD across three independent runs, x=0..800 generations, y=0..1.1 normalized HV; EPG stops at 400, baseline at 800, and the reference HV=1 and crossing at generation 84 are shown. ablation-hv: all three final-run HV values and a distinct mean marker per method, x=0.96..1.07 with an explicit baseline reference at 1.0. Values for NSGA-III, seeding-only, repair-only and full EPG retain the paper's comparison order. The K=20 outcomes remain separate numeric statements.
- **Native-ready**: convergence-hv=no; ablation-hv=no

#### Slide 05 - Ending

- **Audience move**: Know the results → retain the engineering-prior contribution and join discussion.
- **Relationships**: Engineering-prior candidate construction links more effective constrained search to differentiated planning; future validation extends the current model.
- **Composition**: A dark closing field with a concise takeaway and a precise reprise of the engineering graphical abstract.
- **Title**: Thank you
- **Core message**: Engineering priors support more effective search and differentiated planning.
- **Closing impact**: Binding takeaway: engineering-prior seeding and repair support differentiated CLR and storage planning. End with a clear invitation to questions.
- **Content**:
  - Engineering priors → more effective search → differentiated plans.
  - Questions & discussion. MIND 2026.
- **Motion suggestion**: The cover's bus-and-branch motif reappears as a visual identity cue; static delivery remains selected.

## X. Speaker Notes Requirements

- **Generation**: enabled
- **Filename**: match each SVG filename under `notes/`
- **Content**: Write a corresponding English word-for-word script grounded in the final SVG pages and supplied paper. Include the units, budget difference, ablation interpretation and model scope. Avoid inventing the presenter's name. Keep the same text in the separate script and PPTX speaker notes.
- **Total duration**: approximately 4–5 minutes, roughly 520–620 spoken English words
- **Notes style**: Natural conference English, clear transitions and pronounceable mathematical terms
- **Presentation purpose**: Explain the planning problem, engineering-prior method and experimental evidence in five pages.
