from ai.model import ask_qwen

def detect_level(article: str):

    prompt = f"""
    Estimate CEFR level of this Finnish text.

    Return:

    Level: A2/B1/B2/C1

    Text:
    {article}
    """

    return ask_qwen(prompt)