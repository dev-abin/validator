def to_localname_xpath(xpath: str) -> str:
    """
    Converts /A/B/C → /*[local-name()='A']/*[local-name()='B']/*[local-name()='C']
    """
    if not xpath or xpath == "/":
        return xpath

    parts = [p for p in xpath.strip("/").split("/") if p]
    rewritten = "".join(
        f"/*[local-name()='{p}']" for p in parts
    )
    return rewritten
