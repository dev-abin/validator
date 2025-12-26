from lxml import etree

XSL_NS = "http://www.w3.org/1999/XSL/Transform"

# =========================
# 1. Root consistency check
# =========================

def assert_same_root_tag(anchor_node: etree._Element, fixed_elem: etree._Element):
    """
    Ensure the fixed slice root matches the original anchor root.
    Prevents structural corruption.
    """
    if anchor_node.tag != fixed_elem.tag:
        raise ValueError(
            f"Unsafe replacement: root tag mismatch "
            f"(expected {anchor_node.tag}, got {fixed_elem.tag})"
        )

# =========================
# 2. Single-root fragment check
# =========================

def assert_single_root(xml_fragment: str):
    """
    Ensure fragment has exactly one root element.
    """
    try:
        etree.XML(xml_fragment.encode())
    except etree.XMLSyntaxError as e:
        raise ValueError(f"Invalid XML fragment: {e}")

# =========================
# 3. Forbidden XSL instructions check
# =========================

FORBIDDEN_XSL_TAGS = {
    f"{{{XSL_NS}}}template",
    f"{{{XSL_NS}}}apply-templates",
    f"{{{XSL_NS}}}call-template",
    f"{{{XSL_NS}}}import",
    f"{{{XSL_NS}}}include",
}

def assert_no_forbidden_xsl(fixed_elem: etree._Element):
    """
    Prevent global behavior changes.
    """
    for elem in fixed_elem.iter():
        if elem.tag in FORBIDDEN_XSL_TAGS:
            raise ValueError(
                f"Forbidden XSL instruction introduced: {elem.tag}"
            )

# =========================
# 4. Output XPath existence check (post-merge)
# =========================

def assert_output_xpath_exists(xslt_string: str, output_xpath: str):
    """
    Validate that the output XPath is now produced by the XSLT.
    Static structural check (not execution-based).
    """
    xslt_root = etree.XML(xslt_string.encode())
    target = output_xpath.strip("/").split("/")[-1]

    for elem in xslt_root.iter():
        if isinstance(elem.tag, str) and etree.QName(elem).localname == target:
            return

    raise ValueError(
        f"Post-merge validation failed: output XPath not found: {output_xpath}"
    )
