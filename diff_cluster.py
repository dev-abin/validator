def cluster_diffs(diffs):
    clusters = {}
    for d in diffs:
        root = "/".join(d.xpath.split("/")[:3])
        clusters.setdefault(root, []).append(d)
    return sorted(clusters.values(), key=len, reverse=True)
