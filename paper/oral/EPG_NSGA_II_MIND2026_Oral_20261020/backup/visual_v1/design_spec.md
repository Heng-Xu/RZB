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
| Design Style | Academic schematic, selected under explicit delegation |
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
- **Visual Style Behavior**: Use exact aligned geometry, large white fields, square edges, single-weight rules and an asymmetric evidence split. Navy carries hierarchy and teal identifies the proposed method and selected outcomes. Native type and engineering relationships provide the visual focus.
- **Theme**: Academic schematic; a sparse bus-and-branch motif connects cover and ending, with local adaptation to each page job.
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

The body anchor is 28 px because the fixed three-body-page budget needs a small amount of mathematical terminology; detailed explanation remains in the script. Target is Microsoft PowerPoint on Windows; Arial is a standard target face.

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
| P04 | table | metric_table | Compare normalized mean final hypervolume and generation budget for the five methods at K=40 |

## VIII. Image Resource List

| Filename | Dimensions | Ratio | Purpose | Type | Image pattern | Crop Policy | Acquire Via | Status | Reference | text_policy | page_role |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

No image resource is required. The extracted paper figure remains in sources for provenance and is unused on the presentation pages.

## IX. Content Outline

### Part 1: Conference short talk

#### Slide 01 - Cover

- **Audience move**: Unfamiliar with the work → recognize the algorithm, engineering task and paper authors.
- **Relationships**: EPG-NSGA-II is the named method for differentiated county-level CLR planning under high distributed PV penetration; six authors belong to the two organizations printed in the source.
- **Composition**: Asymmetric title-led cover, with a restrained engineering network motif supporting the research identity.
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
- **Composition**: A bidirectional grid explanation paired with a compact mathematical planning brief.
- **Title**: High PV calls for differentiated planning
- **Core message**: Jointly choose station CLR and storage power while balancing cost and N−1 supply inadequacy.
- **Content**:
  - Midday PV export creates reverse power flow; a fixed CLR cap of 2.0 does not capture station differences in PV penetration and transfer capability.
  - CLR means planned transformer capacity divided by forecast peak load and is dimensionless. Station decisions: Rj and storage power Pj in MW.
  - Minimize annualized cost in million CNY/yr and expected energy not supplied, EENS, in MWh/yr. EENS quantifies N−1 supply inadequacy.
  - Constraints: station reverse-flow limits, load-weighted aggregate CLR band 1.80–3.00, and optional upstream reverse-flow limit. Five-year forecast uses 5% annual growth.

#### Slide 03 - Proposed solution

- **Audience move**: Understand the planning problem → identify where seeding and repeated repair modify standard NSGA-II.
- **Relationships**: Initial seeding and repair precede evaluation; variation is followed by repair and then evaluation/selection; selected candidates enter the next generation. Repair addresses aggregate CLR, station reverse flow, then optional upstream reverse flow. Residual infeasibility is handled by constraint domination.
- **Composition**: A clear evolutionary loop with a focused breakdown of the repair operation beneath it.
- **Title**: Engineering priors guide the search
- **Core message**: EPG-NSGA-II adds engineering-prior seeding and feasibility repair to standard NSGA-II.
- **Content**:
  - Seed and repair → vary → repair → evaluate and select → next generation. Initial R values are sampled and storage starts at zero.
  - Repair 1: bounded common CLR offset enforces the aggregate band. Repair 2: increase station storage to address reverse-flow violations. Repair 3: if enabled, allocate storage by descending residual reverse injection until the upstream limit or rating bounds are reached.
  - Standard variation, non-dominated ranking and environmental selection are retained. Constraint domination handles remaining violations.

#### Slide 04 - Results

- **Audience move**: Recognize the algorithm → assess both the ablation evidence and the reported planning outcome with budgets and model scope visible.
- **Relationships**: NSGA-II, NSGA-III, seeding-only, repair-only and EPG-NSGA-II are compared on normalized mean final HV; the 20-station elastic design is compared with the paper's 2.0-capped design on cost and EENS. These are different comparisons at different K.
- **Composition**: Search-quality evidence on the left and planning outcomes on the right, with separate headings and units.
- **Title**: Better search, lower modeled planning cost
- **Core message**: Mean final HV improves 4.8% at K=40; the reported elastic design lowers cost 3.4% and modeled EENS to zero at K=20.
- **Content**:
  - K=40 table: NSGA-II 1.000 / 800 generations; NSGA-III 0.985 / 800; seeding-only 0.998 / 400; repair-only 1.048 / 400; EPG-NSGA-II 1.048 / 400. HV normalized to NSGA-II at its termination with a common reference point; population 100; three runs. The repair component nearly matches the full method.
  - K=40 mean EPG curve reaches standard NSGA-II's final 800-generation HV at generation 84.
  - K=20 reported design comparison: annualized cost 236.40 → 228.43 million CNY/yr, decrease 3.4%; modeled EENS 561.00 → 0.00 MWh/yr. Source reports the same knee-point selection rule.
  - Public-data benchmark: scaled IEEE 33-bus loads and PVGIS-derived profiles. Storage energy/SOC constraints and real-grid calibration remain future work.
- **Visualization**: hv-comparison: native metric table with method, normalized HV and generation budget. The K=20 values are paired numeric statements with explicit units and directions.
- **Native-ready**: hv-comparison=yes

#### Slide 05 - Ending

- **Audience move**: Know the results → retain the engineering-prior contribution and join discussion.
- **Relationships**: Engineering-prior candidate construction links more effective constrained search to differentiated planning; future validation extends the current model.
- **Composition**: An open closing field with one research takeaway, a thank-you and a restrained reprise of the bus motif.
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
