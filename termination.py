def check_termination(prev_diffs, new_diffs):
    if not new_diffs:
        return "DONE"
    if len(new_diffs) >= len(prev_diffs):
        return "FAILED"
    return "CONTINUE"
