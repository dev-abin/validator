from lxml import etree

XSL_NS = "http://www.w3.org/1999/XSL/Transform"

MAX_NODES = 200
MAX_DEPTH = 5
MAX_CHARS = 6000

CONTROL_TAGS = (
    "template",
    "for-each",
    "if",
    "choose",
    "when",
    "otherwise",
)

def is_control(elem):
    return elem.tag.endswith(CONTROL_TAGS)

def prune_depth(elem, max_depth, current=0):
    if current >= max_depth:
        elem.clear()
        elem.text = None
        return
    for child in list(elem):
        prune_depth(child, max_depth, current + 1)

def count_nodes(elem):
    return sum(1 for _ in elem.iter())

def stub_non_anchor(elem):
    elem.clear()
    elem.tag = f"{{{XSL_NS}}}comment"
    elem.text = "STUBBED"

def slice_xslt(anchor: etree._Element) -> etree._ElementTree:
    # Step 1: climb to nearest safe control root
    root = anchor
    while root.getparent() is not None:
        p = root.getparent()
        if is_control(p):
            root = p
            break
        root = p

    # Clone subtree
    clone = etree.fromstring(etree.tostring(root))

    # Step 2: prune depth aggressively
    prune_depth(clone, MAX_DEPTH)

    # Step 3: stub non-anchor branches
    for el in clone.iter():
        if "_anchor_id" in el.attrib:
            continue
        if is_control(el):
            continue
        stub_non_anchor(el)

    # Step 4: enforce node count budget
    if count_nodes(clone) > MAX_NODES:
        # fallback: keep only anchor node and its parents
        anchor_copy = clone.xpath(".//*[@_anchor_id]")
        if anchor_copy:
            minimal = anchor_copy[0]
            parent = minimal.getparent()
            while parent is not None:
                for sib in list(parent):
                    if sib is not minimal:
                        stub_non_anchor(sib)
                minimal = parent
                parent = parent.getparent()
            clone = minimal

    # Step 5: enforce serialized size budget
    xml_str = etree.tostring(clone).decode()
    if len(xml_str) > MAX_CHARS:
        # final fallback: anchor-only slice
        anchor_only = clone.xpath(".//*[@_anchor_id]")
        if anchor_only:
            clone = anchor_only[0]

    return etree.ElementTree(clone)
