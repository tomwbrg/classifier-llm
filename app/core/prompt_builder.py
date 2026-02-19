import yaml
import json


def load_config():
    categories = yaml.safe_load(open("config/categories.yaml"))["categories"]
    examples = json.load(open("config/examples.json"))["examples"]
    return categories, examples


def get_category_by_id(categories: list, cat_id: str) -> dict:
    return next((c for c in categories if c["id"] == cat_id), None)


def select_few_shots(examples: list, max_per_category: int = 2) -> list:
    selected = {}
    for ex in sorted(examples, key=lambda x: x.get("priority", 1), reverse=True):
        cat = ex["category"]
        if cat not in selected:
            selected[cat] = []
        if len(selected[cat]) < max_per_category:
            selected[cat].append(ex)
    result = []
    for exs in selected.values():
        result.extend(exs)
    return result


def build_classification_prompt(text: str) -> tuple[str, str]:
    categories, examples = load_config()
    few_shots = select_few_shots(examples)

    system_prompt = """Tu es un expert en analyse de messages clients pour un service support.
Ton rôle est de classifier avec précision des messages dans des catégories sémantiquement subtiles.
Tu te concentres sur l'INTENTION réelle du client et non uniquement sur les mots utilisés.
Règles absolues :
- Tu retournes UNIQUEMENT un JSON valide, rien d'autre
- Tu raisonnes d'abord, tu classes ensuite
- Tu détectes le sarcasme et l'ironie
- Tu identifies les contraintes temporelles même implicites
- En cas de doute, tu choisis la catégorie la plus actionnable pour l'équipe support"""

    categories_block = "\n".join([
        f"- {cat['name']} ({cat['id']}) : {cat['description']}"
        for cat in categories
    ])

    examples_block = "\n\n".join([
        f"Message : \"{ex['text']}\"\nCatégorie : {ex['category']}"
        for ex in few_shots
    ])

    cat_ids = [c["id"] for c in categories]

    user_prompt = f"""## Catégories disponibles
{categories_block}

## Exemples de référence
{examples_block}

## Message à classifier
"{text}"

## Instructions
Analyse ce message en suivant ces étapes :
1. Quel est le problème ou besoin exprimé ?
2. Y a-t-il une contrainte temporelle (explicite ou implicite) ?
3. Quel est le ton émotionnel (neutre / frustré / positif / sarcastique) ?
4. Y a-t-il une intention d'amélioration ou seulement une plainte ?
5. Quelle catégorie est la plus cohérente ?

Réponds UNIQUEMENT avec ce JSON :
{{
  "category_id": "<un parmi : {', '.join(cat_ids)}>",
  "category_name": "<nom complet>",
  "confidence": <float entre 0.0 et 1.0>,
  "reasoning": "<résumé en 2 phrases max>",
  "key_factors": ["<facteur 1>", "<facteur 2>", "<facteur 3 max>"],
  "alternative_category": "<id si doute, sinon null>"
}}"""

    return system_prompt, user_prompt
