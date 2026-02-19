import json
import re
import yaml
from app.core.llm_client import call_llm


def load_categories():
    return yaml.safe_load(open("config/categories.yaml"))["categories"]


def get_category_description(categories: list, cat_id: str) -> str:
    cat = next((c for c in categories if c["id"] == cat_id), None)
    return cat["description"] if cat else cat_id


def judge_classification(case: dict, prediction) -> dict:
    categories = load_categories()

    # Vérification directe d'abord
    if prediction.category_id == case["expected_category"]:
        return {
            "verdict": "correct",
            "severity": "none",
            "judge_reasoning": "Catégorie prédite identique à la catégorie attendue."
        }

    # Sinon on demande au LLM de juger
    prompt = f"""Tu es un évaluateur expert de systèmes de classification.

## Message évalué
"{case['text']}"

## Classification attendue
{case['expected_category']} — {get_category_description(categories, case['expected_category'])}

## Classification produite
{prediction.category_id} — {get_category_description(categories, prediction.category_id)}

## Raisonnement du système
{prediction.reasoning}

La classification produite est-elle correcte ou incorrecte ?

Réponds UNIQUEMENT avec ce JSON :
{{
  "verdict": "correct",
  "severity": "none",
  "judge_reasoning": "<explication en 1 phrase>"
}}

OU

{{
  "verdict": "incorrect",
  "severity": "minor" | "major",
  "judge_reasoning": "<explication en 1 phrase>"
}}"""

    raw = call_llm(
        prompt,
        "Tu es un évaluateur strict et précis.",
        temperature=0.0,
        max_tokens=200
    )

    try:
        json_match = re.search(r'\{.*\}', raw, re.DOTALL)
        return json.loads(json_match.group())
    except Exception:
        return {
            "verdict": "incorrect",
            "severity": "major",
            "judge_reasoning": "Erreur de parsing"
        }
