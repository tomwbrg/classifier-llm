from app.core.llm_client import call_llm
from app.core.prompt_builder import build_classification_prompt
from app.core.response_parser import parse_response
from app.data.models import Classification

MAX_RETRIES = 2


def classify(text: str) -> Classification:
    system_prompt, user_prompt = build_classification_prompt(text)

    for attempt in range(MAX_RETRIES):
        temperature = 0.1 if attempt == 0 else 0.0
        raw = call_llm(
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=400
        )
        result = parse_response(raw, text)

        if result.category_id != "unknown":
            return result

    # Après MAX_RETRIES échecs → retourner le dernier résultat (unknown)
    return result
