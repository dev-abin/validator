from state import FixState
from xslt_runner import run_xslt
from xml_diff import diff_xml
from spec_matcher import match_specs
from xslt_slicer import (
    find_producing_nodes,
    expand_to_safe_boundary,
    extract_slice
)
from llm_fix import llm_fix_slice
from merger import merge_slice
from termination import check_termination
from lxml import etree


def fix_xslt(xslt, input_xml, target_xml, specs, max_iters=10):
    state = FixState(xslt, input_xml, target_xml, specs)

    for _ in range(max_iters):
        state.output_xml = run_xslt(state.xslt, state.input_xml)
        state.diffs = diff_xml(state.output_xml, state.target_xml)

        if not state.diffs:
            state.status = "DONE"
            break

        for d in state.diffs:
            matched = match_specs(d["xpath"], specs)
            if matched:
                state.current_diff = d
                state.relevant_specs = matched
                break

        if not state.current_diff:
            state.status = "FAILED"
            break

        local_name = state.current_diff["xpath"].split("/")[-1].split("[")[0]

        xslt_tree = etree.XML(state.xslt.encode())
        nodes = find_producing_nodes(xslt_tree, local_name)

        if not nodes:
            state.status = "FAILED"
            break

        boundary = expand_to_safe_boundary(nodes[0])
        if not boundary:
            state.status = "FAILED"
            break

        frag, line_range = extract_slice(xslt_tree, boundary)

        fixed = llm_fix_slice(frag, state.relevant_specs)
        new_xslt = merge_slice(state.xslt, line_range, fixed)

        new_output = run_xslt(new_xslt, state.input_xml)
        new_diffs = diff_xml(new_output, state.target_xml)

        decision = check_termination(state.diffs, new_diffs)
        if decision != "CONTINUE":
            state.status = decision
            break

        state.xslt = new_xslt

    return state
