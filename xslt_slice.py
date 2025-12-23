from lxml import etree
from models import XSLTSlice

XSL_NS = "http://www.w3.org/1999/XSL/Transform"
NS = {"xsl": XSL_NS}

SAFE_BOUNDARIES = {
    f"{{{XSL_NS}}}for-each",
    f"{{{XSL_NS}}}choose",
    f"{{{XSL_NS}}}if",
    f"{{{XSL_NS}}}template",
}

def find_slice(xslt_tree, cluster, specs):
    target_name = cluster[0].xpath.split("/")[-1].split("[")[0]

    for el in xslt_tree.iter():
        if not el.tag.startswith("{") and el.tag == target_name:
            boundary = expand_to_boundary(el)
            if boundary is not None:
                return XSLTSlice(boundary, cluster, specs)

    for el in xslt_tree.xpath("//xsl:element", namespaces=NS):
        if el.get("name") == target_name:
            boundary = expand_to_boundary(el)
            if boundary is not None:
                return XSLTSlice(boundary, cluster, specs)

    return None

def expand_to_boundary(node):
    cur = node
    while cur is not None:
        if cur.tag in SAFE_BOUNDARIES:
            return cur
        cur = cur.getparent()
    return None
