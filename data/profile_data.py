from dataclasses import dataclass, field
from typing import List, Dict
from data.paper_data import PaperSnippet
from enums import ConstitutionCategory, CONSTITUTION_DEFINITION_RUBRIC
import json
import os

@dataclass
class AtomicInference:
    text: str
    sources: List[PaperSnippet]

    def to_dict(self):
        return {
            "text": self.text,
            "sources": [source.to_dict() for source in self.sources]
        }

    @staticmethod
    def from_dict(data):
        return AtomicInference(
            text=data["text"],
            sources=[PaperSnippet.from_dict(source, source_paper=None) for source in data["sources"]]
        )

@dataclass
class HighLevelInference:
    text: str
    sources: List[AtomicInference]

    def to_dict(self):
        return {
            "text": self.text,
            "sources": [s.to_dict() for s in self.sources]
        }

    @staticmethod
    def from_dict(data):
        return HighLevelInference(
            text=data["text"],
            sources=[AtomicInference.from_dict(s) for s in data["sources"]]
        )

@dataclass
class UserConstitution:
    inferences: Dict[ConstitutionCategory, List[HighLevelInference]] = field(default_factory=dict)

    def to_json(self, output_dir: str, user_id: str, make_pretty: bool = False):
        os.makedirs(output_dir, exist_ok=True)
        data = {
            category.value: [inf.to_dict() for inf in inf_list]
            for category, inf_list in self.inferences.items()
        }
        with open(os.path.join(output_dir, f"{user_id}.json"), "w+") as f:
            if make_pretty:
                json.dump(data, f, indent=2)
            else:
                json.dump(data, f, separators=(",", ":"))

    @staticmethod
    def from_json(output_dir: str, user_id: str) -> "UserConstitution":
        with open(os.path.join(output_dir, f"{user_id}.json"), "r") as f:
            data = json.load(f)
        return UserConstitution({
            ConstitutionCategory(key): [HighLevelInference.from_dict(inf) for inf in inf_list]
            for key, inf_list in data.items()
        })
    
    def to_txt(self, output_dir: str, user_id: str):
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, f"{user_id}.txt"), "w+") as f:
            f.write(self.to_markdown())

    def __getitem__(self, key: ConstitutionCategory) -> List[HighLevelInference]:
        return self.inferences.get(key, [])

    def __setitem__(self, key: ConstitutionCategory, value: List[HighLevelInference]) -> None:
        self.inferences[key] = value

    def for_llm_merge(self) -> str:
        lines = []
        for category, high_level_infs in self.inferences.items():
            lines.append(f"\n===== {category.name.title()} =====\n")
            for hli_idx, hli in enumerate(high_level_infs, 1):
                lines.append(f"{hli_idx}. {hli.text}")
                for _, ali in enumerate(hli.sources, 1):
                    lines.append(f"    - {ali.text}")
                    citations = []
                    for src in ali.sources:
                        citations.append(str(src.idx))
                    lines[-1] = lines[-1] + f' [{",".join(citations)}, {src.source_paper.title}]'
                #lines.append('')
        return "\n".join(lines)

    def for_llm(self) -> str:
        lines = []
        idx = 0
        for _, high_level_infs in self.inferences.items():
            #defn = CONSTITUTION_DEFINITION_RUBRIC[category].strip().split('\n')[0]
            #defn = defn[defn.index('**Definition:**') + len('**Definition:**'):defn.index('include:')].replace('*', '').strip()
            #lines.append(f"\n===== {category.name.title()}: {defn} =====\n")
            for _, hli in enumerate(high_level_infs, 1):
                lines.append(f"[{idx}] {hli.text}")
                idx += 1
                # for _, ali in enumerate(hli.sources, 1):
                #     lines.append(f"    - {ali.text}")
        return "\n".join(lines)
    
    def flattened_inferences(self) -> list[HighLevelInference]:
        infs = []
        for _, high_level_infs in self.inferences.items():
            infs.extend(high_level_infs)
        return infs
    
    def lookup_category(self, inf: HighLevelInference):
        for cat, high_level_infs in self.inferences.items():
            if inf in high_level_infs:
                return cat
        return None

    def __str__(self) -> str:
        lines = []
        for category, high_level_infs in self.inferences.items():
            defn = CONSTITUTION_DEFINITION_RUBRIC[category].strip().split('\n')[0]
            defn = defn[defn.index('**Definition:**') + len('**Definition:**'):defn.index('.')].replace('*', '').strip()
            lines.append(f"\n===== {category.name.title()}: {defn} =====\n")
            for hli_idx, hli in enumerate(high_level_infs, 1):
                lines.append(f"{hli_idx}. {hli.text}")
                for _, ali in enumerate(hli.sources, 1):
                    lines.append(f"    - {ali.text}")
                    for src in ali.sources:
                        preview_words = src.text.strip().split()
                        if src.source_paper:
                            preview = ' '.join(preview_words[:10]) + ("..." if len(preview_words) > 10 else "")
                            lines.append(f"        ↳ \"{preview}\" [{src.source_paper.title}]")
                        else:
                            lines.append(f"        ↳ No citation found)")
                lines.append('')
        return "\n".join(lines)
    
    def to_markdown(self) -> str:
        lines = []
        for category, high_level_infs in self.inferences.items():
            defn = CONSTITUTION_DEFINITION_RUBRIC[category].strip().split('\n')[0]
            defn = defn[defn.index('**Definition:**') + len('**Definition:**'):defn.index('.')].replace('*', '').strip()
            lines.append(f"\n\n**{category.name.title()}: {defn}**\n")

            for hli_idx, hli in enumerate(high_level_infs, 1):
                lines.append(f"{hli_idx}: {hli.text}")
                for ali in hli.sources:
                    lines.append(f"- {ali.text}")
                    for src in ali.sources:
                        preview_words = src.text.strip().split()
                        preview = ' '.join(preview_words[:10]) + ("..." if len(preview_words) > 10 else "")
                        if src.source_paper:
                            lines.append(f"    - \"{preview}\" [{src.source_paper.title}]")
                        else:
                            lines.append(f"    - No citation found")
                lines.append("")  # space between entries

        return "\n".join(lines)
    
# ==================================== Alternative User Profile Approaches ====================================

@dataclass
class Keyword:
    text: str
    sources: List[PaperSnippet]

    def to_dict(self):
        return {
            "text": self.text,
            "sources": [source.to_dict() for source in self.sources]
        }

    @staticmethod
    def from_dict(data):
        return Keyword(
            text=data["text"],
            sources=[PaperSnippet.from_dict(source, source_paper=None) for source in data["sources"]]
        )

@dataclass
class KeywordProfile:
    keywords: List[Keyword]

    def to_json(self, output_dir: str, user_id: str):
        os.makedirs(output_dir, exist_ok=True)
        data = {'keywords': k.to_dict() for k in self.keywords}
        with open(os.path.join(output_dir, f"{user_id}.json"), "w+") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def from_json(output_dir: str, user_id: str) -> "KeywordProfile":
        with open(os.path.join(output_dir, f"{user_id}.json"), "r") as f:
            data = json.load(f)
        return KeywordProfile(keywords=[Keyword.from_dict(k) for k in data['keywords']])

    def __str__(self):
        lines = []
        for idx, k in enumerate(self.keywords):
            lines.append(f'{idx+1}. {k.text}')
            for src in k.sources:
                preview_words = src.text.strip().split()
                if src.source_paper:
                    preview = ' '.join(preview_words[:10]) + ("..." if len(preview_words) > 10 else "")
                    lines.append(f"        ↳ \"{preview}\" [{src.source_paper.title}]")
                else:
                    lines.append(f"        ↳ No citation found)")
        return '\n'.join(lines)

    def to_txt(self, output_dir: str, user_id: str):
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, f"{user_id}.txt"), "w+") as f:
            f.write(str(self))

@dataclass
class BiographySentence:
    text: str
    sources: List[PaperSnippet]

    def to_dict(self):
        return {
            "text": self.text,
            "sources": [source.to_dict() for source in self.sources]
        }

    @staticmethod
    def from_dict(data):
        return Keyword(
            text=data["text"],
            sources=[PaperSnippet.from_dict(source, source_paper=None) for source in data["sources"]]
        )

@dataclass
class Biography:
    sentences: List[BiographySentence]

    def to_json(self, output_dir: str, user_id: str):
        os.makedirs(output_dir, exist_ok=True)
        data = {'sentences': s.to_dict() for s in self.sentences}
        with open(os.path.join(output_dir, f"{user_id}.json"), "w+") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def from_json(output_dir: str, user_id: str) -> "Biography":
        with open(os.path.join(output_dir, f"{user_id}.json"), "r") as f:
            data = json.load(f)
        return Biography(sentences=[BiographySentence.from_dict(k) for k in data['sentences']])

    def __str__(self):
        lines = []
        for idx, sent in enumerate(self.sentences):
            lines.append(f'{idx+1}. {sent.text}')
            for src in sent.sources:
                preview_words = src.text.strip().split()
                if src.source_paper:
                    preview = ' '.join(preview_words[:10]) + ("..." if len(preview_words) > 10 else "")
                    lines.append(f"        ↳ \"{preview}\" [{src.source_paper.title}]")
                else:
                    lines.append(f"        ↳ No citation found)")
        return '\n'.join(lines)

    def to_txt(self, output_dir: str, user_id: str):
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, f"{user_id}.txt"), "w+") as f:
            f.write(str(self))

@dataclass
class SnippetProfile:
    query: str
    snippets: List[PaperSnippet]

    def to_json(self, output_dir: str, user_id: str):
        os.makedirs(output_dir, exist_ok=True)
        data = {'query': self.query, 'snippets': [s.to_dict() for s in self.snippets]}
        with open(os.path.join(output_dir, f"{user_id}.json"), "w+") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def from_json(output_dir: str, user_id: str) -> "SnippetProfile":
        with open(os.path.join(output_dir, f"{user_id}.json"), "r") as f:
            data = json.load(f)
        return SnippetProfile(sentences=[PaperSnippet.from_dict(k) for k in data['snippets']])

    def __str__(self):
        lines = [f'Query: {self.query}']
        for idx, snippet in enumerate(self.snippets):
            lines.append(f'{idx+1}. {snippet.text} [{snippet.source_paper.title}]\n')
        return '\n'.join(lines)

    def to_txt(self, output_dir: str, user_id: str):
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, f"{user_id}.txt"), "w+") as f:
            f.write(str(self))

    