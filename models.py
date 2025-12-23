from dataclasses import dataclass

@dataclass
class RawSpec:
    input_xpath: str
    output_xpath: str
    remarks: str

@dataclass
class NormalizedSpec:
    spec_id: str
    input_xpath: str
    output_xpath: str
    rule_type: str   # MISSING_NODE | NON_EMPTY
    description: str
