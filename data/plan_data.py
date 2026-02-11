from dataclasses import dataclass, field
from typing import List, Dict
from data.profile_data import HighLevelInference
from enums import ConstitutionCategory, PersonalizationStrategy, PersonalizationFramework, PersonalizationExperimentGroup, PERSONALIZATION_STRATEGY_RUBRIC, PERSONALIZATION_FRAMEWORK_RUBRIC
import os
import json
import random
import hashlib

# from model.response.scholarqa.models import PlanStepResult, PlanResult

@dataclass
class PlanRequirement:
    text: str
    long_text: str
    source_inference: HighLevelInference | None
    source_category: ConstitutionCategory | None
    strategy_label: PersonalizationStrategy | PersonalizationFramework

    def to_dict(self):
        return {
            "text": self.text,
            "long_text": self.long_text,
            "strategy_label": self.strategy_label.value,
            "source_inference": {} if not self.source_inference else self.source_inference.to_dict(),
            "source_category": '' if not self.source_inference else self.source_category.value,
        }

    @staticmethod
    def from_dict(data) -> "PlanRequirement":
        return PlanRequirement(text=data['text'],
                               long_text=data['long_text'],
                               strategy_label=(PersonalizationStrategy(data['strategy_label']) if data['strategy_label'] in {k.value for k in PERSONALIZATION_STRATEGY_RUBRIC} else PersonalizationFramework(data['strategy_label'])),
                               source_inference=None if not data['source_inference'] else HighLevelInference.from_dict(data['source_inference']),
                               source_category=None if not data['source_category'] else ConstitutionCategory(data['source_category']))

    def __str__(self):
        return self.text

@dataclass
class Plan:
    requirements: Dict[PersonalizationStrategy | PersonalizationFramework, List[PlanRequirement]] = field(default_factory=dict)

    def set_seed(self, unique_id):
        seed = int(hashlib.sha256(str(unique_id).encode()).hexdigest(), 16) % (2**32)
        self.rng = random.Random(seed)

    def to_dict(self):
        return {
            "requirements": {
                key.value: [req.to_dict() for req in val] for key, val in self.requirements.items()
            }
        }

    def to_json(self, output_dir: str, query_id: str, user_id: str, make_pretty: bool = False):
        os.makedirs(os.path.join(output_dir, query_id), exist_ok=True)
        data = self.to_dict()
        with open(os.path.join(output_dir, query_id, f"{user_id}.json"), "w+") as f:
            if make_pretty:
                json.dump(data, f, indent=2)
            else:
                json.dump(data, f, separators=(",", ":"))

    @staticmethod
    def from_json(output_dir: str, query_id: str, user_id: str) -> "Plan":
        path = os.path.join(output_dir, query_id, f"{user_id}.json")
        with open(path, "r") as f:
            data = json.load(f)
        return Plan.from_dict(data)

    @staticmethod
    def from_dict(data):
        return Plan(
            requirements={PersonalizationStrategy(k) if k in [k_.value for k_ in PersonalizationStrategy] else PersonalizationFramework(k): [PlanRequirement.from_dict(req) for req in v] for k, v in data['requirements'].items()}
        )

    # def to_plan_result(self, experiment_group: PersonalizationExperimentGroup, cost: float) -> PlanResult:

    #     enum_map = {
    #         'content': 'content',
    #         'specificity': 'specificity',
    #         'explanation_style': 'style',
    #         'usefulness': 'research ideas',
    #         'search_add': 'paper search',
    #         "search_refine": 'query revision',
    #         'organization': 'outline',
    #         'generation': 'generation',
    #         'knowledge': 'knowledge',
    #         'research_style': 'research-style',
    #         'writing_style': 'writing-style',
    #         'positions': 'positions',
    #         'audience': 'audience',
    #         'miscellaneous': 'miscellaneous',
    #     }

    #     steps = []
    #     for key, val in self.requirements.items():
    #         for req_idx, req in enumerate(val):
    #             if key in PERSONALIZATION_STRATEGY_RUBRIC:
    #                 step = PlanStepResult(text=req.text, personalization_strategy=experiment_group, qualitative_strategy=enum_map[key.value], implementation_strategy=enum_map[req.strategy_label.value], inference_category=enum_map[req.source_category.value] if req.source_category is not None else '', long_text=req.long_text, inference_number=0)
    #             else:
    #                 step = PlanStepResult(text=req.text, personalization_strategy=experiment_group, qualitative_strategy=enum_map[req.strategy_label.value], implementation_strategy=enum_map[key.value], inference_category=enum_map[req.source_category.value] if req.source_category is not None else '', long_text=req.long_text, inference_number=0)
    #             steps.append(step)

    #     return PlanResult(plan=steps, model_name='', cost=cost)

    def __getitem__(self, key: PersonalizationStrategy | PersonalizationFramework) -> List[PlanRequirement]:
        return self.requirements.get(key, [])

    def __setitem__(self, key: PersonalizationStrategy | PersonalizationFramework, value: List[PlanRequirement]) -> None:
        self.requirements[key] = value

    @staticmethod
    def default() -> "Plan":
        return Plan(
            requirements=dict()
        )
    
    def for_llm(self) -> str:
        lines = [f'Plan:']
        for key, val in self.requirements.items():
            defn = PERSONALIZATION_STRATEGY_RUBRIC[key].strip().split('\n')[0] if key in PERSONALIZATION_STRATEGY_RUBRIC else PERSONALIZATION_FRAMEWORK_RUBRIC[key].strip().split('\n')[0]
            defn = defn[defn.index('**Definition:**') + len('**Definition:**'):defn.index('.')].replace('*', '').strip()
            lines.append(f"\n===== {key.name.title()}: {defn} =====\n")
            for req_idx, req in enumerate(val):
                req_text = req.text
                if 'the response' in req_text:
                    req_text = req_text[req_text.index('the response'):].strip()
                lines.append(f"[{req_idx}] {req_text}")
        return "\n".join(lines)
    
    def to_markdown(self, query: str) -> str:
        lines = [f'Query: {query}']
        lines.append('')
        for key, val in self.requirements.items():
            defn = PERSONALIZATION_STRATEGY_RUBRIC[key].strip().split('\n')[0] if key in PERSONALIZATION_STRATEGY_RUBRIC else PERSONALIZATION_FRAMEWORK_RUBRIC[key].strip().split('\n')[0]
            defn = defn[defn.index('**Definition:**') + len('**Definition:**'):defn.index('.')].replace('*', '').strip()
            lines.append(f"**{key.name.title()}: {defn}**")
            for req_idx, req in enumerate(val):
                req_text = req.text
                lines.append(f"- {req_text}")
            lines.append('')
        return "\n".join(lines)

    def __str__(self) -> str:
        lines = []
        for key, val in self.requirements.items():
            lines.append(f"**{key.name.title()}**")
            for req_idx, req in enumerate(val):
                req_text = req.text
                lines.append(f"- {req_text} [{req.source_category.value if req.source_category is not None else None, req.strategy_label.value}]")
            lines.append('')
        return "\n".join(lines)
    
    def sample_requirements(self) -> "Plan":
        new_reqs = dict()
        for k, vals in self.requirements.items():
            req = self.rng.choice(vals)
            new_reqs[k] = [req]
        return Plan(requirements=new_reqs)

    def flatten_requirements(self) -> list[str]:
        reqs = []
        for _, val in self.requirements.items():
            for req in val:
                reqs.append(req.text)
        return reqs
    
    def flatten_requirements_into_objects(self, tag: str) -> list[str]:
        reqs = []
        for k, val in self.requirements.items():
            for req in val:
                reqs.append({'short_text': req.text, 'long_text': req.long_text, 'plan_type': tag, 'qualitative_strategy': req.strategy_label.value, 'implementation_strategy': k.value})
        return reqs

    def shuffle(self) -> "Plan":
        new_reqs = dict()
        for k, vals in self.requirements.items():
            self.rng.shuffle(vals)
            new_reqs[k] = vals
        return Plan(requirements=new_reqs)
    
    def get_impl_requirements(self) -> dict[PersonalizationFramework, list[str]]:
        d = {k: [item.long_text for item in v] for k, v in self.requirements.items()}
        return d


    
@dataclass
class QueryPlans:
    query_to_plan: Dict[str, Plan]

    def to_json(self, output_dir: str, user_id: str, make_pretty: bool = False):
        os.makedirs(output_dir, exist_ok=True)
        data = {
            query: plan.to_dict() for query, plan in self.query_to_plan.items()
        }
        with open(os.path.join(output_dir, f"{user_id}.json"), "w+") as f:
            if make_pretty:
                json.dump(data, f, indent=2)
            else:
                json.dump(data, f, separators=(",", ":"))

    @staticmethod
    def from_json(output_dir: str, user_id: str) -> "QueryPlans":
        combined_path = os.path.join(output_dir, f"{user_id}.json")
        if not os.path.exists(combined_path):
            return QueryPlans.default()
        with open(os.path.join(output_dir, f"{user_id}.json"), "r") as f:
            data = json.load(f)
        return QueryPlans(query_to_plan={query: Plan.from_dict(plan) for query, plan in data.items()})
    
    @staticmethod
    def default() -> "QueryPlans":
        return QueryPlans(query_to_plan=dict())

    def __getitem__(self, key: str) -> Plan:
        return self.query_to_plan.get(key, Plan.default())

    def __setitem__(self, key: str, value: Plan) -> None:
        self.query_to_plan[key] = value