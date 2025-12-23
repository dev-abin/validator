from lxml import etree

XSL_NS = "http://www.w3.org/1999/XSL/Transform"
NS = {"xsl": XSL_NS}

SAFE_BOUNDARIES = {
    f"{{{XSL_NS}}}for-each",
    f"{{{XSL_NS}}}if",
    f"{{{XSL_NS}}}choose",
    f"{{{XSL_NS}}}template",
}

def find_producing_nodes(xslt_tree, output_local_name):
    nodes = []

    for el in xslt_tree.iter():
        if not el.tag.startswith("{") and el.tag == output_local_name:
            nodes.append(el)

    for el in xslt_tree.xpath("//xsl:element", namespaces=NS):
        if el.get("name") == output_local_name:
            nodes.append(el)

    return nodes


def expand_to_safe_boundary(node):
    cur = node
    while cur is not None:
        if cur.tag in SAFE_BOUNDARIES:
            return cur
        cur = cur.getparent()
    return None


def extract_slice(xslt_tree, boundary_node):
    full = etree.tostring(xslt_tree, pretty_print=True, encoding="unicode")
    frag = etree.tostring(boundary_node, pretty_print=True, encoding="unicode")

    start = full.find(frag)
    if start == -1:
        raise RuntimeError("Slice not found")

    start_line = full[:start].count("\n")
    end_line = start_line + frag.count("\n")

    return frag, (start_line, end_line)
