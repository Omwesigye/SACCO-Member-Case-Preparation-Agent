FORBIDDEN_PHRASES = [
    "loan is approved",
    "loan has been approved",
    "approve this loan",
    "recommend approval",
    "recommend approving",
    "loan is declined",
    "loan has been declined",
    "recommend rejection",
    "recommend rejecting",
    "disburse the loan"
]


def validate_ai_response(response):
    """
    Basic safety validation.

    Returns a list of detected problems.
    """

    problems = []

    response_lower = response.lower()

    for phrase in FORBIDDEN_PHRASES:

        if phrase in response_lower:

            problems.append(
                f"Potential decision-boundary violation: '{phrase}'"
            )

    return problems


def response_is_safe(response):
    """
    Returns True when no simple violations are detected.
    """

    return len(validate_ai_response(response)) == 0