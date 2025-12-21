from langgraph.graph import StateGraph
from state import AgentState
import nodes


def build_graph():
    g = StateGraph(AgentState)

    g.add_node("ANALYZE", nodes.transform_and_analyze)
    g.add_node("CLUSTER", nodes.classify_and_cluster)
    g.add_node("SELECT", nodes.select_batch_target)
    g.add_node("ORDER", nodes.prioritize_batch)
    g.add_node("HARNESS", nodes.create_harness)
    g.add_node("LLM", nodes.llm_batch_fix)
    g.add_node("VERIFY", nodes.verify_harness)
    g.add_node("APPLY", nodes.apply_and_lock)
    g.add_node("CHECK", nodes.check_termination)

    g.set_entry_point("ANALYZE")

    g.add_edges([
        ("ANALYZE", "CLUSTER"),
        ("CLUSTER", "SELECT"),
        ("SELECT", "ORDER"),
        ("ORDER", "HARNESS"),
        ("HARNESS", "LLM"),
        ("LLM", "VERIFY"),
        ("VERIFY", "APPLY"),
        ("APPLY", "CHECK"),
        ("CHECK", "ANALYZE")
    ])

    return g.compile()
