from lxml import etree
from xml_utils import extract_namespaces
from xpath_utils import to_localname_xpath

MAX_SAMPLES = 3
MAX_CHARS = 5000
MAX_DEPTH = 2

def parent_xpath(xpath: str) -> str:
    parts = xpath.rstrip("/").split("/")
    return "/".join(parts[:-1]) if len(parts) > 2 else xpath

def prune_depth(elem: etree._Element, max_depth: int, current=0):
    if current >= max_depth:
        elem.clear()
        elem.text = None
        return
    for child in list(elem):
        prune_depth(child, max_depth, current + 1)

def slice_input_xml(input_xml: str, input_xpath: str) -> str:
    tree = etree.XML(input_xml.encode())
    ns = extract_namespaces(input_xml)

    root_xpath = parent_xpath(input_xpath)

    try:
        nodes = tree.xpath(to_localname_xpath(input_xpath))
    except Exception:
        return "<InputSlice/>"

    nodes = nodes[:MAX_SAMPLES]

    wrapper = etree.Element("InputSlice")

    for node in nodes:
        clone = etree.fromstring(etree.tostring(node))
        prune_depth(clone, MAX_DEPTH)
        wrapper.append(clone)

    xml_str = etree.tostring(wrapper, pretty_print=True).decode()

    # Hard size guard
    if len(xml_str) > MAX_CHARS:
        # fallback: keep only tag names, drop children
        wrapper = etree.Element("InputSlice")
        for node in nodes:
            shallow = etree.Element(node.tag)
            wrapper.append(shallow)
        xml_str = etree.tostring(wrapper).decode()

    return xml_str
