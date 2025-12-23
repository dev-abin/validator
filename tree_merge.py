from lxml import etree

def tree_merge(xslt_tree, old_node, new_fragment_xml):
    new_node = etree.fromstring(new_fragment_xml.encode())
    parent = old_node.getparent()
    if parent is None:
        raise RuntimeError("Cannot replace root node")

    parent.replace(old_node, new_node)

    etree.XSLT(xslt_tree)  # validate
    return xslt_tree
