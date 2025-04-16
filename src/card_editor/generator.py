from pathlib import Path

import openai

from config import OPENAI_API_KEY, OPENAI_MODEL


class CardEditor:
    def __init__(self):
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
        self.prompt_template = self._load_prompt_template()

    def _load_prompt_template(self) -> str:
        template_path = Path(__file__).parent / "prompt_template.txt"
        with open(file=template_path, encoding="utf-8") as file:
            return file.read()

    def edit(self, category: str, question: str, answer: str) -> str:
        prompt = self.prompt_template.format(
            category=category, question=question, answer=answer
        )

        response = self.client.responses.create(
            model=OPENAI_MODEL,
            input=prompt,
            temperature=0.5,
            top_p=1.0,
            max_tokens=512,
        )

        return response.output_text.strip()
