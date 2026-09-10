from pathlib import Path


POLICY_FOLDER = Path(__file__).parent / "policies"


def load_policy(filename):
    """
    Load one SACCO policy file.
    """

    path = POLICY_FOLDER / filename

    with open(path, "r", encoding="utf-8") as file:
        return file.read()


def load_all_policies():
    """
    Load all approved policies.

    For this baseline prototype we load all policies
    because there are only a few small documents.

    Later this can be replaced by RAG/vector retrieval.
    """

    policy_files = [
        "loan_policy.txt",
        "savings_policy.txt",
        "repayment_policy.txt"
    ]

    policies = []

    for filename in policy_files:
        content = load_policy(filename)

        policies.append(
            f"""
SOURCE FILE: {filename}

{content}
"""
        )

    return "\n".join(policies)