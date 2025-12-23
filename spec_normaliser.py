import re
from typing import List
from models import RawSpec, NormalizedSpec

def clean_xpath(xpath: str) -> str:
    if not xpath:
        return ""
    m = re.search(r"(/[^ \t\n\r]+)", xpath)
    return m.group(1) if m else xpath.strip()

def is_root_xpath(xpath: str) -> bool:
    return xpath in ("/", "") or xpath.count("/") <= 1

def extract_child_nodes(remarks: str) -> List[str]:
    if not remarks:
        return []
    keywords = ["contain", "contains", "include", "includes", "must have"]
    if not any(k in remarks.lower() for k in keywords):
        return []
    return list(set(re.findall(r"\b[A-Z][A-Za-z0-9_]+\b", remarks)))

def normalize_specs(raw_specs: List[RawSpec]) -> List[NormalizedSpec]:
    out = []
    counter = 1

    for raw in raw_specs:
        in_xp = clean_xpath(raw.input_xpath)
        out_xp = clean_xpath(raw.output_xpath)

        if not out_xp:
            continue

        if is_root_xpath(out_xp):
            children = extract_child_nodes(raw.remarks)
            for child in children:
                out.append(
                    NormalizedSpec(
                        spec_id=f"S{counter}",
                        input_xpath=in_xp,
                        output_xpath=f"{out_xp}/{child}".replace("//", "/"),
                        rule_type="MISSING_NODE",
                        description=f"{child} must exist under {out_xp}"
                    )
                )
                counter += 1
        else:
            out.append(
                NormalizedSpec(
                    spec_id=f"S{counter}",
                    input_xpath=in_xp,
                    output_xpath=out_xp,
                    rule_type="MISSING_NODE",
                    description=raw.remarks or "Node must exist"
                )
            )
            counter += 1

    return out
