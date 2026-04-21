import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class KnowledgeBaseValidationError(Exception):
    """Raised when knowledge base structure or content is invalid."""
    pass


def validate_knowledge_base(data: dict[str, Any]) -> None:
    """
    Validate the structure and content of the knowledge base.
    
    Args:
        data: Parsed knowledge base JSON
        
    Raises:
        KnowledgeBaseValidationError: If validation fails
    """
    # Validate top-level structure
    required_sections = ["pricing", "policies", "product"]
    for section in required_sections:
        if section not in data:
            raise KnowledgeBaseValidationError(
                f"Missing required section: {section}"
            )
    
    # Validate pricing section
    pricing = data["pricing"]
    if not isinstance(pricing, dict):
        raise KnowledgeBaseValidationError("'pricing' must be a dictionary")
    
    required_plans = ["basic", "pro"]
    for plan in required_plans:
        if plan not in pricing:
            raise KnowledgeBaseValidationError(
                f"Missing required pricing plan: {plan}"
            )
        
        plan_data = pricing[plan]
        if not isinstance(plan_data, dict):
            raise KnowledgeBaseValidationError(
                f"Pricing plan '{plan}' must be a dictionary"
            )
        
        if "price" not in plan_data:
            raise KnowledgeBaseValidationError(
                f"Pricing plan '{plan}' missing 'price' field"
            )
        
        if "features" not in plan_data:
            raise KnowledgeBaseValidationError(
                f"Pricing plan '{plan}' missing 'features' field"
            )
        
        if not isinstance(plan_data["features"], list):
            raise KnowledgeBaseValidationError(
                f"Pricing plan '{plan}' features must be a list"
            )
        
        if len(plan_data["features"]) == 0:
            raise KnowledgeBaseValidationError(
                f"Pricing plan '{plan}' must have at least one feature"
            )
    
    # Validate policies section
    policies = data["policies"]
    if not isinstance(policies, dict):
        raise KnowledgeBaseValidationError("'policies' must be a dictionary")
    
    required_policies = ["refund", "support", "trial"]
    for policy in required_policies:
        if policy not in policies:
            raise KnowledgeBaseValidationError(
                f"Missing required policy: {policy}"
            )
        
        if not isinstance(policies[policy], str) or not policies[policy].strip():
            raise KnowledgeBaseValidationError(
                f"Policy '{policy}' must be a non-empty string"
            )
    
    # Validate product section
    product = data["product"]
    if not isinstance(product, dict):
        raise KnowledgeBaseValidationError("'product' must be a dictionary")
    
    required_product_fields = ["name", "description", "use_cases"]
    for field in required_product_fields:
        if field not in product:
            raise KnowledgeBaseValidationError(
                f"Product section missing required field: {field}"
            )
    
    if not isinstance(product["use_cases"], list):
        raise KnowledgeBaseValidationError(
            "Product 'use_cases' must be a list"
        )
    
    if len(product["use_cases"]) == 0:
        raise KnowledgeBaseValidationError(
            "Product must have at least one use case"
        )
    
    logger.info("Knowledge base validation passed")


def load_knowledge_base() -> list[str]:
    """
    Load the AutoStream knowledge base from JSON and split it into
    semantically meaningful chunks suitable for embedding and vector retrieval.
    
    Each chunk is designed to be self-contained and optimized for semantic search:
    - Pricing chunks include plan name, price, and all features
    - Policy chunks include policy type and full policy text
    - Product chunks include product description and use cases
    
    Returns:
        List of text chunks (one per pricing plan, policy, or product fact)
        
    Raises:
        FileNotFoundError: If knowledge.json is not found
        json.JSONDecodeError: If knowledge.json is not valid JSON
        KnowledgeBaseValidationError: If knowledge base structure is invalid
    """
    data_path = Path(__file__).parent.parent / "data" / "knowledge.json"
    
    logger.info(f"Loading knowledge base from {data_path}")
    
    try:
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        logger.error(f"Knowledge base file not found: {data_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in knowledge base: {e}")
        raise
    
    # Validate structure and content
    validate_knowledge_base(data)
    
    chunks: list[str] = []

    # ── Pricing chunks ──────────────────────────────────────────────
    # Create semantically rich chunks that include context for better retrieval
    for plan_name, plan_data in data["pricing"].items():
        features_str = "\n  - " + "\n  - ".join(plan_data["features"])
        chunk = (
            f"AutoStream {plan_name.capitalize()} Plan Pricing\n"
            f"Price: {plan_data['price']}\n"
            f"Features:{features_str}\n\n"
            f"This is the {plan_name} tier subscription for AutoStream video editing platform."
        )
        chunks.append(chunk)
        logger.debug(f"Created pricing chunk for {plan_name} plan")

    # ── Policy chunks ────────────────────────────────────────────────
    # Each policy gets its own chunk for precise retrieval
    for policy_name, policy_text in data["policies"].items():
        chunk = (
            f"AutoStream {policy_name.capitalize()} Policy\n\n"
            f"{policy_text}\n\n"
            f"This policy applies to all AutoStream customers."
        )
        chunks.append(chunk)
        logger.debug(f"Created policy chunk for {policy_name}")

    # ── Product / general info chunk ─────────────────────────────────
    # Comprehensive product overview for general queries
    product = data.get("product", {})
    if product:
        use_cases_str = "\n  - " + "\n  - ".join(product.get("use_cases", []))
        chunk = (
            f"About {product.get('name', 'AutoStream')}\n\n"
            f"{product.get('description', '')}\n\n"
            f"Key use cases and features:{use_cases_str}\n\n"
            f"AutoStream helps content creators edit videos faster using AI technology."
        )
        chunks.append(chunk)
        logger.debug("Created product overview chunk")
    
    logger.info(f"Successfully loaded {len(chunks)} knowledge base chunks")
    return chunks
