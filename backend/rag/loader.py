import json
from pathlib import Path


def load_knowledge_base() -> list[str]:
    """
    Load the AutoStream knowledge base from JSON and split it into
    text chunks suitable for embedding and vector retrieval.

    Returns:
        List of text chunks (one per pricing plan, policy, or product fact)
    """
    data_path = Path(__file__).parent.parent / "data" / "knowledge.json"

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    chunks: list[str] = []

    # ── Pricing chunks ──────────────────────────────────────────────
    for plan_name, plan_data in data["pricing"].items():
        features_str = "\n  - " + "\n  - ".join(plan_data["features"])
        chunk = (
            f"AutoStream {plan_name.capitalize()} Plan\n"
            f"Price: {plan_data['price']}\n"
            f"Features:{features_str}"
        )
        chunks.append(chunk)

    # ── Policy chunks ────────────────────────────────────────────────
    for policy_name, policy_text in data["policies"].items():
        chunk = f"AutoStream {policy_name.capitalize()} Policy: {policy_text}"
        chunks.append(chunk)

    # ── Product / general info chunk ─────────────────────────────────
    product = data.get("product", {})
    if product:
        use_cases_str = "\n  - " + "\n  - ".join(product.get("use_cases", []))
        chunk = (
            f"About AutoStream\n"
            f"{product.get('description', '')}\n"
            f"Key use cases:{use_cases_str}"
        )
        chunks.append(chunk)

    return chunks
