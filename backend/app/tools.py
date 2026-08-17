"""Tools the model can call to return structured data alongside its prose reply.
"""

PROPOSE_REPLIES = {
    "name": "propose_replies",
    "description": (
        "Propose 2-4 short candidate replies the user might send next, phrased "
        "in their first-person voice (e.g., 'I want something instrumental'). "
        "Call this whenever you ask a clarifying question. Skip it when you're "
        "giving a final recommendation — the user will react in their own words."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "replies": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 2,
                "maxItems": 4,
                "description": "Short first-person replies, ideally under ~8 words.",
            },
        },
        "required": ["replies"],
    },
}

ALL_TOOLS = [PROPOSE_REPLIES]