from lxml import etree

def extract_namespaces(xml_str: str) -> dict:
    root = etree.XML(xml_str.encode())
    ns = {}
    for k, v in root.nsmap.items():
        if k is None:
            ns["ns"] = v
        else:
            ns[k] = v
    return ns
