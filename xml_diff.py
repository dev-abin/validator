from lxml import etree

def diff_xml(output_xml: str, target_xml: str):
    out = etree.fromstring(output_xml.encode())
    tgt = etree.fromstring(target_xml.encode())

    diffs = []

    def walk(o, t, path):
        if o is None and t is not None:
            diffs.append({"xpath": path, "type": "MISSING"})
            return
        if o is not None and t is None:
            diffs.append({"xpath": path, "type": "EXTRA"})
            return

        if o.tag != t.tag or (o.text or "").strip() != (t.text or "").strip():
            diffs.append({"xpath": path, "type": "VALUE_OR_TAG_MISMATCH"})

        oc, tc = list(o), list(t)
        for i in range(max(len(oc), len(tc))):
            walk(
                oc[i] if i < len(oc) else None,
                tc[i] if i < len(tc) else None,
                f"{path}/{o.tag.split('}')[-1]}[{i+1}]"
            )

    walk(out, tgt, "")
    return diffs
