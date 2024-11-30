from openai import OpenAI
from typing import Dict
from config import OPENAI_API_KEY
from ollama import Client


class LLMProcessor:
    def __init__(self):
        self.client = Client(model="")

    def process_paper(self, paper: Dict) -> Dict:
        prompt = f"""
        Analyze the following research paper and provide:
        1. Main topic (one sentence)
        2. Key findings (2-3 points)
        3. Technical complexity (Low/Medium/High)

        Title: {paper['title']}
        Abstract: {paper['abstract']}
        """

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )

        analysis = response.choices[0].message.content

        paper['llm_analysis'] = analysis
        return paper
