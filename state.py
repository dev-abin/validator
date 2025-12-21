from typing import Dict, List, Any
from dataclasses import dataclass, field


@dataclass
class AgentState:
    iteration: int = 0
    phase: str = "LOCAL_STABILIZATION"

    xslt: str = ""
    input_xml: str = ""
    target_xml: str = ""

    failure_clusters: Dict[str, List[dict]] = field(default_factory=dict)
    locked_templates: List[str] = field(default_factory=list)
    deferred_cross_cutting: List[dict] = field(default_factory=list)

    active_job: Dict[str, Any] = field(default_factory=dict)

    context_budget: Dict[str, int] = field(default_factory=lambda: {
        "max_xslt_lines": 200,
        "max_xml_lines": 80,
        "max_spec_rules": 3
    })
