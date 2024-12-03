import requests
from config import API_KEY, BASE_URL


class SemanticScholarClient:
    def __init__(self):
        self.headers = {"x-api-key": API_KEY}

    def get_papers(self, query, limit=100):
        endpoint = f"{BASE_URL}/paper/search"
        params = {
            "query": query,
            "limit": limit
        }

        response = requests.get(
            endpoint,
            headers=self.headers,
            params=params
        )

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API request failed with status {response.status_code}")
