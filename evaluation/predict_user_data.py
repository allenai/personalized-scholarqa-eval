from data.dataset_loader import DatasetLoader
import tqdm
from enums import ModelType
from llms.model_factory import ModelFactory
import json
import os

from dotenv import load_dotenv
from model.util import enum_type

from evaluation.rubrics import EXAMPLE_MAP, JSON_PROMPT, METRIC_MAP, PROMPT_BASIC, DESCRIPTION_MAP, PROMPT_METRIC

load_dotenv(dotenv_path=".env")

def setup():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model_name",
        type=str,
        help="Name of the model on the official API",
        required=True
    )
    parser.add_argument(
        "--model_type",
        type=enum_type(ModelType),
        help="Enum for the model type/API provider",
        required=True
    )
    parser.add_argument(
        "--num_examples",
        type=int,
        help="Number of few-shot examples to predict in multiples of three (only 0, 1, 2 for 0, 3, 6 examples)",
        required=True
    )
    parser.add_argument(
        "--prompt_dir",
        type=str,
        help="Directory with the prompts for predicting user satisfaction",
        required=True
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        help="The output directory to save the run",
        required=True
    )
    parser.add_argument(
        "--input_dir",
        type=str,
        help="Directory with the input dataset of user data",
        required=True
    )
    return parser.parse_args()

def collect_example_prompt(num_examples: int, split: str, metric: str, prompt_dir):
    if num_examples == 0:
        return ''
    prompt_template = EXAMPLE_MAP[split]
    example_str = ''
    for example_idx in range(num_examples):
        f = open(f'{prompt_dir}/{split}/{metric}_{example_idx+1}.txt', 'r')
        example_str += f.read() + '\n'
    return prompt_template.format(examples=example_str, n=num_examples)
    
    
def main():

    args = setup()

    ds_loader = DatasetLoader.from_subsets(
        ds_name=args.input_dir,
        subsets=['profile', 'plan', 'response', 'all_text']
    )
    simulation_ds = ds_loader.load_simulation_data()

    factory = ModelFactory()
    llm = factory.get_model(model_type=args.model_type, model_name=args.model_name, temp=0.0)

    basic_prompts = []
    metric_prompts = []
    labels = []
    splits = []
    metrics = []

    for split in simulation_ds.keys():
        curr_ds = simulation_ds[split]

        for source_texts, generation, metric, query, label, metadata in zip(
            curr_ds["source_texts"],
            curr_ds["generation"],
            curr_ds["metric"],
            curr_ds["query"],
            curr_ds["label"],
            curr_ds["metadata"]
        ):

            if len(source_texts) > 1:
                source_text_raw = "\n".join(
                    [
                        """<paper {idx}>
{source_text}
</paper {idx}>
""".format(
                            source_text=source_text, idx=idx + 1
                        )
                        for idx, source_text in enumerate(source_texts)
                    ]
                )
            else:
                source_text_raw = source_texts[0]

            example_str = collect_example_prompt(num_examples=args.num_examples, split=split, metric=metric, prompt_dir=args.prompt_dir)
            prompt_basic = PROMPT_BASIC.format(
                task_description=DESCRIPTION_MAP[split]
                .format(generation=generation, source_text=source_text_raw, query=query, category=metadata['category'])
                .strip(),
                format_description=JSON_PROMPT.strip(),
                example_str=example_str,
                query=query,
            ).strip()

            prompt_metric = PROMPT_METRIC.format(
                task_description=DESCRIPTION_MAP[split]
                .format(generation=generation, source_text=source_text_raw, query=query, category=metadata['category'])
                .strip(),
                format_description=JSON_PROMPT.strip(),
                example_str=example_str,
                metric_description=METRIC_MAP[f"{split}_{metric}"].strip(),
            ).strip()

            basic_prompts.append(prompt_basic)
            metric_prompts.append(prompt_metric)
            labels.append(label)
            splits.append(split)
            metrics.append(metric)

    assert (
        len(basic_prompts) == len(metric_prompts)
        and len(metric_prompts) == len(labels)
        and len(labels) == len(splits)
    )

    fout = f'{args.output_dir}/{args.model_name}.jsonl'
    os.makedirs(os.path.dirname(fout), exist_ok=True)

    with open(fout, "w") as f:
        for prompt_basic, prompt_metric, label, split, curr_metric in tqdm.tqdm(
            list(zip(basic_prompts, metric_prompts, labels, splits, metrics))
        ):

            response_basic = llm.generate_json(
                prompt=prompt_basic,
                target_json={"is_satisfied": True, "explanation": ""},
                backup_json={"is_satisfied": True, "explanation": ""},
            )
            response_metric = llm.generate_json(
                prompt=prompt_metric,
                target_json={"is_satisfied": True, "explanation": ""},
                backup_json={"is_satisfied": True, "explanation": ""},
            )

            curr_out = {
                "split": split,
                "metric": curr_metric,
                "true": label,
                "pred_basic": None if not response_basic else response_basic["is_satisfied"],
                "explanation_basic": '' if not response_basic else response_basic["explanation"],
                "pred_metric": None if not response_metric else response_metric["is_satisfied"],
                "explanation_metric": '' if not response_metric else response_metric["explanation"],
            }

            f.write(json.dumps(curr_out) + "\n")
            f.flush()


if __name__ == "__main__":
    main()
