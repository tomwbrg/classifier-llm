import json
import yaml
from app.core.llm_client import call_llm


def load_categories():
    return yaml.safe_load(open("config/categories.yaml"))["categories"]


def get_confusable(categories: list, cat_id: str) -> str:
    cat = next((c for c in categories if c["id"] == cat_id), None)
    return cat.get("confusable_with", "") if cat else ""


def generate_test_cases(category: dict, confusable: str, n: int = 10) -> list:
    prompt = f"""Génère {n} messages clients RÉALISTES pour la catégorie "{category['name']}".
Définition : {category['description']}

Répartis les exemples ainsi :
- 25% faciles (signal très clair)
- 50% moyens (signal modéré)
- 25% difficiles (ressemble à "{confusable}" mais est bien "{category['name']}")

Réponds UNIQUEMENT avec ce JSON :
{{
  "test_cases": [
    {{
      "text": "<message client réaliste>",
      "difficulty": "easy|medium|hard",
      "hint": "<signal linguistique clé attendu>"
    }}
  ]
}}"""

    raw = call_llm(
        prompt,
        "Tu es un expert en génération de données de test pour classification.",
        temperature=0.7,
        max_tokens=1500
    )

    try:
        import re
        json_match = re.search(r'\{.*\}', raw, re.DOTALL)
        data = json.loads(json_match.group())
        cases = data.get("test_cases", [])
        for case in cases:
            case["expected_category"] = category["id"]
        return cases
    except Exception:
        return []


def generate_all_test_cases(n_per_category: int = 10) -> list:
    categories = load_categories()
    all_cases = []

    for category in categories:
        confusable = get_confusable(categories, category["id"])
        cases = generate_test_cases(category, confusable, n_per_category)
        all_cases.extend(cases)

    return all_cases
