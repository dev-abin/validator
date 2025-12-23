from lxml import etree
from validator import validate_spec
from anchor import find_anchor, inject_anchor_id
from slicer import slice_xslt
from input_slicer import slice_input_xml
from target_slicer import slice_target_xml
from patcher import patch_xslt
from llm import call_llm

def run_mv_ctr(xslt, input_xml, target_xml, specs, apply_xslt):
    xslt_tree = etree.ElementTree(etree.XML(xslt.encode()))

    for spec in specs:
        output = apply_xslt(xslt, input_xml)
        if validate_spec(output, spec):
            continue

        anchor = find_anchor(xslt_tree, spec.output_xpath)
        aid = inject_anchor_id(anchor)

        xslt_slice = etree.tostring(slice_xslt(anchor)).decode()
        input_slice = slice_input_xml(input_xml, spec.input_xpath)
        target_slice = slice_target_xml(target_xml, spec.output_xpath)

        new_anchor = call_llm(xslt_slice, spec.description, aid, input_slice, target_slice)
        patch_xslt(xslt_tree, aid, new_anchor)

        xslt = etree.tostring(xslt_tree).decode()
        if not validate_spec(apply_xslt(xslt, input_xml), spec):
            raise RuntimeError(f"Spec {spec.spec_id} failed")

    return xslt
