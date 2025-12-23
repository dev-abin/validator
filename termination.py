def should_continue(old_diffs, new_diffs, seen_clusters, current_cluster):
    if not new_diffs:
        return False, "DONE"

    if len(new_diffs) >= len(old_diffs):
        return False, "NO_PROGRESS"

    cluster_key = tuple(d.xpath for d in current_cluster)
    if cluster_key in seen_clusters:
        return False, "STUCK"

    return True, "CONTINUE"
