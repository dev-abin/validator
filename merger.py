from lxml import etree

def merge_slice(original_xslt, line_range, new_fragment):
    lines = original_xslt.splitlines()
    start, end = line_range

    merged = (
        lines[:start]
        + new_fragment.splitlines()
        + lines[end:]
    )

    merged_str = "\n".join(merged)

    etree.XML(merged_str.encode())
    etree.XSLT(etree.XML(merged_str.encode()))

    return merged_str
