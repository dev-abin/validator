import copy
import json
import time
from pathlib import Path
from collections import defaultdict
from typing import List, Dict

from lxml import etree

# ==============================
# CONFIG
# ==============================

XSLT_PATH = "initial.xslt"

OUTPUT_XSLT_PATH = "refined.xslt"

MAX_ITERATIONS = 8
MODEL = "gpt-4.1"


# ==============================
# IO HELPERS
# ==============================

def read_file(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")

def write_file(path: str, content: str):
    Path(path).write_text(content, encoding="utf-8")

def parse_xml(xml: str) -> etree._Element:
    return etree.XML(xml.encode())

# ==============================
# SPEC VALIDATION (PLUG-IN)
# ==============================

def validate_against_specs(xslt_str: str) -> List[Dict]:
    """
    MUST RETURN spec_diffs in the SAME STRUCTURE you already use.
    This is the ONLY external dependency.
    """
    raise NotImplementedError("Hook your existing spec validation here")


import ast

def parse_diff(file_path):
    """
    Reads a text file containing string-represented dictionaries 
    and returns a list of dictionaries.
    """
    data_list = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                # Strip whitespace and check if the line is not empty
                line = line.strip()
                if line:
                    try:
                        # Safely convert the string line into a dictionary
                        dict_data = ast.literal_eval(line)
                        data_list.append(dict_data)
                    except (ValueError, SyntaxError) as e:
                        print(f"Skipping malformed line: {line[:50]}... Error: {e}")
                        
        return data_list
    
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return []




# ==============================
# XSLT APPLY (PLUG-IN)
# ==============================

def apply_xslt(xslt_str: str, input_xml: str) -> str:
    xslt_root = etree.XML(xslt_str.encode())
    transform = etree.XSLT(xslt_root)
    return str(transform(etree.XML(input_xml.encode())))

# ==============================
# DIFF CLASSIFICATION
# ==============================

def classify_diffs(spec_diffs: List[Dict]):
    removals, count_fixes, missing = [], [], []

    for d in spec_diffs:
        cat = d.get("issue_category", "")
        if "Remove from XSLT" in cat:
            removals.append(d)
        elif "Wrong Count" in cat:
            count_fixes.append(d)
        elif "Missing output" in cat:
            missing.append(d)

    return removals, count_fixes, missing

def xpath_parent(xpath: str) -> str:
    return "/".join(xpath.rstrip("/").split("/")[:-1])

# ==============================
# XSLT TREE OPS
# ==============================

def remove_xpath(tree: etree._Element, output_xpath: str):
    """
    Remove XSLT instructions that generate an overgenerated output element.
    This operates on the XSLT AST, not on output XML paths.
    """

    leaf = output_xpath.rstrip("/").split("/")[-1]

    ns = {
        "xsl": "http://www.w3.org/1999/XSL/Transform"
    }

    removed = False

    # 1️⃣ Literal output elements <PaymentCard>
    for node in tree.xpath(f"//*[local-name()='{leaf}']"):
        parent = node.getparent()
        if parent is not None:
            parent.remove(node)
            print("removed here","//*[local-name()")
            removed = True

    # 2️⃣ xsl:element name="PaymentCard"
    for node in tree.xpath(
        f"//xsl:element[@name='{leaf}']",
        namespaces=ns
    ):
        parent = node.getparent()
        if parent is not None:
            parent.remove(node)
            print("removed here","//xsl:element[@name=")
            removed = True

    # 3️⃣ xsl:for-each selecting PaymentCard
    for node in tree.xpath(
        f"//xsl:for-each[contains(@select, '{leaf}')]",
        namespaces=ns
    ):
        parent = node.getparent()
        if parent is not None:
            parent.remove(node)
            print("removed here","//xsl:for-each[contains(@select")
            removed = True

    # 4️⃣ xsl:copy-of selecting PaymentCard
    for node in tree.xpath(
        f"//xsl:copy-of[contains(@select, '{leaf}')]",
        namespaces=ns
    ):
        parent = node.getparent()
        if parent is not None:
            parent.remove(node)
            print("removed here","//xsl:copy-of[contains(@select")
            removed = True

    if not removed:
        print(f"[WARN] Overgenerated node '{leaf}' not found in XSLT")


def extract_slice(tree: etree._Element, anchor_xpath: str) -> etree._Element:
    """
    Robust slice extractor for monolithic XSLTs.

    Resolution order:
    1. Literal element with local-name == anchor leaf
    2. xsl:for-each whose select ends with anchor leaf
    3. Closest ancestor that constructs the anchor leaf
    """

    anchor_leaf = anchor_xpath.rstrip("/").split("/")[-1]

    ns = {
        "xsl": "http://www.w3.org/1999/XSL/Transform"
    }

    # 1️⃣ Literal element construction
    elems = tree.xpath(f"//*[local-name()='{anchor_leaf}']")
    if elems:
        return copy.deepcopy(elems[0])

    # 2️⃣ for-each selecting the anchor
    for_each = tree.xpath(
        f"//xsl:for-each[contains(@select, '{anchor_leaf}')]",
        namespaces=ns
    )
    if for_each:
        return copy.deepcopy(for_each[0])

    # 3️⃣ xsl:element name="Anchor"
    xsl_elem = tree.xpath(
        f"//xsl:element[@name='{anchor_leaf}']",
        namespaces=ns
    )
    if xsl_elem:
        return copy.deepcopy(xsl_elem[0])

    raise ValueError(f"Anchor not found in XSLT by heuristic: {anchor_xpath}")


def replace_slice(tree: etree._Element, anchor_xpath: str, new_slice: etree._Element):
    anchor_leaf = anchor_xpath.rstrip("/").split("/")[-1]

    ns = {"xsl": "http://www.w3.org/1999/XSL/Transform"}

    candidates = (
        tree.xpath(f"//*[local-name()='{anchor_leaf}']") +
        tree.xpath(f"//xsl:for-each[contains(@select, '{anchor_leaf}')]", namespaces=ns) +
        tree.xpath(f"//xsl:element[@name='{anchor_leaf}']", namespaces=ns)
    )

    if not candidates:
        raise ValueError(f"Anchor not found for replacement: {anchor_xpath}")

    old = candidates[0]
    parent = old.getparent()
    idx = parent.index(old)

    parent.remove(old)
    parent.insert(idx, new_slice)

# ==============================
# LLM CORE — FULL IMPLEMENTATION
# ==============================

def llm_fix_slice(slice_xml: str, diffs: List[Dict]) -> str:
    """
    HARD CONTRACT:
    - Fix iteration cardinality first
    - Use expected_source_path as iteration anchor
    - Explode loops when PaxSegmentRefID-like rules apply
    - Remove overgenerated nodes
    - Add missing mandatory nodes
    - Preserve namespaces
    - Output VALID XSLT XML ONLY
    """

    system_prompt = """
    You are a senior XSLT architect fixing a production transformation.

    Rules you MUST follow:
    1. Cardinality correctness is NON-NEGOTIABLE.
    2. COUNT_MISMATCH means iteration logic is wrong — FIX LOOPS FIRST.
    3. If a parent has multiple logical associations (e.g. PaxSegmentRefID),
    you MUST explode the parent node, not nest the association.
    4. Remove nodes explicitly marked as overgenerated.
    5. Add nodes explicitly marked as missing.
    6. Do NOT invent data.
    7. Do NOT change unrelated logic.
    8. Output ONLY valid XSLT XML — no commentary.
    9. You MUST preserve the outermost element of the slice exactly
    (same element name, same namespace, same position).
    10. For every COUNT_MISMATCH diff, the number of output elements
        produced by this slice MUST match the target count implied by the diff.
    """


    user_prompt = f"""
    === BROKEN XSLT SLICE ===
    {slice_xml}

    === SPEC-VALIDATED DIFFS FOR THIS SLICE ===
    {json.dumps(diffs, indent=2)}

    === TASK ===
    Rewrite this slice so that ALL above diffs are resolved.
    """


    resp = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    return resp.choices[0].message.content.strip()

# ==============================
# MAIN REFINEMENT LOOP
# ==============================
def prune_dominated_anchors(anchors: list[str]) -> list[str]:
    """
    Keep only highest (structural) anchors.
    If /A/B is kept, drop /A/B/C, /A/B/D, etc.
    """
    anchors = sorted(anchors, key=lambda x: x.count("/"))
    kept = []
    # print(anchors)
    print(len(anchors))
    for a in anchors:
        if not any(a.startswith(k + "/") for k in kept):
            kept.append(a)
        
    # print(kept)
    print(len(kept))
    return kept


def refine(xslt_str: str) -> str:
    """
    Iteratively refines a monolithic XSLT until spec diffs converge to zero.

    Safety guarantees:
    - Spec diffs must strictly decrease each iteration
    - Structural anchors are dominance-pruned
    - Invalid XSLT is rejected immediately
    - Infinite loops and regressions are prevented
    """

    xslt_tree = etree.XML(xslt_str.encode())
    prev_diff_count = None
    
    spec_diffs = parse_diff('spec_diffs.txt')

    for iteration in range(1, MAX_ITERATIONS + 1):
        print(f"\n===== ITERATION {iteration} =====")

        # ---- Spec validation (ground truth) ----
        # spec_diffs = validate_against_specs(xslt_str)
        curr_diff_count = len(spec_diffs)

        print(f"Spec diffs: {curr_diff_count}")

        # ---- Convergence ----
        if curr_diff_count == 0:
            print("✅ Converged: no spec diffs remaining")
            return xslt_str

        # ---- Progress monotonicity check ----
        if prev_diff_count is not None and curr_diff_count >= prev_diff_count:
            raise RuntimeError(
                f"❌ No progress detected: prev={prev_diff_count}, curr={curr_diff_count}"
            )
        prev_diff_count = curr_diff_count

        # ---- Classify diffs ----
        removals, count_fixes, _ = classify_diffs(spec_diffs)
        print(len(count_fixes))
        # print(count_fixes)

        # ---- Phase 1: Remove overgeneration ----
        for d in removals:
            print(f"Removing overgenerated node: {d['output_xpath']}")
            remove_xpath(xslt_tree, d["output_xpath"])

        # ---- Phase 2: Build raw anchor groups ----
        raw_groups = defaultdict(list)
        for d in count_fixes:
            anchor = d.get("expected_source_path") or xpath_parent(d["output_xpath"])
            raw_groups[anchor].append(d)
            
        # print(raw_groups)
        print(len(raw_groups))

        if not raw_groups:
            raise RuntimeError(
                "❌ Spec diffs remain but no fixable COUNT_MISMATCH anchors found"
            )

        # ---- Phase 3: Dominance pruning (CRITICAL) ----
        anchors = prune_dominated_anchors(list(raw_groups.keys()))
        groups = {a: raw_groups[a] for a in anchors}

        print("Anchors to fix:")
        for a in anchors:
            print(f"  - {a}")

        # ---- Phase 4: Fix each anchor slice ----
        for anchor, diffs in groups.items():
            print(f"\nFixing slice @ {anchor}")

            slice_el = extract_slice(xslt_tree, anchor)
            slice_xml = etree.tostring(slice_el, pretty_print=True).decode()
            
            print(slice_xml)

            # fixed_xml = llm_fix_slice(slice_xml, diffs)
            # fixed_el = etree.XML(fixed_xml.encode())
            print("assume llm fixed it")

            # replace_slice(xslt_tree, anchor, fixed_el)

            # ---- Structural validity check ----
            try:
                etree.XML(etree.tostring(xslt_tree))
            except Exception as e:
                raise RuntimeError(
                    f"❌ XSLT became invalid after fixing anchor {anchor}"
                ) from e

        # ---- Update working XSLT ----
        xslt_str = etree.tostring(xslt_tree, pretty_print=True).decode()

    # ---- Hard termination ----
    raise RuntimeError("❌ Max iterations reached without convergence")


# ==============================
# ENTRY POINT
# ==============================

if __name__ == "__main__":
    xslt = read_file(XSLT_PATH)

    final_xslt = refine(xslt)

    write_file(OUTPUT_XSLT_PATH, final_xslt)

    print("\n🎯 XSLT refinement complete.")
