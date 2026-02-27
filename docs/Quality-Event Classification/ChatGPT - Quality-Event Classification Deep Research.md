# Quality-Event Classification, Routing, and Escalation in Automotive Surface Finishing Operations

## Scope and source notes

This report focuses on the practical reality of **surface finishing as a “special process”** in automotive supply chains: coating results (especially corrosion and adhesion performance) are often **not fully verifiable at the moment of manufacture**, and failures can be **latent** (showing up after assembly, testing, or service exposure). That single fact strongly shapes how the industry classifies and routes “quality events” in coating lines: shops must treat many process signals as **potential product risk** and route them with containment discipline. citeturn33search15turn12view0

Several key requirements documents (notably the full text of IATF 16949, ISO 9001:2015, and AIAG CQI manuals) are copyrighted and usually distributed commercially. Where direct standards text is not openly accessible, this report uses: **official sanctioned interpretations** for IATF clauses, **OEM customer-specific requirements (CSRs)** published through the IATF Global Oversight site, and **publicly available CQI-12/CQI-11 assessment artifacts** that show the *actual question sets and expectations auditors use* (reaction plans, monitoring frequencies, log reviews, calibration/pyrometry controls, etc.). citeturn12view0turn12view1turn23view0turn22view0turn19view1turn20view1

For Toyota supplier requirements (AQMR / SQAM), the most authoritative current documents are often behind supplier portals; public copies exist but authenticity/version control can be unclear. This report therefore uses Toyota-related content only where it is clearly identified as SQAM and framed as **directional evidence of common OEM expectations**, not definitive clause-by-clause compliance. citeturn11search3

A downloadable workbook containing the requested **Part 2 reference tables** (Table A, B, C) is included here:  
[Download the Excel workbook](sandbox:/mnt/data/Automotive_Coating_Quality_Event_Research_Tables.xlsx)

## Classification models and routing patterns used in industrial practice

A coating operation typically needs to classify an event along **three independent axes** at the moment of discovery:

1. **Signal strength / certainty**: “something looks off” vs “out-of-control trend” vs “out-of-spec” vs “confirmed nonconformance.” (This controls whether the system opens a lightweight record, triggers containment, or escalates to formal problem solving.) citeturn12view0turn17view1  
2. **Object of control**: product (defect), process (parameter deviation), equipment/facility (capability loss), material/chemistry (incoming or bath excursion), measurement system (calibration/MSA), system/documentation change, customer-originated complaint, supplier-originated defect. CQI-12 and CQI-11 make this separation explicit by requiring both **product controls** (job audits, release checks) and **process controls** (tables of monitored parameters, calibration/pyrometry, reaction plans). citeturn17view1turn19view1turn20view1  
3. **Origin / accountability path**: internal detection, customer-detected escape, supplier-caused, or regulatory-driven (EHS). This axis drives who owns response (operations vs supplier quality vs customer quality vs EHS) and which external reporting clocks start. citeturn23view0turn22view3turn27search0turn27search3  

The industry rarely relies on a *single* classification scheme. Instead, mature systems use a **hybrid**: a small set of *event classes* (what workflow opens) plus one or more *attributes* (severity, origin, technology, customer program, special characteristic flags) used for escalation automation and “read-across.”

### The most common model families

The table below summarizes model families that repeatedly show up across automotive supplier practices, OEM CSRs, CQI assessments, and the way ERP/QMS systems structure quality notifications.

| Model family | How it classifies events | What separates tiers/categories | Where it shows up in practice | Strengths | Weaknesses / failure modes |
|---|---|---|---|---|---|
| **Signal-strength tiering** (Observation → Drift → Deviation → Nonconforming output → Escalation/8D) | Starts with *certainty and risk* rather than cause | “Suspect” vs “nonconforming”; “out of control” vs “out of spec”; shipped vs not shipped | Explicitly reinforced by CQI-12 monitoring logic (control limits, revert to minimum frequencies) and by OEM “customer concern” clocks that start as soon as the customer notifies. citeturn17view1turn23view0turn24view0 | Prevents waiting for proof before containment; supports drift-to-escalation pathways | If drift is treated as “noise,” chronic issues accumulate without ownership |
| **Event-type routing** (product vs process vs equipment vs material vs measurement vs audit vs customer vs supplier) | Opens different workflows based on *what happened* | Different required data, owners, and reaction plans depending on class | CQI-12 and CQI-11 are structured around process tables (process control) + job audits (product), plus handling/log review and calibration/pyrometry. citeturn19view1turn20view1turn17view1 | Matches how coating lines actually work (chemistry, ovens, booths, application) | If taxonomy is too fine-grained, operators misclassify and data quality collapses |
| **Origin-based classification** (Internal / Customer / Supplier / Regulatory) | Routes by “who found it / who owns it” | Customer vs internal detection triggers different containment scale and timelines | Strongly visible in Ford CSR “Customer Concerns” and shipped-product notification requirements, and in CSII/controlled shipping escalations. citeturn23view0turn23view3turn22view3 | Aligns accountability and external communication | Can mask the true technical class (process/equipment) if used alone |
| **Severity & risk model** (Minor/Major/Critical + special-characteristic flags) | Uses severity/risk to set escalation and authorization requirements | Safety/regulatory/critical characteristics trigger immediate escalation; customer authorization required for certain dispositions | GM and Ford use explicit escalation expectations; IATF sanctioned interpretations require customer authorization for “use as is” and for rework/repair dispositions. citeturn12view1turn23view0turn22view0 | Enables automatic escalation rules | Severity scoring is often inconsistent without clear decision gates |
| **ERP “notification type” model** (internal problem, customer complaint, vendor complaint, etc.) | Encodes workflows by business object | Complaint vs internal issue vs supplier issue | Large manufacturers frequently implement this inside ERP/QMS suites; for example, entity["company","SAP","enterprise software vendor"] QM supports different “notification types” (customer complaint, complaint against vendor, internal problem report). citeturn6search1turn6search2 | Proven at scale; integrates with purchasing, production, shipping | ERP-driven type lists can drift away from coating-reality unless validated by CQI/OEM needs |
| **Containment-status model** (safe launch / EPC / controlled shipping) | Uses containment mode as a top-level state | Launch vs serial vs “customer containment active” | GM Early Production Containment requires a pre-launch control plan, reaction plan for *single defect*, and no rework at the containment station; OEM controlled shipping models define CS1/CS2 escalation patterns. citeturn16view3turn22view3turn8search6turn8search12 | “Nothing falls through the cracks” because containment is explicit and audited | If applied too broadly, becomes permanent “inspection factory” and hides process capability problems |

### What “routing” means in coating operations

Across these models, “routing” usually means assigning the event to one of a small number of **primary workflows**, each with different required fields, owners, and clocks:

- **Suspect product containment workflow**: quarantine + define scope + verification plan (especially important when chemistry/oven/equipment signals are ambiguous but risk is real). CQI-12 and CQI-11 explicitly require segregation and controlled movement for nonconforming/suspect material. citeturn17view1turn20view3  
- **Nonconforming output (NCR) workflow**: confirmed defect + disposition decision + reinspection/retest evidence + traceability. IATF links containment/interim actions to control of nonconforming outputs and problem solving. citeturn12view0turn12view1  
- **Process deviation / out-of-control workflow**: parameter breach or SPC signal + reaction plan + product risk decision (“what lots are affected?”). CQI-12’s “revert frequency if outside control limits” is a concrete, operationalized form of this model. citeturn17view1turn19view1  
- **Customer concern / complaint workflow**: containment at customer + certified stock + structured problem solving (typically 8D) on OEM timelines (hours to days). Ford’s CSR is unusually explicit about timing and 8D milestones. citeturn23view0turn23view3  
- **Supplier nonconformance (SCAR) workflow**: incoming defect/COA mismatch + supplier response + containment + verification. IATF’s sanctioned interpretation on outsourced process control requires criteria/actions to “escalate” the type and extent of control over external providers. citeturn12view0  
- **Audit finding / system nonconformance workflow**: CQI findings, layered process audits, internal audits, etc., often routed to corrective action even if no defect is currently visible—because in special processes, “system gaps” are treated as latent defect risk. Stellantis CSR explicitly requires Layered Process Audits and frames them as a mechanism to ensure compliance to manufacturing requirements. citeturn24view1turn25search16  

## Standards and OEM requirements

This section answers: **what is required**, **what is strongly implied**, and **where suppliers have discretion** to define their own classification model.

### ISO 9001:2015 requirements that drive event classification

ISO 9001:2015 sets the baseline expectation: organizations must control nonconforming outputs and take corrective action. But ISO 9001 generally does **not prescribe** the internal *classification tiers* or naming conventions—suppliers define those as long as the system prevents unintended use/delivery and drives corrective action effectiveness. This is reinforced by ISO auditing guidance emphasizing correct documentation of nonconformities when they exist, rather than turning audits into “fault finding” exercises. citeturn28search15turn13view1

Practical implication for event systems: ISO 9001 supports a distinction between (a) **signals/observations** that may not yet be nonconformance, and (b) **confirmed nonconforming outputs** requiring formal control—because the standard cares about outcomes (control + correction + prevention), not what you call your record type. citeturn28search15

### IATF 16949 requirements that force routing discipline in automotive suppliers

Even via the publicly available sanctioned interpretations, several requirements directly shape how events must be routed:

- **Problem solving must be tiered by problem type/scale and must prevent recurrence.** The sanctioned interpretation for clause 10.2.3 requires “defined approaches for various types and scale of problems,” and explicitly includes containment/interim actions for control of nonconforming outputs, root cause analysis, systemic corrective actions, effectiveness verification, and updating PFMEA/control plan. citeturn12view0  
- **Customer authorization (concession/deviation permit) is required before further processing in specific cases.** The sanctioned interpretation linked to clause 8.7.1.1 requires customer concession/deviation when product or manufacturing process differs from what is approved, and requires customer authorization prior to further processing for “use as is” and for rework for repair dispositions (and to communicate sub-component reuse if applicable). citeturn12view1  
- **Outsourced processes require an escalation model for control.** The sanctioned interpretation for clause 8.4.2.1 requires criteria and actions to escalate or reduce the types and extent of controls used to verify conformity of externally provided products/processes/services. This is effectively an “event escalation” requirement applied to the supply base. citeturn12view0  
- **Risk analysis must include “lessons learned” from complaints, scrap, and rework.** This creates an implied expectation of accumulation logic (issues must be trended and fed into risk controls). citeturn12view0  

Where IATF leaves discretion: IATF does not mandate that you use a specific internal taxonomy (e.g., “QN vs NCR”). Instead, it requires that your **documented processes** produce the required behaviors: containment, authorization, traceability, corrective action, and prevention of recurrence—with customer-prescribed methods used where required. citeturn12view0turn12view1

### How CQI-12 turns coating process control into “event types”

CQI-12 is explicitly written as a coating **system assessment** designed to evaluate the quality systems in coating shops supplying automotive coatings, including conversion coatings, anodizing, powder coatings, sprayed coatings, dip/spin coatings, and common steps like aqueous/mechanical pretreatment and curing. citeturn33search15turn25search10

Public CQI-12 assessment artifacts show several classification expectations that are coating-specific:

- **Suspect/nonconforming material control is treated as foundational.** CQI-12 language and its assessment structure emphasize the need to prevent movement of nonconforming product into/out of the production system and require defined hold areas, authorized personnel, disposition controls, and tracking of material movements. citeturn17view1turn19view1  
- **Process monitoring is explicitly tied to control limits, minimum frequencies, and “revert” logic.** CQI-12 process tables state that reduced monitoring frequencies require at least **30 consecutive measurements** to justify, and if a reduced-frequency data point is outside control limits, the process must revert to minimum frequencies. This is an unusually concrete published mechanism for a “drift → escalation” trigger. citeturn17view1turn19view1  
- **Calibration and pyrometry failures are explicit event triggers with forced routing.** CQI-12 includes language requiring corrective actions and documentation for out-of-tolerance conditions, and pyrometry sections describe that failed temperature uniformity requires determining/documenting the cause and prohibits further processing until corrected and successfully re-verified (or until an approved deviation/exception is obtained). citeturn19view0turn19view1  

In other words: CQI-12 implicitly defines multiple event classes that many generic QMS templates miss (pyrometry failure, SAT/TUS out-of-tolerance, monitoring frequency reversion, trap-point events, etc.). citeturn19view1turn17view1

### CQI-11 (plating) contrasts that matter for classification design

CQI-11 (plating) uses many of the same structural ideas as CQI-12 (process tables, monitoring reviews, calibration/pyrometry expectations), but it contains distinctive “hard gate” timing logic—especially around hydrogen embrittlement relief.

Example: CQI-11 requires that, for hydrogen embrittlement avoidance and relief, **log review occurs prior to shipment release and not exceed 24 hours**. citeturn20view1

This is valuable as a comparison because it shows a special process model where “record review” is itself an **event gate** tied to shipment release, not merely a continuous improvement activity. A coating operation can apply analogous logic to high-risk cure logs, chemistry excursions, or nonconformance release reviews. citeturn20view1turn19view1

### CQI-29 clarification

In the automotive CQI family, CQI-29 is widely referenced as the **Brazing System Assessment**, not “Thermal Spray.” GM’s CSR revision history explicitly lists “CQI-29 Brazing System Assessment.” citeturn22view0

If “thermal spray” is in your internal scope, it is likely controlled via other customer/special-process frameworks rather than an AIAG CQI-29 document; treat that as a documentation gap to verify against your customer program requirements. citeturn22view0turn25search10

### OEM customer-specific requirements that impose event thresholds and reporting clocks

OEM CSRs are where the most explicit *classification-and-routing* thresholds appear, because they define when internal issues become customer-facing events with deadlines.

**Ford (CSR)**
- Requires processes/systems to prevent shipment of nonconforming product to any Ford facility and “should analyze” nonconforming product/process output using 8D methodology. citeturn23view0  
- Requires notification to Ford within **24 hours or sooner** if nonconforming product has been shipped. citeturn23view3  
- For “Customer Concerns,” requires response in **24 hours**, containment in the Ford plant, certified stock, an 8D delivered through interim containment actions, and delivery of an 8D (or 6-panel) within **15 calendar days** with preliminary/verified root cause and a corrective/preventive action plan. citeturn23view0  

**GM (CSR)**
- Requires the documented problem-solving process to include tracking issues through closure and daily review by a multi-disciplined team including plant management (with documented daily reviews), robust root cause method, and timely closure with exit criteria; it also expects documented initial containment. citeturn22view0  
- Requires certification-body notification within **5 business days** after being placed in Controlled Shipping Level 2 (CSII), and frames CSII as a performance indicator of problems in product realization. citeturn22view3  
- Requires error-proofing devices to be tested to failure/simulated failure at shift start at minimum, and requires a reaction plan including containment when error-proofing fails. citeturn22view0  

**Stellantis (CSR)** (relevant even if not in your current OEM list, because Tier 1 programs frequently flow down these expectations)
- Requires suppliers to use a Stellantis tracking system to submit 8D reports and manage containment/corrective/preventive actions during mass production. citeturn24view0  
- Requires proactive containment (“safe launch”) during launch periods with defined exit conditions, explicitly noting PPAP acceptance is not sufficient as an exit condition. citeturn24view2  
- Requires product/process changes to be classified according to a Stellantis A/B/C/D classification system with associated validation level and PPAP submission requirements. citeturn24view2  
- Treats reuse of components as a rework operation and requires planned rework to be incorporated into process flow, PFMEA, and control plan; also expects Stellantis approval for unplanned rework. citeturn24view2  

**BMW CSR (publicly posted CSR)**
The BMW CSR document accessible publicly is comparatively light on operational quality-event thresholds; it emphasizes supplier responsibilities such as appointment of a product safety and conformity representative and points to additional BMW Group standards accessible via supplier portals. citeturn21view0  
Practical implication: for BMW programs, many event-routing requirements may be contained in portal standards rather than the short CSR summary, so suppliers often implement BMW event thresholds via program-specific documentation rather than relying on one published PDF. citeturn21view0  

## Coating-event taxonomy and technology-specific differences

This section “maps the landscape” of what can go wrong (or might be going wrong) in coating operations, and how adjacent categories are distinguished when building a routing model.

### Core distinctions that prevent category collisions

In coating operations, the boundary lines between categories are operationally important:

- **Product quality event**: a part characteristic fails acceptance criteria (appearance, thickness, adhesion, corrosion, etc.). These route to **NCR + disposition** plus (often) escalation rules if severe or repetitive. citeturn12view0turn23view0  
- **Process deviation event**: a process parameter leaves validated/spec limits (chemistry, cure profile, viscosity, booth airflow). These typically route to **process reaction plan + suspect product scope decision** because product impact may be uncertain. citeturn17view1turn19view1  
- **Process drift event**: parameters trend toward limits or violate SPC/control rules without yet breaking spec. CQI-12’s control-limit “revert frequency” logic is a concrete example of how drift becomes an event type rather than ignored noise. citeturn17view1  
- **Equipment/facility capability loss**: calibration/pyrometry failures, filtration/DP alarms, power-supply instability. In special processes, these often route as **“equipment event + product risk assessment”** because equipment failures can create widespread latent defects. citeturn19view1turn19view0  
- **Material/chemistry excursion**: batch failures, contamination, bath chemistry drift, reclaim contamination. These usually require containment because the affected scope is typically by lot/time window and can cross multiple orders. citeturn19view1turn26search0  
- **Customer-originated event**: complaint/return/chargeback/controlled shipping. These route into OEM-defined response clocks and structured problem solving. citeturn23view0turn22view3turn24view0  

### Technology-specific event behaviors

image_group{"layout":"carousel","aspect_ratio":"16:9","query":["powder coating line electrostatic spray booth","automotive e-coat electrodeposition bath line","robotic liquid spray paint booth automotive"],"num_per_query":1}

#### Powder coating: electrostatic field behavior + reclaim creates unique event types

Two powder-specific physical behaviors frequently create “category traps” unless explicitly modeled:

- **Faraday cage effect**: electrostatic field-line behavior prevents charged powder from reaching recesses/internal corners, producing “missed coverage” (holidays) that may not be visible until corrosion testing or customer inspection. This is a product defect but often originates from electrostatic/process setup. citeturn34search8turn34search15  
- **Back ionization / micro-cratering**: excessive field strength can create micro-craters and rough texture; many troubleshooting guides tie this to high voltage, part geometry, grounding, and excessive film build. citeturn34search11turn34search15  
- **Reclaim contamination**: reclaim creates a rapid “propagation mechanism” for defects and color/effect shifts—an event class that simply does not exist in e-coat and looks different from liquid paint (where batch segregation is the analog). citeturn34search23turn17view1  

Implication for classification: powder operations often benefit from splitting **“coverage/transfer physics”** events (Faraday, grounding, kV/µA issues) from generic “appearance defects,” because the routing and data needed are different. citeturn34search8turn34search23

#### E-coat: continuous immersion chemistry + electrical control drives event structure

E-coat behaves like a continuous “plant within a plant”—a combination of chemistry management, filtration/UF systems, and electrical deposition control. Sources describing electrocoating emphasize its reliance on voltage/current control and the sensitivity to process stability, which supports treating bath/electrical signals as first-class event types. citeturn26search21turn26search32turn26search25

Common e-coat-specific event classes (often not captured by generic “NCR” templates) include:
- **Bath chemistry excursions** (pH, conductivity, solids, P/B ratio) and **UF/permeate quality degradation** that can change deposition behavior and contaminate rinses. citeturn26search32turn26search25  
- **Power supply / grounding instability**: uneven deposition and patchy coverage can be electrical rather than purely chemical. citeturn26search25turn26search21  
- **Carryover and trap-point events** (fallen parts, deposits) that can create particulate/film defects and contamination loops. citeturn19view1turn17view1  

Implication for classification: e-coat systems often route events first by **“chemistry/electrical/system health”** rather than by visible defects, because visible defects may be a lagging indicator. citeturn26search32turn17view1

#### Liquid spray paint: batch mixing + multi-coat windows produce time-dependent event types

Liquid systems, especially multi-coat primer/base/clear, create event types that are inherently **time-window-based**:
- **Mix ratio, viscosity, and pot life** errors (where material changes over time) produce defects and cure failures that are often batch-contained but can affect many parts before detection. citeturn34search7turn7search27  
- **Flash time and intercoat window deviations** can cause solvent-pop, dieback, and other appearance defects; these are process events that behave differently than powder/e-coat. citeturn7search27  
- **Metallic orientation / mottling** is a classic liquid-specific appearance failure mode; refinishing guidance discusses how application technique and film wetness contribute to mottling and streaking. citeturn34search21turn34search32  
- **Color difference (ΔE)** is commonly used as an objective metric to quantify color difference; vendors explain ΔE as a distance metric and note that tolerances depend on product context and measurement method (including multi-angle measurement for effect finishes). citeturn34search6turn34search31turn34search28  

Implication for classification: liquid operations often require explicit event types for **“mixing/timing failures”** (pot life exceeded, incorrect reduction, flash time deviation), because those failures are preventable through workflow controls (timers, batch tracking) and are not well captured as generic “defect found” records. citeturn7search27turn34search7  

## Disposition and escalation logic in coating operations

### Disposition options in coating and how they interact with event classification

Disposition is the decision about **what happens to affected product**. Classification is the decision about **which workflow and controls apply**. In coating, these are tightly linked but not identical:

- A **process deviation** (e.g., pretreatment concentration out of range) can exist *without* a confirmed product defect at the moment it’s detected, but still requires a **suspect product containment workflow** and ultimately a disposition decision for the affected time window. citeturn17view1turn12view0  
- A **product defect** (e.g., adhesion failure) triggers immediate NCR/disposition, but the system still needs process/material/equipment records to determine the containment scope and prevent recurrence. citeturn12view0turn19view1  

The full practical disposition set in coating commonly includes:
- **Use-as-is** (only when allowed and typically requiring customer concession depending on context)  
- **Rework**: repaint/recoat, sand-and-buff then refinish, strip and recoat, blend/spot repair  
- **Scrap**  
- **Return to supplier** (when substrate/material is at fault)  

The critical automotive constraint is that customer authorization is required in defined cases. IATF’s sanctioned interpretation requires customer concession/deviation permits when product/process differs from approved, and requires customer authorization for “use as is” and for rework for repair dispositions before further processing. citeturn12view1

### Coating rework creates secondary events (“the rework loop problem”)

Coating rework is not just a disposition—it often creates **new process and product risks**:

- Powder coat rework frequently involves stripping methods (chemical stripping, burn-off ovens, blasting) or liquid touch-up; these choices create secondary risks (base-metal damage, distortion, contamination, re-clean requirements). citeturn26search0turn26search24  
- E-coat repair and removal methods include stripping/abrasion/burn-off approaches, and surface condition after repair can drive new adhesion/corrosion risks. citeturn26search16turn26search4  
- Industry commentary on coating operations highlights how “touch-up” and rework loops can become normalized, which is a classic trap: the system must treat rework not as routine noise but as a signal of process capability gaps. citeturn26search7  

Stellantis explicitly treats reuse of components as rework and requires planned rework to be incorporated into process flows, PFMEA, and control plan, reinforcing that rework is a controlled process—not an ad hoc activity. citeturn24view2  

### Escalation and accumulation logic used to prevent “death by a thousand cuts”

Coating operations face a chronic failure mode: small defects or small excursions that are individually “minor” can accumulate into major cost and customer risk. Automotive requirements address this through a mix of concrete triggers and required management routines:

**Concrete published triggers**
- CQI-12: reduced monitoring frequency is only justified by ≥30 consecutive measurements; if any data point at reduced frequency is outside control limits, revert to minimum monitoring frequencies. This is a published, explicit accumulation logic for drift. citeturn17view1turn19view1  
- Ford: customer concerns require response in 24 hours and delivery of an 8D package with defined milestones and a 15-day timeline; shipped nonconforming product requires notification within 24 hours or sooner. citeturn23view0turn23view3  
- GM: CSII triggers certification-body notification within 5 business days and forces corrective-action verification scrutiny. citeturn22view3  
- GM EPC (Early Production Containment): requires a reaction plan for a **single defect**, treats EPC as the customer, forbids rework at the EPC station, and requires daily management review and cross-shift communication—making single defects escalation triggers during launch containment. citeturn16view3  
- CQI-11 (comparison): hydrogen embrittlement avoidance/relief requires log review prior to shipment and not more than 24 hours—illustrating a hard release gate model. citeturn20view1  

**Structured escalation states**
- **Safe launch / proactive containment**: OEM-required enhanced controls during launch or after shutdowns/changes, with explicit exit criteria. Stellantis requires safe launch and notes PPAP acceptance is not enough to exit. citeturn24view2  
- **Controlled shipping (CS1/CS2/CSL)**: customer-imposed containment levels that typically escalate when the supplier cannot demonstrate effective containment or permanent corrective action. Public supplier containment procedures define CS1 and CS2 as escalation levels, often with third-party involvement at higher levels. citeturn8search6turn8search12turn22view3  

**Regulatory-side “events” coating operations must treat as first-class**
Surface finishing plants can also face regulatory deviations tied to air emissions (e.g., NESHAP for surface coating of miscellaneous metal parts and products) and wastewater pretreatment standards (metal finishing categorical standards). These create event types with reporting obligations and potential production constraints. citeturn27search0turn27search1turn27search3turn27search9  

## Implementation evidence and comparative fit criteria

### Evidence on what tends to work (and what tends to fail)

A useful automotive case study published via entity["organization","Automotive Industry Action Group","north america trade group"] describes how entity["company","Dana Incorporated","automotive supplier"] implemented a global nonconformity system across ~100 plants and thousands of suppliers, replacing a decentralized mix of legacy tools and spreadsheets. The key *failure modes* it identifies are directly relevant to event classification systems:

- Different plants used different systems, rejection criteria, corrective action formats, and problem-solving methods, creating inconsistent data and making supplier visibility and “read across” difficult. citeturn31view0  
- Spreadsheet/email-based workflows created manual data entry and errors, undermining trust in the data and preventing global visibility. citeturn31view0  

The same case study reports that standardized workflows, supplier master data, and centralized visibility allowed quicker global process changes and better cross-plant understanding of supplier issues. citeturn31view0  

Separate research in manufacturing analytics emphasizes that defect classification quality matters because analysts (and increasingly ML/AI systems) depend on consistent, well-structured defect labels; one open-access review notes that manufacturing ML efforts can fail if defect classification is weak, highlighting the need to critically review how defects are classified. citeturn32search25  

On adoption barriers: manufacturing surveys on technology adoption consistently find integration difficulty and skills gaps as major barriers—important because overly complex front-line classification increases training burden and misclassification. citeturn32search23  

### Comparative fit criteria for multi-technology coating operations at different scales

The question is not “which framework is best,” but what each model family is best at **preventing** (missed containment, misrouted customer escapes, chronic drift, etc.). The table below frames that comparison in the context of multi-plant, multi-technology coating operations.

| Model emphasis | Best fit conditions | Where it tends to be strongest | Typical weak points to watch |
|---|---|---|---|
| **Signal-strength tiering** | High-volume operations with lots of “weak signals” (trending chemistry, booth drift) | Prevents waiting for proof; makes “drift” a first-class event that can auto-escalate (CQI-12 revert logic is a concrete example) citeturn17view1 | If the “drift” tier lacks ownership and timeboxed actions, it becomes a parking lot |
| **Event-type routing (process/product/equipment/material/customer/supplier)** | Multi-technology plants where different event classes require different data and owners | Matches CQI-style assessments and coating reality (chemistry, cure, material handling, calibration/pyrometry) citeturn33search15turn19view1 | Taxonomy explosion: too many event types causes misclassification; too few hides root causes |
| **Origin-based classification** | Environments where customer timelines, supplier accountability, and regulatory reporting are dominant constraints | Clean ownership and communication; aligns with Ford shipped-product notification and customer concern clocks citeturn23view0turn23view3 | Can blur technical learning if the system stops at “customer event” and doesn’t capture process detail |
| **Severity/risk-based escalation** | Mix of cosmetic and performance-critical requirements; diverse customer sensitivity | Enables auto-escalation and consistent prioritization; aligns with concession requirements and OEM escalation states (CSII) citeturn12view1turn22view3 | Severity scoring is notoriously inconsistent without explicit decision gates and examples |
| **Containment-state model (safe launch/EPC/controlled shipping)** | Launches, major changes, recovery after shutdowns, or post-escape periods | Very strong “nothing falls through cracks”: explicit containment areas, enhanced controls, exit criteria; GM EPC is explicit about single-defect reaction plans and management review citeturn16view3turn24view2 | Becomes permanent if exit logic is weak; can disguise process capability problems behind inspection |

### A practical synthesis observed across the industry

Across CQI practice, OEM CSRs, and large supplier implementations, the “most scalable” pattern is a **hybrid**:

- **Small, stable set of primary workflows** (Suspect Product, NCR/Disposition, Process Deviation/OOC, Equipment/Calibration, Customer Concern/8D, Supplier SCAR, Audit/System Gap, EHS/Compliance).  
- **Attributes** used for automation and learning: technology (powder/e-coat/liquid), stage (pretreat/application/cure), detection origin, shipped/not shipped, special characteristic flags, and severity.

This aligns with the requirements that actually carry risk in automotive coating: call the event whatever you want internally, but your system must reliably force the right behaviors—containment, authorization, corrective action, prevention of recurrence, and customer-timed responses. citeturn12view0turn12view1turn23view0turn19view1  

## Structured reference tables

The attached workbook contains:

- **Table A — Quality Event Type Master**: 194 coating-relevant event types with definitions, triggers, discoverers, severity defaults, disposition paths, escalation triggers, technology notes, and clause references.  
- **Table B — Decision Gate Reference**: a sequential gate model from first discovery to closure/read-across.  
- **Table C — Escalation Rule Reference**: published and commonly required escalation triggers drawn from CQI logic, OEM CSRs, EPC/safe launch containment logic, and regulatory deviation requirements.

[Download the Excel workbook](sandbox:/mnt/data/Automotive_Coating_Quality_Event_Research_Tables.xlsx)