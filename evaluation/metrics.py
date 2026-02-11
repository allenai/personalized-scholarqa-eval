from dataclasses import dataclass, field, asdict
from typing import List, Dict, Tuple
from enums import ConstitutionCategory, PersonalizationFramework, PersonalizationStrategy
from data import UserConstitution, HighLevelInference
import os
import json
from collections import defaultdict, Counter
import numpy as np

@dataclass
class InferenceMetric:

    source_accuracy: bool | None # is the inference supported by the source
    category_accuracy: bool | None # is the inference under the right category

    specificity: int | None # specificity from 1-5

    max_sim_all: float | None # diversity w.r.t. all inferences
    max_sim_idx_all: int | None
    max_sim_text_all: str | None
    avg_sim_all: float | None

    max_sim_cat: float | None # diversity w.r.t. inferences in the same category
    max_sim_idx_cat: int | None
    max_sim_text_cat: str | None
    avg_sim_cat: float | None

    max_sim_across: float | None # diversity w.r.t. inferences across all constitutions
    max_sim_idx_across: int | None
    max_sim_text_across: str | None
    avg_sim_across: float | None

    num_relevant_cites: int | None # total number of relevant cites (check if model makes up reasoning)
    num_unique_cites: int | None # number of unique papers (in case of duplicates)
    num_cites: int | None # total number of papers the inference uses
    cite_relevance: list[int] |  None # indicator of which citations are relevant

    @staticmethod
    def default():
        return InferenceMetric(source_accuracy=None, category_accuracy=None, specificity=None, max_sim_all=None, max_sim_across=None, max_sim_cat=None, max_sim_idx_all=None, max_sim_idx_cat=None, max_sim_idx_across=None, avg_sim_all=None, avg_sim_cat=None, avg_sim_across=None, num_relevant_cites=None, num_cites=None, num_unique_cites=None, cite_relevance=None, max_sim_text_all=None, max_sim_text_cat=None, max_sim_text_across=None)
    
    def is_valid(self) -> bool:
        return (self.avg_sim_across != None and self.max_sim_text_across != None and self.max_sim_across != None and self.max_sim_idx_across != None and self.max_sim_text_all != None and self.max_sim_all != None and self.max_sim_idx_all != None and self.avg_sim_all != None and self.max_sim_text_cat != None and self.max_sim_cat != None and self.max_sim_idx_cat != None and self.avg_sim_cat != None) and (int(self.source_accuracy != None) + int(self.category_accuracy != None) + int(self.specificity != None) >= 2)

    def to_dict(self):
        return asdict(self)
    
    @staticmethod
    def from_dict(data: dict):
        return InferenceMetric(**data)
    
    def __str__(self):
        return f"src_acc={self.source_accuracy}, cat_acc={self.category_accuracy}, spec={self.specificity}, sim_within={self.max_sim_text_all} [{self.max_sim_all}], sim_across={self.max_sim_text_across} [{self.max_sim_across}]" + (f', cites=({self.num_cites}, {self.num_unique_cites}, {self.cite_relevance})' if self.num_cites else '')

    
@dataclass
class AtomicInferenceMetrics:
    metric: InferenceMetric

    @staticmethod
    def default():
        return AtomicInferenceMetrics(metric=InferenceMetric.default())
    
    def to_dict(self):
        return {
            'metric': self.metric.to_dict(),
        }
    
    @staticmethod
    def from_dict(data: dict):
        return AtomicInferenceMetrics(metric=InferenceMetric.from_dict(data['metric']))

@dataclass
class HighLevelInferenceMetric:
    atomic_metrics: List[AtomicInferenceMetrics]
    metric: InferenceMetric

    @staticmethod
    def from_hli(hli: HighLevelInference):
        return HighLevelInferenceMetric(metric=InferenceMetric.default(), atomic_metrics=[AtomicInferenceMetrics.default() for _ in hli.sources])
    
    def to_dict(self):
        return {
            'metric': self.metric.to_dict(),
            'atomic_metrics': [ali_metric.to_dict() for ali_metric in self.atomic_metrics]
        }

    @staticmethod
    def from_dict(data: dict):
        return HighLevelInferenceMetric(metric=InferenceMetric.from_dict(data['metric']),
                                      atomic_metrics=[AtomicInferenceMetrics.from_dict(ali) for ali in data['atomic_metrics']])

@dataclass
class ConstitutionMetrics:
    metrics: Dict[ConstitutionCategory, List[HighLevelInferenceMetric]]
    hli_iterators: Dict[ConstitutionCategory, int] = field(
        default_factory=lambda: {k: 0 for k in ConstitutionCategory}
    )
    ali_iterators: Dict[ConstitutionCategory, tuple] = field(
        default_factory=lambda: {k: (0, 0) for k in ConstitutionCategory}
    )

    @staticmethod
    def from_constitution(constitution: UserConstitution):
        return ConstitutionMetrics(metrics={cat: [HighLevelInferenceMetric.from_hli(hli=hli) for hli in hlis] for cat, hlis in constitution.inferences.items()})
    
    # TODO: Is there a smarter way to do this? (low priority)
    def insert_hli(self, category: ConstitutionCategory, metric: InferenceMetric):
        # insert metric
        hli_itr = self.hli_iterators[category]
        self.metrics[category][hli_itr].metric = metric

        # adjust iterator
        hli_itr += 1
        if hli_itr == len(self.metrics[category]):
            hli_itr = 0
        self.hli_iterators[category] = hli_itr

    def insert_ali(self, category: ConstitutionCategory, metric: InferenceMetric):
        # insert metric
        ali_itr, hli_itr = self.ali_iterators[category]
        self.metrics[category][hli_itr].atomic_metrics[ali_itr].metric = metric

        # adjust iterator
        ali_itr += 1
        if ali_itr == len(self.metrics[category][hli_itr].atomic_metrics):
            ali_itr = 0
            hli_itr += 1
            if hli_itr == len(self.metrics[category]):
                hli_itr = 0
        self.ali_iterators[category] = ali_itr, hli_itr

    def is_valid(self) -> bool:
        for _, metrics in self.metrics.items():
            for hli_metric in metrics:
                if not hli_metric.metric.is_valid():
                    print('invalid hli:', hli_metric)
                    return False
                for ali_metric in hli_metric.atomic_metrics:
                    if not ali_metric.metric.is_valid():
                        print('invalid ali:', ali_metric)
                        return False
        return True
    
    def to_dict(self):
        return {
            category.value: [inf.to_dict() for inf in metrics] for category, metrics in self.metrics.items()
        }
    
    @staticmethod
    def from_dict(data: dict):
        return ConstitutionMetrics(metrics={ConstitutionCategory(key): [HighLevelInferenceMetric.from_dict(v) for v in val] for key, val in data.items()})

@dataclass
class ConstitutionEvalRun:
    metrics: Dict[str, ConstitutionMetrics]

    def to_json(self, output_dir: str, run_name: str):
        output_path = os.path.join(output_dir, f"{run_name}.jsonl")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(os.path.join(output_dir, f"{run_name}.jsonl"), "w+") as f:
            json.dump({key: metric.to_dict() for key, metric in self.metrics.items()}, f, indent=2)

    @staticmethod
    def from_json(output_dir: str, run_name: str) -> "ConstitutionEvalRun":
        path = os.path.join(output_dir, f"{run_name}.jsonl")
        with open(path, "r") as f:
            raw = json.load(f)
        metrics = {key: ConstitutionMetrics.from_dict(val) for key, val in raw.items()}
        return ConstitutionEvalRun(metrics=metrics)

    def summarize_metrics(self) -> Dict[str, Dict[str, Dict[str, float]]]:

        def collect_numeric_metrics(metric: InferenceMetric, collector: Dict[str, List[float]]):
            for field_name, value in metric.__dict__.items():
                if isinstance(value, (int, float)) and value is not None:
                    collector[field_name].append(value)
                if isinstance(value, list) and len(value) > 0 and isinstance(value[0], (int, float)):
                    collector[field_name].extend(value)

        hli_data = defaultdict(list)
        ali_data = defaultdict(list)

        for cm in self.metrics.values():
            for hli_list in cm.metrics.values():
                for hli in hli_list:
                    collect_numeric_metrics(hli.metric, hli_data)
                    for ali in hli.atomic_metrics:
                        collect_numeric_metrics(ali.metric, ali_data)

        def summarize(data: Dict[str, List[float]]) -> Dict[str, Dict[str, float]]:
            return {
                k: {
                    'mean': float(np.mean(v)) if v else None,
                    'count': len(v)
                } for k, v in data.items()
            }

        return {
            'hli': summarize(hli_data),
            'ali': summarize(ali_data)
        }

@dataclass
class PlanMetrics:
    metrics: dict[PersonalizationStrategy | PersonalizationFramework, Tuple[str, str, str]]

    def to_dict(self):
        return {k.value: v for k, v in self.metrics.items()}
    
    @staticmethod
    def from_dict(data: dict):
        return PlanMetrics(metrics={(PersonalizationFramework(k) if k in {n.value for n in PersonalizationFramework} else PersonalizationStrategy(k)): v for k, v in data.items()})

@dataclass
class PlanEvalRun:

    metrics: dict[tuple[str, str], PlanMetrics]

    def to_json(self, output_dir: str, run_name: str):
        output_path = os.path.join(output_dir, f"{run_name}.jsonl")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(os.path.join(output_dir, f"{run_name}.jsonl"), "w+") as f:
            json.dump({str((key[0], key[1])): metric.to_dict() for key, metric in self.metrics.items()}, f, indent=2)

    @staticmethod
    def from_json(output_dir: str, run_name: str) -> "PlanEvalRun":
        path = os.path.join(output_dir, f"{run_name}.jsonl")
        with open(path, "r") as f:
            raw = json.load(f)

        keys = [eval(k) for k in raw.keys()]
        metrics = {(k[0], k[1]): PlanMetrics.from_dict(raw[str(k)]) for k in keys}
        return PlanEvalRun(metrics=metrics)

    def summarize_metrics(self) -> Dict[str, Dict[str, float]]:
        summary = defaultdict(Counter)

        annot_data = {
            'A': [],
            'B': [],
            'winner': []
        }

        # Iterate through all PlanMetrics
        for _, plan_metrics in self.metrics.items():
            for metric_key, result in plan_metrics.metrics.items():
                summary[metric_key.value][result[0]] += 1
                annot_data['A'].append(result[1])
                annot_data['B'].append(result[2])
                annot_data['winner'].append(result[0])

        # Normalize counts to proportions
        proportions = {}
        for metric_key, counter in summary.items():
            total = sum(counter.values())
            proportions[metric_key] = {
                outcome: count / total for outcome, count in counter.items()
            }

            # Ensure all categories are present
            for category in ["A", "B", "Tie"]:
                proportions[metric_key].setdefault(category, 0.0)

        return proportions, annot_data