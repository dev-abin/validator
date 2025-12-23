from lxml import etree

def run_xslt(xslt_str: str, input_xml: str) -> str:
    xslt_tree = etree.XML(xslt_str.encode())
    transform = etree.XSLT(xslt_tree)
    result = transform(etree.XML(input_xml.encode()))
    return str(result)
