from openai import OpenAI
from typing import Dict
from config import OPENAI_API_KEY
from ollama import Client
from llmclient import LLMModel

class LLMProcessor:
    def __init__(self, model):
        self.model = LLMModel(model_name=model)

    def process_paper(self, paper: Dict) -> Dict:
        prompt = f"""
        Analyze the following research paper and provide:
        1. Main topic (one sentence)
        2. Key findings (2-3 points)
        3. Technical complexity (Low/Medium/High)

        Title: {paper['title']}
        Abstract: {paper['abstract']}
        """

        response = self.model.generate(prompt)

        analysis = response

        paper['llm_analysis'] = analysis
        return paper
