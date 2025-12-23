from lxml import etree
from xml_utils import extract_namespaces
from xpath_utils import to_localname_xpath

def slice_target_xml(target_xml: str, output_xpath: str) -> str:
    tree = etree.XML(target_xml.encode())
    ns = extract_namespaces(target_xml)
    nodes = tree.xpath(to_localname_xpath(output_xpath))

    wrapper = etree.Element("TargetSlice")
    for n in nodes:
        wrapper.append(n)

    return etree.tostring(wrapper, pretty_print=True).decode()
