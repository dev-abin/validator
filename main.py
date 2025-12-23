from graph import build_graph
from state import AgentState
from pathlib import Path


# =========================
# I/O ADAPTERS (BORING BY DESIGN)
# =========================

def load_xslt(path: str = "data/input.xslt") -> str:
    return Path(path).read_text(encoding="utf-8")


def load_input_xml(path: str = "data/input.xml") -> str:
    return Path(path).read_text(encoding="utf-8")


def load_target_xml(path: str = "data/target.xml") -> str:
    return Path(path).read_text(encoding="utf-8")


def save_xslt(xslt: str, path: str = "data/output.xslt") -> None:
    Path(path).write_text(xslt, encoding="utf-8")


# =========================
# ENTRY POINT
# =========================

from spec_normaliser import normalize_specs
from agent import run_mv_ctr


specs = normalize_specs(read_specs())
updated = run_mv_ctr(xslt, input_xml, target_xml, specs, apply_xslt)
    
    
def main():
    graph = build_graph()

    state = AgentState(
        xslt=load_xslt(),
        input_xml=load_input_xml(),
        target_xml=load_target_xml()
    )

    final_state = graph.invoke(state)

    if final_state.phase == "DONE":
        save_xslt(final_state.xslt)
        print("XSLT stabilization completed successfully.")
    else:
        print(f"XSLT stabilization ended in phase: {final_state.phase}")


if __name__ == "__main__":
    main()
