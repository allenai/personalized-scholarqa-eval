from abc import ABC, abstractmethod
import json
from data import PaperSnippet, Paper
from dataclasses import dataclass
from typing import List

# Abstract base class for implementing LLMs
class LLM(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def generate_text(self, prompt: str) -> str:
        """Generate text from a prompt"""
        pass

    def validate_json_structure(self, sample: dict, target: dict) -> bool:
        """Recursively check if target JSON matches the structure of the sample JSON."""
        for key, val in sample.items():
            if key not in target:
                return False
            if isinstance(val, dict):
                if not isinstance(target[key], dict):
                    return False
                if not self.validate_json_structure(val, target[key]):
                    return False
            elif isinstance(val, list):
                if not isinstance(target[key], list):
                    return False
                if val and isinstance(val[0], dict):
                    for item in target[key]:
                        if not self.validate_json_structure(val[0], item):
                            return False
            else:
                if not isinstance(target[key], type(val)):
                    return False
        return True

    def generate_json(self, prompt: str, target_json: dict, backup_json: dict = dict(), num_tries=0) -> dict | None:
        if num_tries == 10:
            return None
        try:
            out = self.generate_text(prompt=prompt)
            self.out = out
            out = out[out.index("{"):out.rindex("}")+1]
            json_data = json.loads(out)
            if self.validate_json_structure(sample=target_json, target=json_data) or self.validate_json_structure(sample=backup_json, target=json_data):
                return json_data

            print(f"Failed to adhere to JSON on attempt {num_tries+1}/{10}:")
            # print(json_data)
            # print(target_json)
            return self.generate_json(prompt=prompt, target_json=target_json, num_tries=num_tries+1)
        except Exception as e:
            print(f"Failed to parse JSON on attempt {num_tries+1}/{10}:", e)
            print(self.out)
            return self.generate_json(prompt=prompt, target_json=target_json, num_tries=num_tries+1)
        
# data class for retriever results
@dataclass
class RetrieverResult:
    rank: int # 0-indexed
    score: float # relevance score
    text: PaperSnippet # actual text
    text_index: int # index of where the text was found (for sorting later)

# Abstract base class for implementing Retrievers
class Retriever(ABC):

    @abstractmethod
    def index_docs(self, papers: List[Paper]):
        """Index a set of documents"""
        pass

    @abstractmethod
    def topk_each(self, query: str, k: int) -> List[RetrieverResult]:
        """Return the top-k outputs for a query within each document"""
        pass

    @abstractmethod
    def topk_all(self, query: str, k: int) -> List[RetrieverResult]:
        """Return the top-k outputs for a query across all documents"""
        pass

    def topk(self, query: str, k: int, concatenate_papers: bool):
        """Return the top-k outputs for a query either across or in documents (based on 'concatenate_papers')"""
        if concatenate_papers:
            return self.topk_all(query=query, k=k)
        else:
            return self.topk_each(query=query, k=k)
        

