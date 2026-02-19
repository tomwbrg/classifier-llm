from app.evaluation.generator import generate_all_test_cases
from app.evaluation.judge import judge_classification
from app.core.classifier import classify


def run_evaluation(n_per_category: int = 10) -> dict:
    test_cases = generate_all_test_cases(n_per_category)
    results = []

    for case in test_cases:
        prediction = classify(case["text"])
        judgment = judge_classification(case, prediction)

        results.append({
            "text": case["text"],
            "expected": case["expected_category"],
            "predicted": prediction.category_id,
            "confidence": prediction.confidence,
            "difficulty": case.get("difficulty", "medium"),
            "verdict": judgment["verdict"],
            "severity": judgment["severity"],
            "judge_reasoning": judgment["judge_reasoning"]
        })

    return build_report(results)


def build_report(results: list) -> dict:
    total = len(results)
    if total == 0:
        return {}

    correct = sum(1 for r in results if r["verdict"] == "correct")
    hard = [r for r in results if r["difficulty"] == "hard"]
    hard_correct = sum(1 for r in hard if r["verdict"] == "correct")

    by_category = {}
    for cat_id in set(r["expected"] for r in results):
        cat_results = [r for r in results if r["expected"] == cat_id]
        cat_correct = sum(1 for r in cat_results if r["verdict"] == "correct")
        by_category[cat_id] = {
            "accuracy": cat_correct / len(cat_results) if cat_results else 0,
            "total": len(cat_results)
        }

    failed = [r for r in results if r["verdict"] == "incorrect"]

    return {
        "strict_accuracy": correct / total,
        "hard_accuracy": hard_correct / len(hard) if hard else 0,
        "total_cases": total,
        "by_category": by_category,
        "failed_cases": failed,
        "all_results": results
    }
