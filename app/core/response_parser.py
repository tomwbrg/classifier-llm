import re
import json
import yaml
from app.data.models import Classification

CONFIDENCE_THRESHOLD = 0.65


def load_categories():
    return yaml.safe_load(open("config/categories.yaml"))["categories"]


def get_category_name(categories: list, cat_id: str) -> str:
    cat = next((c for c in categories if c["id"] == cat_id), None)
    return cat["name"] if cat else cat_id


def get_category_description(categories: list, cat_id: str) -> str:
    cat = next((c for c in categories if c["id"] == cat_id), None)
    return cat["description"] if cat else ""


def parse_response(raw: str, input_text: str) -> Classification:
    categories = load_categories()
    valid_ids = [c["id"] for c in categories]

    try:
        json_match = re.search(r'\{.*\}', raw, re.DOTALL)
        if not json_match:
            raise ValueError("Aucun JSON trouvé dans la réponse")

        data = json.loads(json_match.group())

        # Validation
        if data.get("category_id") not in valid_ids:
            raise ValueError(f"Catégorie invalide : {data.get('category_id')}")
        if not (0.0 <= float(data.get("confidence", 0)) <= 1.0):
            raise ValueError("Confidence hors bornes")

        confidence = float(data["confidence"])
        alt = data.get("alternative_category")
        alt_name = get_category_name(categories, alt) if alt and alt in valid_ids else None

        return Classification(
            text=input_text,
            category_id=data["category_id"],
            category_name=get_category_name(categories, data["category_id"]),
            confidence=confidence,
            reasoning=data.get("reasoning", ""),
            key_factors=data.get("key_factors", []),
            alternative_category=alt if alt in valid_ids else None,
            alternative_category_name=alt_name,
            needs_review=confidence < CONFIDENCE_THRESHOLD
        )

    except Exception as e:
        # Fallback : catégorie inconnue, needs_review forcé
        return Classification(
            text=input_text,
            category_id="unknown",
            category_name="Non classifié",
            confidence=0.0,
            reasoning=f"Erreur de parsing : {str(e)}",
            key_factors=[],
            needs_review=True
        )

