import copy
import re
from lxml import etree


# =========================
# FAILURE CLASSIFICATION
# =========================

def is_cross_cutting(failure: dict) -> bool:
    return (
        failure.get("is_global", False)
        or len(failure.get("templates_involved", [])) > 1
    )


def cluster_failures(failures: list[dict]):
    clusters = {}
    deferred = []

    for f in failures:
        if is_cross_cutting(f):
            deferred.append(f)
            continue

        tid = f["template_id"]
        clusters.setdefault(tid, []).append(f)

    return clusters, deferred


# =========================
# STRUCTURAL PRIORITY
# =========================

TYPE_PRIORITY = {
    "MISSING_ELEMENT": 0,
    "EXTRA_ELEMENT": 1,
    "CARDINALITY_FAIL": 2,
    "ATTRIBUTE_MISSING": 3,
    "VALUE_MISMATCH": 4,
    "FORMAT_ERROR": 5,
}


def prioritize_failures(failures: list[dict]) -> list[dict]:
    def key(f):
        return (
            TYPE_PRIORITY.get(f["type"], 99),
            f["xpath"].count("/")
        )
    return sorted(failures, key=key)


# =========================
# TEMPLATE SELECTION
# =========================

def select_template_to_fix(state):
    candidates = [
        (tid, fails)
        for tid, fails in state.failure_clusters.items()
        if tid not in state.locked_templates
    ]

    if not candidates:
        return {}

    # highest impact first
    tid, fails = max(candidates, key=lambda x: len(x[1]))

    return {
        "template_id": tid,
        "failures": fails
    }


# =========================
# XSLT EXTRACTION / MERGE
# =========================

def extract_template(xslt: str, template_id: str) -> str:
    pattern = rf'(<xsl:template[^>]+{template_id}[^>]*>.*?</xsl:template>)'
    match = re.search(pattern, xslt, re.DOTALL)
    if not match:
        raise ValueError(f"Template {template_id} not found")
    return match.group(1)


def replace_template(xslt: str, template_id: str, new_template: str) -> str:
    pattern = rf'<xsl:template[^>]+{template_id}[^>]*>.*?</xsl:template>'
    return re.sub(pattern, new_template, xslt, flags=re.DOTALL)


# =========================
# XML SLICING
# =========================

def slice_input_xml(input_xml: str, match_expr: str, limit=5) -> str:
    root = etree.fromstring(input_xml.encode())
    nodes = root.xpath(f"//{match_expr}")

    wrapper = etree.Element("SliceWrapper")
    for n in nodes[:limit]:
        wrapper.append(copy.deepcopy(n))

    return etree.tostring(wrapper, pretty_print=True).decode()


def slice_target_xml(target_xml: str, output_xpath: str, limit=5) -> str:
    root = etree.fromstring(target_xml.encode())
    nodes = root.xpath(output_xpath)

    wrapper = etree.Element("SliceWrapper")
    for n in nodes[:limit]:
        wrapper.append(copy.deepcopy(n))

    return etree.tostring(wrapper, pretty_print=True).decode()


# =========================
# DEPENDENCY RESOLUTION
# =========================

def resolve_dependencies(xslt: str, template_str: str) -> str:
    deps = []

    # named templates
    for name in re.findall(r'call-template name="([^"]+)"', template_str):
        pat = rf'(<xsl:template name="{name}".*?</xsl:template>)'
        m = re.search(pat, xslt, re.DOTALL)
        if m:
            deps.append(m.group(1))

    # global variables
    for var in set(re.findall(r'\$([A-Za-z0-9_-]+)', template_str)):
        pat = rf'(<xsl:variable name="{var}".*?</xsl:variable>)'
        m = re.search(pat, xslt, re.DOTALL)
        if m:
            deps.append(m.group(1))

    return "\n".join(deps)


def build_harness_xslt(template: str, dependencies: str) -> str:
    return f"""
<xsl:stylesheet version="2.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
{dependencies}
{template}
</xsl:stylesheet>
"""


# =========================
# LLM OUTPUT GUARDS
# =========================

def validate_llm_output(proposed: str, dependencies: str) -> None:
    # dependency immutability
    for dep in re.findall(r'<xsl:(template|variable).*?>', dependencies):
        if dep in proposed:
            raise ValueError("LLM modified dependency section")

    # scope widening
    if "//" in proposed:
        raise ValueError("XPath scope widening detected")


# =========================
# FULL ANALYSIS
# =========================

def analyze_failures(state):
    output_xml = apply_xslt(state.input_xml, state.xslt)
    failures = []

    for spec in read_specifications():
        result = spec.validate(state.input_xml, output_xml)
        if not result.ok:
            failures.append(result.to_failure())

    return failures
