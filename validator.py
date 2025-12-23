from lxml import etree
from xml_utils import extract_namespaces
from xpath_utils import to_localname_xpath
from models import NormalizedSpec

def validate_spec(output_xml: str, spec: NormalizedSpec) -> bool:
    tree = etree.XML(output_xml.encode())
    ns = extract_namespaces(output_xml)
    nodes = tree.xpath(to_localname_xpath(spec.output_xpath))


    if spec.rule_type == "MISSING_NODE":
        return bool(nodes)

    if spec.rule_type == "NON_EMPTY":
        return bool(nodes and nodes[0].text and nodes[0].text.strip())

    raise ValueError("Unknown rule type")
