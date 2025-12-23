from dataclasses import dataclass
from typing import List, Optional
from lxml import etree

@dataclass
class Diff:
    xpath: str
    diff_type: str  # MISSING, EXTRA, VALUE_MISMATCH

@dataclass
class XSLTSlice:
    fragment_node: etree._Element
    relevant_diffs: List[Diff]
    relevant_specs: List[dict]
