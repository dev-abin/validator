def match_specs(diff_xpath, specs):
    return [
        s for s in specs
        if diff_xpath.startswith(s["output_xpath"])
    ]
