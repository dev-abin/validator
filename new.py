from lxml import etree
from copy import deepcopy
from typing import List, Dict

XSL_NS = "http://www.w3.org/1999/XSL/Transform"
XSL = f"{{{XSL_NS}}}"


# ============================================================
# Diff handling
# ============================================================

def get_anchor_xpath(output_xpath: str) -> str:
    parts = [p for p in output_xpath.split("/") if p]
    if len(parts) <= 2:
        return "/" + "/".join(parts)

    # Heuristic: drop leaf AND value-level nodes
    VALUE_NODES = {
        "Amount", "BaseAmount", "TotalAmount", "Tax", "TaxCode",
        "DescText", "Remark", "ID", "Code"
    }

    while len(parts) > 2 and parts[-1] in VALUE_NODES:
        parts.pop()

    return "/" + "/".join(parts)

def has_extra(diffs):
    return any(d["diff_type"] == "EXTRA" for d in diffs)

def has_missing(diffs):
    return any(d["diff_type"] == "MISSING" for d in diffs)


def group_diffs_by_anchor(diffs: List[Dict]) -> Dict[str, List[Dict]]:
    grouped = {}
    for d in diffs:
        anchor = get_anchor_xpath(d["output_xpath"])
        grouped.setdefault(anchor, []).append(d)
    return grouped


def anchor_priority(diffs: List[Dict]) -> int:
    """
    EXTRA → 0
    MISSING → 1
    COUNT_MISMATCH → 2
    """
    types = {d["diff_type"] for d in diffs}
    if types == {"EXTRA"}:
        return 0
    if types == {"MISSING"}:
        return 1
    return 2


# ============================================================
# XSLT navigation
# ============================================================

def parse_xslt(xslt_str: str) -> etree._Element:
    return etree.XML(xslt_str.encode("utf-8"))


def local_name(node):
    return etree.QName(node).localname


def find_literal_nodes(root, tag_name):
    return root.xpath(f"//*[local-name()='{tag_name}']")


def score_match(node, anchor_parts):
    score = 0
    cur = node
    for expected in reversed(anchor_parts):
        cur = cur.getparent()
        if cur is None:
            break
        if local_name(cur) == expected:
            score += 1
        else:
            break
    return score


def locate_best_node(root, anchor_xpath: str):
    parts = [p for p in anchor_xpath.split("/") if p]
    if not parts:
        return None

    leaf = parts[-1]
    candidates = find_literal_nodes(root, leaf)

    if not candidates:
        return None

    scored = [(score_match(c, parts[:-1]), c) for c in candidates]
    scored.sort(key=lambda x: x[0], reverse=True)

    best_score, best_node = scored[0]
    if best_score == 0:
        return None

    return best_node



def find_loop_owner(node):
    cur = node
    while cur is not None:
        if cur.tag in (XSL + "for-each", XSL + "apply-templates"):
            return cur

        # Literal element that contains a for-each → treat as owner
        if any(
            child.tag in (XSL + "for-each", XSL + "apply-templates")
            for child in cur
        ):
            return cur

        cur = cur.getparent()
    return None



# ============================================================
# Snippet + Context
# ============================================================

def extract_snippet(loop_node) -> str:
    return etree.tostring(loop_node, pretty_print=True, encoding="unicode")


def extract_context(loop_node) -> str:
    """
    Minimal read-only context:
    parent xsl:for-each nodes only.
    """
    ctx = []
    cur = loop_node.getparent()
    while cur is not None:
        if cur.tag == XSL + "for-each":
            ctx.append(etree.tostring(cur, pretty_print=True, encoding="unicode"))
        cur = cur.getparent()
    return "\n".join(ctx)


# ============================================================
# Prompt
# ============================================================

def build_prompt(anchor, diffs, snippet, context) -> str:
    return f"""
You are fixing ONE XSLT BLOCK.

ANCHOR:
{anchor}

DIFFS:
{diffs}

READ-ONLY CONTEXT (do not modify):
{context}

EDITABLE BLOCK (ONLY THIS):
```xml
{snippet}
```

RULES:

* Modify ONLY the editable block
* Do NOT change element names or namespaces
* Fix ONLY the listed diffs
* COUNT_MISMATCH → fix loop structure
* EXTRA → add guards or remove emission
* MISSING → add missing output in correct loop

Return ONLY valid XSLT XML. No explanation.
"""


# ============================================================
# Validation
# ============================================================

def xslt_compiles(xslt_root) -> bool:
    try:
        etree.XSLT(xslt_root)
        return True
    except Exception:
        return False


# ============================================================
# DOM patching
# ============================================================

def replace_node(old_node, new_node):
    parent = old_node.getparent()
    index = list(parent).index(old_node)
    parent.remove(old_node)
    parent.insert(index, new_node)


def anchor_has_extra(diffs):
    return any(d["diff_type"] == "EXTRA" for d in diffs)


# ============================================================
# Main refinement function
# ============================================================

def refine_xslt(xslt_str: str, spec_validated_diff: List[Dict]) -> str:
    xslt_root = parse_xslt(xslt_str)
    snapshot = deepcopy(xslt_root)

    grouped = group_diffs_by_anchor(spec_validated_diff)
    
    print(grouped)

    ordered_anchors = sorted(
        grouped.keys(),
        key=lambda a: anchor_priority(grouped[a])
    )
    
    print(ordered_anchors)

    locked = set()

    for anchor in ordered_anchors:
        if anchor in locked:
            continue

        diffs = grouped[anchor]

        literal_node = locate_best_node(xslt_root, anchor)
        print(literal_node)
        if literal_node is None:
            continue

        loop_node = find_loop_owner(literal_node)
        print(loop_node)
        if loop_node is None:
            continue

        snippet = extract_snippet(loop_node)
        context = extract_context(loop_node)
        
        print(snippet)
        print(context)

        prompt = build_prompt(anchor, diffs, snippet, context)
        
        for _ in range(2):
            fixed_snippet = get_llm_response(prompt)
            try:
                new_loop = etree.XML(fixed_snippet.encode("utf-8"))
                break
            except Exception:
                new_loop = None

        if new_loop is None:
            xslt_root = deepcopy(snapshot)
            continue
        new_loop = None

        test_root = deepcopy(xslt_root)
        test_literal = locate_best_node(test_root, anchor)
        test_loop = find_loop_owner(test_literal)

        replace_node(test_loop, new_loop)

        if not xslt_compiles(test_root):
            xslt_root = deepcopy(snapshot)
            continue

        # If this anchor had EXTRA, ensure snippet actually changed
        if anchor_has_extra(diffs):
            if etree.tostring(loop_node) == etree.tostring(new_loop):
                xslt_root = deepcopy(snapshot)
                continue

        # Commit
        # Enforce semantic change for EXTRA / MISSING
        if (has_extra(diffs) or has_missing(diffs)) and \
        etree.tostring(loop_node) == etree.tostring(new_loop):
            xslt_root = deepcopy(snapshot)
            continue

        # Commit
        replace_node(loop_node, new_loop)
        snapshot = deepcopy(xslt_root)
        locked.add(anchor)



    return etree.tostring(xslt_root, pretty_print=True, encoding="unicode")


def parse_diff(file_path):
    """
    Reads a text file containing string-represented dictionaries 
    and returns a list of dictionaries.
    """
    import ast
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
    
import copy
import json
import time
from pathlib import Path
from collections import defaultdict
from typing import List, Dict

from lxml import etree


XSLT_PATH = "initial.xslt"


def read_file(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")

if __name__ == "__main__":
    xslt_str = read_file(XSLT_PATH)
    spec_diffs = parse_diff('spec_diffs.txt')
    fixed_xslt = refine_xslt(xslt_str, spec_diffs)
