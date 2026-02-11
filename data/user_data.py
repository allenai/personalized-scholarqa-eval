from dataclasses import dataclass
from typing import List
from data.paper_data import Paper

@dataclass
class User:
    user_id: str
    name: str
    papers: List[Paper]

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "papers": [p.paper_id for p in self.papers]
        }

    @staticmethod
    def from_dict(data):
        return User(
            user_id=data["user_id"],
            name=data["name"],
            sources=[Paper.from_dict() for s in data["sources"]]
        )