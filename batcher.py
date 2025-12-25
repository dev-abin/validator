from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Literal, Tuple
from collections import defaultdict

# =========================
# Type Definitions
# =========================

CaseType = Literal["A", "B", "C"]


@dataclass(frozen=True)
class Issue:
    """Atomic spec-backed diff."""
    case: CaseType
    output_path: str
    expected_count: Optional[int]
    observed_count: Optional[int]


@dataclass
class XSLTTemplate:
    """Found via static analysis of XSLT (future use)"""
    match: str
    output_paths: Set[str]
    line_start: int
    line_end: int
    dependencies: List[str] = field(default_factory=list)


@dataclass
class Batch:
    """Repair unit for LLM processing."""
    case: CaseType
    batch_root: str  # XPath representing the batch scope
    issues: List[Issue]
    responsible_templates: List[XSLTTemplate] = field(default_factory=list)
    estimated_tokens: int = 0
    locked: bool = False
    history: List[str] = field(default_factory=list)


# =========================
# Utility Functions
# =========================

def parent_xpath(path: str) -> Optional[str]:
    """Extract parent path from XPath-like string."""
    parts = [p for p in path.strip("/").split("/") if p]
    if len(parts) <= 1:
        return None
    return "/" + "/".join(parts[:-1])


# =========================
# Batching Functions
# =========================

def batch_case_a(issues: List[Issue]) -> List[Batch]:
    """
    Case A: Missing output (required by spec but not present).
    Strategy: Group by parent path and expected count.
    """
    by_parent_and_count: Dict[Tuple[str, Optional[int]], List[Issue]] = defaultdict(list)
    
    for issue in issues:
        parent = parent_xpath(issue.output_path) or "/"
        key = (parent, issue.expected_count)
        by_parent_and_count[key].append(issue)
    
    batches = []
    for (parent, exp), group in by_parent_and_count.items():
        batches.append(
            Batch(
                case="A",
                batch_root=parent,
                issues=group,
                history=[f"A: parent={parent}, expected={exp}"]
            )
        )
    
    return batches


def batch_case_b(issues: List[Issue]) -> List[Batch]:
    """
    Case B: Cardinality mismatch (output exists but wrong count).
    Strategy: Batch by exact output path and expected count.
    """
    grouped: Dict[Tuple[str, Optional[int]], List[Issue]] = defaultdict(list)

    for issue in issues:
        key = (issue.output_path, issue.expected_count)
        grouped[key].append(issue)

    batches = []
    for (path, expected), group in grouped.items():
        batches.append(
            Batch(
                case="B",
                batch_root=path,
                issues=group,
                history=[f"B: cardinality batch (expected={expected})"]
            )
        )

    return batches


def batch_case_c(issues: List[Issue]) -> List[Batch]:
    """
    Case C: Overgeneration (output exists but not in spec).
    Strategy: Group by parent path.
    """
    by_parent: Dict[str, List[Issue]] = defaultdict(list)
    
    for issue in issues:
        parent = parent_xpath(issue.output_path) or "/"
        by_parent[parent].append(issue)
    
    batches = []
    for parent, group in by_parent.items():
        batches.append(
            Batch(
                case="C",
                batch_root=parent,
                issues=group,
                history=[f"C: overgen parent={parent}"]
            )
        )
    
    return batches


# =========================
# Merge & Split Logic
# =========================

def adaptive_merge(batches: List[Batch], max_batch_size: int = 10) -> List[Batch]:
    """
    Merge small batches that share parent structure.
    Prevents explosion of tiny batches, especially in Case C.
    """
    merged = []
    
    # Group by parent path
    by_parent: Dict[str, List[Batch]] = defaultdict(list)
    for batch in batches:
        parent = parent_xpath(batch.batch_root) or "/"
        by_parent[parent].append(batch)
    
    for parent, group in by_parent.items():
        total_issues = sum(len(b.issues) for b in group)
        
        if total_issues <= max_batch_size and len(group) > 1:
            # Combine into one batch
            all_issues = []
            all_history = []
            all_templates = []
            
            for b in group:
                all_issues.extend(b.issues)
                all_history.extend(b.history)
                all_templates.extend(b.responsible_templates)
            
            merged.append(
                Batch(
                    case=group[0].case,
                    batch_root=parent,
                    issues=all_issues,
                    responsible_templates=all_templates,
                    history=all_history + [f"merged {len(group)} batches"]
                )
            )
        else:
            merged.extend(group)
    
    return merged


def split_batch(batch: Batch, max_size: int) -> List[Batch]:
    """Split oversized batch into smaller chunks."""
    chunks = []
    for i in range(0, len(batch.issues), max_size):
        chunk_issues = batch.issues[i:i+max_size]
        chunks.append(
            Batch(
                case=batch.case,
                batch_root=batch.batch_root,
                issues=chunk_issues,
                responsible_templates=batch.responsible_templates,
                estimated_tokens=batch.estimated_tokens,
                history=batch.history + [f"split chunk {i//max_size + 1}"]
            )
        )
    return chunks


# =========================
# Main Entry Point
# =========================

def batch_issues_adaptive(case: CaseType, issues: List[Issue]) -> List[Batch]:
    """
    Monolithic XSLT-aware batching with adaptive merging/splitting.
    
    Strategy:
    - Start conservative (fine-grained batches)
    - Merge small related batches
    - Split oversized batches for LLM context window
    """
    if not issues:
        return []
    
    # Phase 1: Initial batching by case
    if case == "C":
        batches = batch_case_c(issues)
        batches = adaptive_merge(batches, max_batch_size=10)
        
    elif case == "B":
        batches = batch_case_b(issues)
        
    elif case == "A":
        batches = batch_case_a(issues)
        batches = adaptive_merge(batches, max_batch_size=8)
    
    else:
        raise ValueError(f"Unknown case type: {case}")
    
    # Phase 2: Split oversized batches
    final_batches = []
    MAX_ISSUES_PER_BATCH = 20  # Tune based on LLM context window
    
    for batch in batches:
        if len(batch.issues) > MAX_ISSUES_PER_BATCH:
            sub_batches = split_batch(batch, MAX_ISSUES_PER_BATCH)
            final_batches.extend(sub_batches)
        else:
            final_batches.append(batch)
    
    return final_batches


# =========================
# Example Usage
# =========================

if __name__ == "__main__":
    # Case A: Missing elements
    issues_a = [
        Issue("A", "/Order/Item[1]/Price", 1, 0),
        Issue("A", "/Order/Item[1]/Tax", 1, 0),
        Issue("A", "/Order/Item[2]/Price", 1, 0),
    ]
    
    # Case B: Wrong cardinality
    issues_b = [
        Issue("B", "/Order/Item/Fee", 2, 1),
        Issue("B", "/Order/Item/Fee", 2, 3),
    ]
    
    # Case C: Overgeneration
    issues_c = [
        Issue("C", "/Order/Debug/Message", None, 1),
        Issue("C", "/Order/Debug/Timestamp", None, 1),
        Issue("C", "/flyingItem/InternalNote", None, 1),
    ]
    
    print("=" * 60)
    print("BATCHING RESULTS")
    print("=" * 60)
    
    for case, issues in [("A", issues_a), ("B", issues_b), ("C", issues_c)]:
        batches = batch_issues_adaptive(case, issues)
        print(f"\nCase {case}: {len(issues)} issues → {len(batches)} batches")
        for i, batch in enumerate(batches, 1):
            print(f"  Batch {i}:")
            print(f"    Root: {batch.batch_root}")
            print(f"    Issues: {len(batch.issues)}")
            print(f"    History: {batch.history}")