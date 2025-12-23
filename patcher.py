from lxml import etree

def patch_xslt(xslt_tree: etree._ElementTree, anchor_id: str, new_anchor_xml: str):
    new_node = etree.fromstring(new_anchor_xml.encode())
    old = xslt_tree.xpath(f".//*[@_anchor_id='{anchor_id}']")[0]
    old.getparent().replace(old, new_node)
