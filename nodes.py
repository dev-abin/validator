import engine


def transform_and_analyze(state):
    state._raw_failures = engine.analyze_failures(state)
    return state


def classify_and_cluster(state):
    clusters, deferred = engine.cluster_failures(state._raw_failures)
    state.failure_clusters = clusters
    state.deferred_cross_cutting.extend(deferred)
    return state


def select_batch_target(state):
    state.active_job = engine.select_template_to_fix(state)
    return state


def prioritize_batch(state):
    if state.active_job:
        state.active_job["failures"] = engine.prioritize_failures(
            state.active_job["failures"]
        )
    return state


def create_harness(state):
    job = state.active_job
    if not job:
        return state

    tid = job["template_id"]
    template = engine.extract_template(state.xslt, tid)
    deps = engine.resolve_dependencies(state.xslt, template)

    job["dependencies"] = deps
    job["harness_xslt"] = engine.build_harness_xslt(template, deps)

    match_expr = tid  # assumes template_id == match
    job["input_slice"] = engine.slice_input_xml(state.input_xml, match_expr)
    job["target_slice"] = engine.slice_target_xml(
        state.target_xml,
        job["failures"][0]["xpath"]
    )

    return state


def llm_batch_fix(state):
    job = state.active_job
    if not job:
        return state

    prompt = {
        "template": job["harness_xslt"],
        "failures": job["failures"],
        "input": job["input_slice"],
        "target": job["target_slice"]
    }

    job["proposed_template"] = call_llm(prompt)
    return state


def verify_harness(state):
    job = state.active_job
    if not job:
        return state

    engine.validate_llm_output(
        job["proposed_template"],
        job["dependencies"]
    )

    apply_xslt(job["input_slice"], job["proposed_template"])
    job["verified"] = True
    return state


def apply_and_lock(state):
    job = state.active_job
    if not job or not job.get("verified"):
        return state

    state.xslt = engine.replace_template(
        state.xslt,
        job["template_id"],
        job["proposed_template"]
    )

    # re-run validation for this template
    if not job["failures"]:
        state.locked_templates.append(job["template_id"])

    return state


def check_termination(state):
    state.iteration += 1

    if not state.failure_clusters:
        state.phase = "DONE"

    if state.iteration > 100:
        state.phase = "FAILED"

    return state
