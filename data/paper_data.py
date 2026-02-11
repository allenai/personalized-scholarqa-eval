from enums import PaperField, PaperVenue
from typing import List
from dataclasses import dataclass
import json
import os

@dataclass
class PaperSnippet:
    idx: int
    text: str
    source_paper: "Paper"

    def to_dict(self):
        return {
            "idx": self.idx,
            "text": self.text,
            "source_paper_file_path": self.source_paper.file_path
        }

    @staticmethod
    def from_dict(data, source_paper=None):
        if not source_paper:
            paper_data = data["source_paper_file_path"].split('/')
            output_dir, paper_id = '/'.join(paper_data[:-1]), paper_data[-1]
            try:
                paper = Paper.from_json(output_dir=output_dir, paper_id=paper_id.replace('.json', ''))
            except:
                paper = NewPaper.from_json(output_dir=output_dir, paper_id=paper_id.replace('.json', ''))
            return PaperSnippet(
                idx=data["idx"] if "idx" in data else 0,
                text=data["text"],
                source_paper=paper
            )
        else:
            return PaperSnippet(
                idx=data["idx"] if "idx" in data else 0,
                text=data["text"],
                source_paper=source_paper
            )
        
    def __repr__(self):
        return f"Snippet: {self.text}\nPaper: {self.source_paper.file_path}"

@dataclass
class Paper:
    paper_id: str
    file_path: str
    title: str
    venue: PaperVenue
    field: PaperField
    content: List[PaperSnippet]

    @staticmethod
    def default():
        return Paper(paper_id='', file_path='', title='', venue=None, field=None, content=[])

    def load_paper_markdown(self, markdown_source: str):
        f = open(markdown_source, 'r')
        file_lines = f.readlines()
        start_idx, end_idx = 0, -1
        lines = []
        for line_idx, line in enumerate(file_lines):
            if start_idx == 0 and 'abstract' in line.lower() and len(line.strip().split()) <= 2:
                start_idx = line_idx
            elif 'references' in line.lower() and len(line.strip().split()) <= 2:
                end_idx = line_idx
                break
            lines.append(line.strip())

        self.content = [PaperSnippet(text=line, source_paper=self, idx=0) for line in lines[start_idx:end_idx] if line.strip() != '']
        for idx, snippet in enumerate(self.content):
            snippet.idx = idx
        assert self.content, f"ERROR: No text found for paper {self.paper_id} | {self.title}"

    def to_json(self, output_dir: str):
        os.makedirs(output_dir, exist_ok=True)
        self.paper_file_path = os.path.join(output_dir, f"{self.paper_id}.json")
        for snippet in self.content:
            snippet.source_paper.file_path = self.paper_file_path
        data = {
            "paper_id": self.paper_id,
            "title": self.title,
            "file_path": self.paper_file_path,
            "venue": self.venue.value,
            "field": self.field.value,
            "content": [snippet.to_dict() for snippet in self.content]
        }
        with open(self.paper_file_path, "w+") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def from_json(paper_id: str, output_dir: str):
        # print(paper_id, output_dir)
        paper_file_path = os.path.join(output_dir, f"{paper_id}.json")
        if os.path.exists(paper_file_path):
            with open(paper_file_path, "r") as f:
                data = json.load(f)
            paper = Paper(
                paper_id=data["paper_id"],
                title=data["title"],
                venue=PaperVenue(data["venue"]),
                field=PaperField(data["field"]),
                file_path=paper_file_path,
                content=[]  # will set next
            )
            paper.content = [PaperSnippet.from_dict(snippet_dict, source_paper=paper) for snippet_dict in data["content"]]
            for idx, snippet in enumerate(paper.content):
                snippet.idx = idx
        else:
            print('not found', paper_id, output_dir)
            paper = Paper.default()
        return paper
        
    def __repr__(self):
        paragraph_texts = '\n'.join(f'[{idx}] ' + snippet.text for idx, snippet in enumerate(self.content))
        return f"Paper Title: {self.title}\nPaper Content:\n{paragraph_texts}"
    
    def __getitem__(self, key: int) -> PaperSnippet:
        return self.content[key]

    def __setitem__(self, key: int, value: PaperSnippet) -> None:
        self.content[key] = value

@dataclass
class NewPaper:
    paper_id: str
    file_path: str
    title: str
    full_title: str
    source: str
    year: int
    content: List[PaperSnippet]

    @staticmethod
    def default():
        return NewPaper(paper_id='', file_path='', title='', full_title='', source='', year=0, content=[])

    def load_paper_markdown(self, markdown_source: str):
        f = open(markdown_source, 'r')
        file_lines = f.readlines()
        start_idx, end_idx = 0, -1
        lines = []
        for line_idx, line in enumerate(file_lines):
            if start_idx == 0 and 'abstract' in line.lower() and len(line.strip().split()) <= 2:
                start_idx = line_idx
            elif 'references' in line.lower() and len(line.strip().split()) <= 2:
                end_idx = line_idx
                break
            lines.append(line.strip())

        self.content = [PaperSnippet(text=line, source_paper=self, idx=0) for line in lines[start_idx:end_idx] if line.strip() != '']
        for idx, snippet in enumerate(self.content):
            snippet.idx = idx
        assert self.content, f"ERROR: No text found for paper {self.paper_id} | {self.title}"

    def to_json(self, output_dir: str):
        os.makedirs(output_dir, exist_ok=True)
        self.paper_file_path = os.path.join(output_dir, f"{self.paper_id}.json")
        for snippet in self.content:
            snippet.source_paper.file_path = self.paper_file_path
        data = {
            "paper_id": self.paper_id,
            "title": self.title,
            "full_title": self.full_title,
            "file_path": self.paper_file_path,
            "source": self.source,
            "year": self.year,
            "content": [snippet.to_dict() for snippet in self.content]
        }
        with open(self.paper_file_path, "w+") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def from_json(paper_id: str, output_dir: str):
        # print(paper_id, output_dir)
        paper_file_path = os.path.join(output_dir, f"{paper_id}.json")
        if os.path.exists(paper_file_path):
            with open(paper_file_path, "r") as f:
                data = json.load(f)
            paper = NewPaper(
                paper_id=data["paper_id"],
                title=data["title"],
                full_title=data["full_title"],
                file_path=paper_file_path,
                year=data['year'],
                source=data['source'],
                content=[]  # will set next
            )
            paper.content = [PaperSnippet.from_dict(snippet_dict, source_paper=paper) for snippet_dict in data["content"]]
            for idx, snippet in enumerate(paper.content):
                snippet.idx = idx
        else:
            paper = NewPaper.default()
        return paper
        
    def __repr__(self):
        paragraph_texts = '\n'.join(f'[{idx}] ' + snippet.text for idx, snippet in enumerate(self.content))
        return f"Paper Title: {self.title}\nPaper Content:\n{paragraph_texts}"
    
    def __getitem__(self, key: int) -> PaperSnippet:
        return self.content[key]

    def __setitem__(self, key: int, value: PaperSnippet) -> None:
        self.content[key] = value