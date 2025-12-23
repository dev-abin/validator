import openai

SYSTEM_PROMPT = """
You are editing XSLT.
Rules:
- Modify ONLY the node with the given _anchor_id
- Do NOT add loops
- Do NOT widen XPath
- Return ONLY the modified node XML
"""

def call_llm(xslt_slice, spec_desc, anchor_id, input_slice, target_slice):
    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"""
SPEC:
{spec_desc}

ANCHOR_ID:
{anchor_id}

INPUT XML:
{input_slice}

TARGET XML:
{target_slice}

XSLT SLICE:
{xslt_slice}
"""}
        ]
    )
    return resp.choices[0].message.content.strip()
