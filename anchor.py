from lxml import etree
import uuid

XSL_NS = "http://www.w3.org/1999/XSL/Transform"
NS = {"xsl": XSL_NS}

def find_anchor(xslt_tree: etree._ElementTree, output_xpath: str) -> etree._Element:
    tag = output_xpath.strip("/").split("/")[-1]

    hits = xslt_tree.xpath(f".//*[local-name()='{tag}']")
    if hits:
        return hits[0]

    hits = xslt_tree.xpath(".//xsl:element[@name=$n]", n=tag, namespaces=NS)
    if hits:
        return hits[0]

    hits = xslt_tree.xpath(".//xsl:value-of", namespaces=NS)
    if hits:
        return hits[0]

    raise RuntimeError(f"No anchor found for {output_xpath}")

def inject_anchor_id(node: etree._Element) -> str:
    aid = f"A_{uuid.uuid4().hex[:8]}"
    node.attrib["_anchor_id"] = aid
    return aid
