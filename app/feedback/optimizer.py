import json
from datetime import datetime
from app.data.database import get_unused_wrong_feedbacks, mark_feedbacks_used
from app.core.llm_client import call_llm


def load_examples():
    return json.load(open("config/examples.json"))


def save_examples(data: dict):
    with open("config/examples.json", "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def select_best_example(cat_id: str, candidates: list) -> dict:
    if len(candidates) == 1:
        return candidates[0]

    candidates_text = "\n".join([
        f"{i}. \"{c['text']}\""
        for i, c in enumerate(candidates)
    ])

    prompt = f"""Parmi ces messages clients, tous de catégorie "{cat_id}", 
lequel est le plus utile comme exemple d'apprentissage ?
Critères : représentatif, signal clair, cas non trivial.

{candidates_text}

Réponds UNIQUEMENT avec le chiffre (0, 1, 2...) du meilleur exemple."""

    raw = call_llm(prompt, "Tu es un expert en sélection d'exemples d'apprentissage.", temperature=0.0)

    try:
        index = int(raw.strip()[0])
        return candidates[index] if index < len(candidates) else candidates[0]
    except Exception:
        return candidates[0]


def run_optimizer() -> dict | None:
    feedbacks = get_unused_wrong_feedbacks()

    if len(feedbacks) < 2:
        return None

    # Grouper par catégorie correcte
    by_category = {}
    for fb in feedbacks:
        cat = fb["correct_label"]
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(fb)

    # Sélectionner le meilleur exemple par catégorie
    new_examples = []
    for cat_id, candidates in by_category.items():
        if len(candidates) >= 1:
            best = select_best_example(cat_id, candidates)
            new_examples.append({
                "text": best["text"],
                "category": cat_id,
                "source": "feedback",
                "priority": 2,
                "added_at": datetime.now().isoformat()
            })

    if not new_examples:
        return None

    # Fusionner avec examples.json existant (max 2 par catégorie)
    data = load_examples()
    existing = data["examples"]

    for new_ex in new_examples:
        cat = new_ex["category"]
        # Retirer les anciens exemples feedback de cette catégorie si déjà 2
        cat_examples = [e for e in existing if e["category"] == cat]
        feedback_examples = [e for e in cat_examples if e.get("source") == "feedback"]

        if len(cat_examples) >= 2 and feedback_examples:
            existing.remove(feedback_examples[0])

        existing.append(new_ex)

    data["examples"] = existing
    data["version"] = data.get("version", 1) + 1
    data["last_updated"] = datetime.now().strftime("%Y-%m-%d")

    if "changelog" not in data:
        data["changelog"] = []
    data["changelog"].append({
        "version": data["version"],
        "date": data["last_updated"],
        "changes": f"Ajout de {len(new_examples)} exemple(s) depuis feedback",
        "feedbacks_used": len(feedbacks)
    })

    save_examples(data)
    mark_feedbacks_used([fb["id"] for fb in feedbacks])

    return data
