from lxml import etree
from xslt_runner import run_xslt
from xml_diff import diff_xml
from diff_cluster import cluster_diffs
from xslt_slice import find_slice
from llm_fix import llm_fix_slice
from tree_merge import tree_merge
from termination import should_continue

def fix_xslt(xslt_str, input_xml, target_xml, specs, max_iters=5):
    xslt_tree = etree.XML(xslt_str.encode())
    seen_clusters = set()

    for _ in range(max_iters):
        output = run_xslt(xslt_tree, input_xml)
        diffs = diff_xml(output, target_xml)

        if not diffs:
            return xslt_tree, "SUCCESS"

        clusters = cluster_diffs(diffs)
        cluster = clusters[0]

        slice_obj = find_slice(xslt_tree, cluster, specs)
        if not slice_obj:
            return xslt_tree, "FAILED_NO_SLICE"

        frag_xml = etree.tostring(slice_obj.fragment_node, encoding="unicode")
        fixed_xml = llm_fix_slice(frag_xml, cluster, specs)

        new_tree = tree_merge(xslt_tree, slice_obj.fragment_node, fixed_xml)
        new_output = run_xslt(new_tree, input_xml)
        new_diffs = diff_xml(new_output, target_xml)

        cont, status = should_continue(diffs, new_diffs, seen_clusters, cluster)
        if not cont:
            return new_tree, status

        seen_clusters.add(tuple(d.xpath for d in cluster))
        xslt_tree = new_tree

    return xslt_tree, "MAX_ITERATIONS"
