# XSLT Auto-Refinement Agent

## LOCK · SLICE · ORDER Algorithm

---

## 1. Problem Statement

We need to **validate and refine large, complex XSLT stylesheets** using:

* Huge Input XML
* Existing (often legacy) XSLT
* Generated Output XML
* Target XML (reference implementation)
* Formal Specifications
  (`input_xpath → output_xpath + remarks`)

### Constraints

* Files can be **hundreds of MB**
* XSLT can contain **hundreds of templates**
* LLM context is limited
* Naive “one fix at a time” loops are too slow
* Naive “global refactor” approaches are unsafe

---

## 2. Core Insight

> **XSLT correctness emerges at the template boundary, not at the file level.**

Therefore:

* **Templates** are the unit of stabilization
* **Specs** are the authority
* **Target XML** is discovery-only
* **LLM** is a bounded code editor, not a system reasoner

---

## 3. High-Level Strategy

We use a **batch-oriented, template-centric agent** with three enforced constraints:

### LOCK

Once a template is stabilized, it must never regress.

### SLICE

The LLM and validator must only see **small, isolated harnesses**, never full files.

### ORDER

Structural problems must always be fixed **before** value or formatting problems.

---

## 4. Two Classes of Business Logic

### 4.1 Local Logic (Handled Now)

* Single template
* Single output subtree
* Can be validated via XPath rules

→ Fixed in the **LOCAL_STABILIZATION** phase

### 4.2 Cross-Cutting Logic (Deferred)

* Spans multiple templates
* Global aggregation (totals, currency consistency, etc.)
* Cannot be reasoned locally

→ Detected, classified, and **explicitly deferred** to a later phase

---

## 5. Authoritative Invariants (Non-Negotiable)

1. Spec rules decide correctness
2. Target XML never triggers fixes directly
3. LLM never decides scope
4. Structure before value
5. Context must be local and bounded
6. Templates are locked after stabilization
7. Cross-cutting logic is never fixed opportunistically

Breaking any of these **will cause non-convergence**.

---

## 6. Agent State (Conceptual)

```json
{
  "phase": "LOCAL_STABILIZATION",
  "xslt": "...",
  "input_xml": "...",
  "target_xml": "...",

  "failure_clusters": {
    "T_INVOICE_LINE": [F1, F2, F3]
  },

  "locked_templates": ["T_HEADER"],
  "deferred_cross_cutting": [],

  "context_budget": {
    "max_xslt_lines": 200,
    "max_xml_lines": 80,
    "max_spec_rules": 3
  }
}
```

---

## 7. End-to-End Algorithm (Step by Step)

### STEP 1 — Transform & Analyze (Global, Non-LLM)

1. Apply full XSLT to full input XML
2. Run **spec-based validation**
3. Run **target XML diff** (discovery only)
4. Emit **failures as facts**

Each failure includes:

* output_xpath
* failure type
* structural depth
* responsible template_id

---

### STEP 2 — Classify Failures

For each failure:

**If it is cross-cutting**:

* Touches multiple templates
* Or touches multiple output roots
* Or requires aggregation

→ Move to `deferred_cross_cutting`

**Else**:
→ Eligible for local fixing

---

### STEP 3 — Cluster by Template

Group remaining failures by:

```
template_id → [failures]
```

This is the **only batching dimension** allowed.

---

### STEP 4 — Select Batch Target (Template-First)

1. Skip templates already in `locked_templates`
2. Rank templates by:

   * Number of failures
   * Structural severity
3. Pick **one template only**

---

### STEP 5 — Structural Ordering Inside the Batch

Failures inside the template are sorted by:

1. Failure category

   ```
   MISSING_NODE >
   EXTRA_NODE >
   CARDINALITY >
   ATTRIBUTE >
   VALUE >
   FORMAT
   ```

2. Structural depth
   (parent nodes before child nodes)

This prevents:

* Hallucinated guards
* Over-engineered `xsl:choose`
* Fixing values on missing nodes

---

### STEP 6 — Create Dependency-Aware Harness (SLICE)

#### Input Slice

* Extract only nodes matched by the template’s `match=`
* Limit to a small sample (3–5 nodes)

#### Target Slice

* Extract corresponding expected output nodes

#### Template Slice

* Extract the target `<xsl:template>`

#### Dependency Resolution

* Inject:

  * Named templates called via `xsl:call-template`
  * Global variables referenced
* Mark dependencies **read-only**

Result:

* A **standalone, valid XSLT**
* Small enough for LLM + fast validation

---

### STEP 7 — LLM Batch Fix

LLM receives:

* Template slice
* Ordered failure list
* Relevant spec rules
* Input slice
* Target slice

Hard rules in prompt:

* Fix in listed order
* No dependency modification
* No scope expansion
* Return **full updated template only**

---

### STEP 8 — Harness Verification

Run harness XSLT against input slice.

Reject immediately if:

* XSLT fails to compile
* Dependencies modified
* XPath scope widened (`//` abuse)
* New structural regressions appear

Accept only if:

* All batched failures resolved
* No new slice-level issues

---

### STEP 9 — Apply & Lock

1. Merge updated template into full XSLT
2. Re-validate only:

   * This template’s output subtree
   * Related spec rules
3. If **zero failures remain**:

   * Add template to `locked_templates`

Locked templates are immutable unless a **new structural failure** appears.

---

### STEP 10 — Termination Check

Stop when:

* No local failures remain
* OR only cross-cutting failures remain
* OR max iterations reached

If only cross-cutting remains:
→ Transition to `GLOBAL_INTEGRATION` phase (future work)

---

## 8. Why This Converges

* **Monotonic**: failures only decrease
* **Local**: fixes never affect unrelated templates
* **Bounded**: LLM context never explodes
* **Locked**: no regression loops
* **Ordered**: structure stabilizes first

---

## 9. What This System Deliberately Does NOT Do

* Infer missing business rules
* Fix cross-cutting logic
* Refactor XSLT for elegance
* Optimize performance
* Guess intent from target XML

Those are **separate phases by design**.

---

## 10. Mental Model (Keep This)

> You are not “fixing XML mappings”.
> You are **stabilizing templates under executable contracts**.

The LLM is a tool.
The agent enforces discipline.
The spec is law.

---

## 11. Current Status

* LOCAL_STABILIZATION: ✅ implemented
* GLOBAL_INTEGRATION: ⏳ future phase
* Cross-cutting logic: detected & deferred

---

## 12. Next Possible Extensions

* Cross-cutting integration phase
* Schematron-based validators
* Confidence metrics
* Visualization of failure trees
* Audit logs for compliance

---
