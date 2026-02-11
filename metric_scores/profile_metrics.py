from evaluation.metrics import ConstitutionEvalRun
from data import UserConstitution
import pandas as pd

MODELS_TO_EVALUATE = ['gpt-4.1-2025-04-14'] # the models you want to evaluate (saved in the form {name}.jsonl)
PROFILE_DIR = 'outputs/user_profile/profiles/' # directory of profiles
EVAL_DIR = 'evaluation/eval_runs/profiles/gpt-4.1-2025-04-14' # where the eval run is saved

def build_comparison_table(runs: list, names: list[str], metrics: list[str]):
    all_metrics = sorted(set(metrics))
    methods = ['hli', 'ali']

    # Create MultiIndex: (Method, Run)
    columns = pd.MultiIndex.from_product([methods, names], names=['Method', 'Run'])

    data = []
    for metric in all_metrics:
        row = []
        for method in methods:
            for run in runs:
                d = run.summarize_metrics()
                mean = d.get(method, {}).get(metric, {}).get('mean', None)
                row.append(mean)
        data.append(row)

    row = []
    for idx, (name, run) in enumerate(list(zip(names, runs))):
        out_dir = f'{PROFILE_DIR}/{name}'
        curr_row = []
        for k, metric in run.metrics.items():
            c = UserConstitution.from_json(out_dir, k)
            for _, hlis in c.inferences.items():
                for hli in hlis:
                    curr_row.append(len(hli.text.split()))
        row.append(sum(curr_row) / (1.0 * len(curr_row)))
    data.append(row)

    df = pd.DataFrame(data, index=all_metrics + ['length'], columns=columns)
    return df

metric_runs = []
run_names = []
for model_name in MODELS_TO_EVALUATE:
    metric_runs.append(ConstitutionEvalRun.from_json(output_dir=EVAL_DIR, run_name=model_name))
    run_names.append(model_name)


print(build_comparison_table(metric_runs, run_names, ['source_accuracy', 'category_accuracy', 'cite_relevance', 'num_cites', 'specificity']))