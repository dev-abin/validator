# MV-CTR — Minimal Viable Contract-Trace-Reduce

A deterministic system for fixing legacy XSLT using specifications as contracts.

## Guarantees
- No full XML or XSLT sent to LLM
- Anchor-based DOM patching
- Root-safe spec normalization
- Namespace-safe XPath
- Monotonic convergence

## Pipeline
Raw Specs → Normalized Specs → Anchor Fix → Full Revalidation

## Requirements
- Python 3.9+
- lxml
- OpenAI API key

## Limitations
- No aggregation fixes
- No caching or parallelism
- No dynamic element inference
