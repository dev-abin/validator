from slicer import find_nearest_existing_output_node

XSL_NS = "http://www.w3.org/1999/XSL/Transform"

from safety_check import (
    assert_same_root_tag,
    assert_no_forbidden_xsl,
    assert_single_root,
    assert_output_xpath_exists,
)

def find_anchor_node(xslt_root, output_xpath):
    anchor, _ = find_nearest_existing_output_node(xslt_root, output_xpath)
    if anchor is None:
        raise ValueError("Anchor node not found for reinsertion")
    return anchor


def ensure_xsl_namespace(xml_fragment: str) -> str:
    """
    Ensure xmlns:xsl is declared on the fragment root if xsl: is used.
    """
    if "xsl:" not in xml_fragment:
        return xml_fragment

    # If already declared, do nothing
    if 'xmlns:xsl=' in xml_fragment:
        return xml_fragment

    # Inject namespace into root element
    xml_fragment = xml_fragment.strip()

    if not xml_fragment.startswith("<"):
        raise ValueError("Invalid XML fragment")

    # Insert xmlns:xsl into first tag
    end = xml_fragment.find(">")
    if end == -1:
        raise ValueError("Malformed XML fragment")

    root_tag = xml_fragment[:end]
    rest = xml_fragment[end:]

    injected = (
        f'{root_tag} xmlns:xsl="{XSL_NS}"{rest}'
    )

    return injected



from lxml import etree

from lxml import etree

def replace_xslt_slice(
    xslt_string: str,
    output_xpath: str,
    fixed_slice_xml: str
) -> str:
    """
    Replace the responsibility slice in the original XSLT with the fixed slice.
    """

    # 1. Parse original XSLT ONCE
    xslt_root = etree.XML(xslt_string.encode())
    

    # 1. Inject namespace FIRST
    fixed_slice_xml = ensure_xsl_namespace(fixed_slice_xml)

    # 2. Now it is safe to parse / validate
    assert_single_root(fixed_slice_xml)
    fixed_elem = etree.XML(fixed_slice_xml.encode())

    
    # -------------------------
    # Locate anchor
    # -------------------------
    anchor_node, _ = find_nearest_existing_output_node(xslt_root, output_xpath)
    if anchor_node is None:
        raise ValueError("Anchor node not found")
    
        # -------------------------
    # Structural safety checks
    # -------------------------
    assert_same_root_tag(anchor_node, fixed_elem)
    assert_no_forbidden_xsl(fixed_elem)

    parent = anchor_node.getparent()
    if parent is None:
        raise ValueError("Anchor node has no parent; cannot replace")

    # 4. Preserve formatting
    fixed_elem.tail = anchor_node.tail

    # 5. Replace node
    parent.replace(anchor_node, fixed_elem)

    updated_xslt = etree.tostring(
        xslt_root,
        pretty_print=True,
        encoding="unicode"
    )

    # -------------------------
    # Post-merge validation
    # -------------------------
    assert_output_xpath_exists(updated_xslt, output_xpath)

    return updated_xslt
