import random
from data.dataset_loader import DatasetLoader
from data.plan_data import Plan
from data.profile_data import UserConstitution
from evaluation.metrics import PlanEvalRun
import datasets
import numpy as np

DATASET_DIR = 'data/local_datasets/simulated_profile_inputs'
MODELS_TO_EVALUATE = ['gpt-4.1-2025-04-14']
EVAL_DIR = 'evaluation/eval_runs/plans/' # where the eval run is saved

ds = datasets.load_from_disk(DATASET_DIR)
query_map = dict(zip(ds['dev']['query_id'], ds['dev']['query'])) | dict(zip(ds['test']['query_id'], ds['test']['query']))

ds = DatasetLoader(DATASET_DIR)
author_map = ds.load_author_map()


for model in MODELS_TO_EVALUATE:

    eval_run_personalized = PlanEvalRun.from_json(output_dir=EVAL_DIR, run_name=f'{model}_personalized')
    eval_run_query = PlanEvalRun.from_json(output_dir=EVAL_DIR, run_name=f'{model}_query')
    eval_run_category = PlanEvalRun.from_json(output_dir=EVAL_DIR, run_name=f'{model}_category')

    print(f'\n\nEvaluating Model: {model}\n--------------------------------------')
    pers_labels = []
    for (query_id, user_id), metrics in eval_run_personalized.metrics.items():
        for strat, data in metrics.metrics.items():
            pers_labels.append(data[0])

    print('Personalization Win Rate (Self-Consistency):', 1.0 * sum([x == 'A' for x in pers_labels]) / len(pers_labels))

    conflicts = {'normal': [], 'personalized': []}
    author_conflict_type = {'low': [], 'medium': [], 'high': []}
    for (query_id, user_id), metrics in eval_run_query.metrics.items():
        for strat, data in metrics.metrics.items():
            
            for x in data[0][0]:
                conflicts['personalized'].append(x[0])
                author_conflict_type[author_map[user_id]].append(x[0])
            for x in data[0][1]:
                conflicts['normal'].append(x[0])

    print()
    print("Overall Coherence -- Normal:", 1.0 - np.mean(conflicts['normal']))
    print("Overall Coherence -- Personalized:", 1.0 - np.mean(conflicts['personalized']))
    for k, v in author_conflict_type.items():
        print(f"    * {k.title()}-Similarity Author Coherence", 1.0 - np.mean(v))

    category_accuracy = {'normal': [], 'personalized': []}
    for (query_id, user_id), metrics in eval_run_category.metrics.items():
        for strat, data in metrics.metrics.items():
            category_accuracy['normal'].extend(data[0][0])
            category_accuracy['personalized'].extend(data[0][1])

    print()
    print("Overall Category Accuracy -- Normal:", np.mean(category_accuracy['normal']))
    print("Overall Category Accuracy -- Personalized:", np.mean(category_accuracy['personalized']))
    print('--------------------------------------')