from lxml import etree
from typing import Optional, List


XSL_NS = "http://www.w3.org/1999/XSL/Transform"
NSMAP = {"xsl": XSL_NS}


prompt_t = """You are an expert XSLT engineer.
You are fixing a SMALL, ISOLATED XSLT fragment extracted from a larger monolithic stylesheet.
The fragment is responsible for producing a specific output XPath.

=== SPEC-VALIDATED DIFF (GROUND TRUTH) ===
Output XPath: {output_xpath}
Issue Type: {status}
Expected Behavior:
{expected_rule}

{optional_expected_source_xpath_block}

=== XSLT SLICE (EDITABLE) ===
{xslt_slice}

=== RULES (STRICT) ===
1. Modify ONLY the provided XSLT slice.
2. Do NOT refactor, rename, or reformat unrelated parts.
3. Do NOT introduce new templates, modes, or apply-templates.
4. Do NOT assume any context outside this slice.
5. Preserve existing structure, ordering, and namespaces.
6. Output MUST be valid XSLT/XML.
7. Return ONLY the corrected XSLT slice. No explanations.

=== TASK ===
Rewrite the XSLT slice so that it satisfies the expected behavior.

"""



CONTROL_TAGS = {
    f"{{{XSL_NS}}}for-each",
    f"{{{XSL_NS}}}if",
    f"{{{XSL_NS}}}choose",
    f"{{{XSL_NS}}}template",
}


def is_literal_result(elem):
    return (
        not str(elem.tag).startswith(f"{{{XSL_NS}}}")
        and elem.tag is not etree.Comment
    )


def find_behavioral_boundary(node: etree._Element) -> etree._Element:
    current = node

    while current.getparent() is not None:
        parent = current.getparent()

        # Stop at for-each / if / choose
        if parent.tag in {
            f"{{{XSL_NS}}}for-each",
            f"{{{XSL_NS}}}if",
            f"{{{XSL_NS}}}choose",
        }:
            return parent

        # Stop at enclosing literal-result block
        if is_literal_result(current) and is_literal_result(parent):
            return current

        current = parent

    return current



def collect_dependencies(boundary: etree._Element) -> List[etree._Element]:
    """
    Collect variable declarations and value-of instructions
    used within the boundary.
    """
    deps = []
    for elem in boundary.iter():
        if elem.tag in {
            f"{{{XSL_NS}}}variable",
            f"{{{XSL_NS}}}value-of",
            f"{{{XSL_NS}}}attribute",
        }:
            deps.append(elem)
    return deps


def extract_xslt_slice(xslt_str: str, diff: dict) -> str:
    xslt_root = etree.XML(xslt_str.encode())
    output_xpath = diff["output_xpath"]

    anchor_node, missing_tail = find_nearest_existing_output_node(xslt_root, output_xpath)

    if anchor_node is None:
        raise ValueError(f"Cannot locate any parent for {output_xpath}")

    boundary = find_behavioral_boundary(anchor_node)

    slice_copy = etree.fromstring(etree.tostring(boundary))

    return etree.tostring(
        slice_copy,
        pretty_print=True,
        encoding="unicode"
    )




def local_name(tag):
    # Ensure tag is converted to a string if it's a cython object
    tag_str = str(tag) 
    if tag_str.startswith("{"):
        return tag_str.split("}", 1)[1]
    return tag_str



from lxml import etree

def matches_output_node(elem: etree._Element, target_name: str) -> bool:
    # Ignore comments, PIs, etc.
    if not isinstance(elem.tag, str):
        return False

    # Case 1: literal result element (any namespace)
    if not elem.tag.startswith(f"{{{XSL_NS}}}"):
        return etree.QName(elem).localname == target_name

    # Case 2: xsl:element name="Buyer" or name="ns4:Buyer"
    if elem.tag == f"{{{XSL_NS}}}element":
        name = elem.get("name")
        if name:
            return name.split(":")[-1] == target_name

    return False



def find_nearest_existing_output_node(xslt_root: etree._Element, output_xpath: str):
    parts = output_xpath.strip("/").split("/")

    # Try deepest → shallowest
    for i in range(len(parts), 0, -1):
        candidate = parts[i - 1]

        for elem in xslt_root.iter():
            if matches_output_node(elem, candidate):
                return elem, parts[i:]  # remaining missing path

    return None, None


def find_output_node(xslt_root: etree._Element, output_xpath: str) -> Optional[etree._Element]:
    """
    Locate the XSLT node responsible for producing the final element in output_xpath.
    """
    target_name = output_xpath.strip("/").split("/")[-1]
    print(target_name)

    for elem in xslt_root.iter():
        print(elem.tag)
        if matches_output_node(elem, target_name):
            return elem

    return None
