import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def call_llm(
    user_prompt: str,
    system_prompt: str,
    temperature: float = 0.1,
    max_tokens: int = 400
) -> str:
    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=max_tokens,
        temperature=temperature,
        system=system_prompt,
        messages=[
            {"role": "user", "content": user_prompt}
        ]
    )
    return message.content[0].text
