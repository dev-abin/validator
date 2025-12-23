class FixState:
    def __init__(self, xslt, input_xml, target_xml, specs):
        self.xslt = xslt
        self.input_xml = input_xml
        self.target_xml = target_xml
        self.specs = specs

        self.output_xml = None
        self.diffs = []

        self.current_diff = None
        self.relevant_specs = []

        self.slice_fragment = None
        self.slice_line_range = None

        self.proposed_fix = None
        self.status = "CONTINUE"
